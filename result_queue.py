# -*- coding: utf-8 -*-
"""
Последовательная очередь обработки результатов с задержкой между
записями в GitHub.

Зачем: тестеры часто пишут результаты пачкой, пока ждут, когда бот
включится. Если обрабатывать их конкурентно/без паузы, велик шанс
поймать sha-конфликт в GitHub API (два запроса читают один и тот же sha,
второй PUT отклоняется). github_storage.update_players_file уже умеет
ретраить при конфликте, но чтобы не полагаться только на ретраи (это
дополнительные секунды на каждый конфликт, плюс лишняя нагрузка на
GitHub API), очередь обрабатывает результаты СТРОГО последовательно,
с паузой 5-10 секунд между записями.

Реализовано как простой FIFO в отдельном потоке - подходит для нашего
объёма (десятки результатов, не тысячи), не требует внешних очередей
вроде Redis/Celery.
"""

import time
import queue
import threading
import random
import traceback


DELAY_MIN_SECONDS = 5
DELAY_MAX_SECONDS = 10


class ResultQueue:
    """
    Очередь задач. Каждая задача - произвольная функция без аргументов
    (замыкание), которая выполняет обработку одного результата
    (парсинг уже сделан снаружи, здесь только "сделать GitHub-запись
    и отправить карточку").

    Между обработкой соседних задач выдерживается случайная пауза
    DELAY_MIN_SECONDS..DELAY_MAX_SECONDS - вариативность нужна, чтобы
    не создавать полностью синхронную нагрузку, если вдруг несколько
    инстансов почему-то шлют запросы одновременно (защитная мера,
    не строго необходимая при одном инстансе бота).
    """

    def __init__(self, on_task_error=None, delay_min=DELAY_MIN_SECONDS, delay_max=DELAY_MAX_SECONDS):
        self._queue = queue.Queue()
        self._on_task_error = on_task_error
        self._delay_min = delay_min
        self._delay_max = delay_max
        self._worker_thread = None
        self._stop_flag = threading.Event()
        # Для тестов/интроспекции: сколько задач обработано и с какими паузами
        self.processed_count = 0
        self.last_delay_used = None

    def start(self):
        if self._worker_thread is not None and self._worker_thread.is_alive():
            return
        self._stop_flag.clear()
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()

    def stop(self):
        self._stop_flag.set()

    def submit(self, task_fn):
        """Добавляет задачу в конец очереди. task_fn - callable без аргументов."""
        self._queue.put(task_fn)

    def qsize(self):
        return self._queue.qsize()

    def _worker_loop(self):
        first_task = True
        while not self._stop_flag.is_set():
            try:
                task_fn = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if not first_task:
                delay = random.uniform(self._delay_min, self._delay_max)
                self.last_delay_used = delay
                time.sleep(delay)
            first_task = False

            try:
                task_fn()
            except Exception as e:
                traceback.print_exc()
                if self._on_task_error:
                    try:
                        self._on_task_error(e)
                    except Exception:
                        traceback.print_exc()
            finally:
                self.processed_count += 1
                self._queue.task_done()
