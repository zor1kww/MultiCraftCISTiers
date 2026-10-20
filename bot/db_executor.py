"""
Мост между потоками. Соединение с БД принадлежит ТОЛЬКО потоку
Discord-бота (драйверу Turso нельзя делиться соединением между
потоками), а Telegram-панель работает в другом потоке. Поэтому панель
не ходит в БД сама: она передаёт сюда функцию fn(conn), поток Discord
раз в секунду забирает очередь (drain) и выполняет функции у себя, а
панель ждёт результат.
"""

import queue
import threading


class _Call:
    __slots__ = ("fn", "done", "result", "error", "cancelled")

    def __init__(self, fn):
        self.fn = fn
        self.done = threading.Event()
        self.result = None
        self.error = None
        self.cancelled = False


_queue: "queue.Queue[_Call]" = queue.Queue()


def run_on_db_thread(fn, timeout: float = 15.0):
    """Выполняет fn(conn) в потоке БД и возвращает результат (исключение
    из fn пробрасывается). TimeoutError - поток БД не ответил вовремя;
    такой вызов помечается отменённым и позже выполнен НЕ будет, чтобы
    действие админа не сработало с опозданием, когда он уже увидел
    ошибку."""
    call = _Call(fn)
    _queue.put(call)
    if not call.done.wait(timeout):
        call.cancelled = True
        raise TimeoutError("поток БД не ответил за отведённое время")
    if call.error is not None:
        raise call.error
    return call.result


def drain(conn, limit: int = 50) -> int:
    """Вызывается из потока Discord: выполняет накопившиеся вызовы."""
    handled = 0
    while handled < limit:
        try:
            call = _queue.get_nowait()
        except queue.Empty:
            break
        handled += 1
        if call.cancelled:
            continue
        try:
            call.result = call.fn(conn)
        except Exception as e:  # возвращаем вызвавшему, а не роняем поток Discord
            call.error = e
        finally:
            call.done.set()
    return handled
