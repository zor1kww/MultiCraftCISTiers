# -*- coding: utf-8 -*-
"""
Машина состояний диалога тир-тестера с ботом.

Разделена от telebot намеренно: этот модуль ничего не знает про Telegram,
только хранит/переключает состояние и валидирует ввод на каждом шаге.
Это позволяет протестировать весь сценарий диалога без сети и без
реального Telegram API - что важно, поскольку в этой среде нет
доступа ни к сети, ни к установленному пакету telebot.

Хранилище состояний - в памяти процесса (обычный dict). При перезапуске
бота (в т.ч. спин-даун Render) все незавершённые диалоги теряются -
это осознанный компромисс: цена восстановления state через GitHub/файл
для диалога из ~10 шагов не оправдана, тестер просто начнёт заново.
"""

from bot_config import VALID_KITS, REGIONS, TIER_ORDER, RETIRED_ELIGIBLE_TIERS, TESTERS


# ==========================================
# Шаги диалога
# ==========================================
STEP_TEST_OR_ADMIN = "test_or_admin"          # "Прошёл тир-тест" / "Изменение без теста"
STEP_PLAYER_NAME = "player_name"
STEP_KIT = "kit"
STEP_REGION = "region"
STEP_TIER_BEFORE = "tier_before"
STEP_TIER_TESTED = "tier_tested"              # только для ветки "тир-тест"
STEP_PASSED = "passed"                        # только для ветки "тир-тест", сдал/не сдал
STEP_TIER_AFTER = "tier_after"                # только для ветки "без теста"
STEP_NO_TEST_REASON = "no_test_reason"        # только для ветки "без теста"
STEP_RETIRED_CHOICE = "retired_choice"        # только если итоговый тир HT3+
STEP_DUELS_COUNT = "duels_count"              # только для ветки "тир-тест"
STEP_DUEL_OPPONENT = "duel_opponent"
STEP_DUEL_SCORE = "duel_score"
STEP_TESTER_SELECT = "tester_select"
STEP_COMMENT = "comment"
STEP_PREVIEW = "preview"
STEP_DONE = "done"


class DialogState:
    """Состояние одного диалога (одного тестера, один результат за раз)."""

    def __init__(self, tester_id: int, tester_username: str = None):
        self.tester_id = tester_id
        self.tester_username = tester_username
        self.step = STEP_TEST_OR_ADMIN

        self.is_test = None          # True = "Прошёл тир-тест", False = "Изменение без теста"
        self.player_name = None
        self.kit = None
        self.region = None
        self.tier_before = None      # тир игрока ДО (для обеих веток)
        self.tier_tested = None      # тир, который тестировался (только ветка теста)
        self.passed = None           # сдал ли tier_tested (только ветка теста)
        self.tier_after = None       # итоговый тир (вычисляется для ветки теста, вводится для "без теста")
        self.no_test_reason = None
        self.retired = False         # ручной Retired (кнопка на шаге ввода ранга)
        self.duels_expected = 0
        self.duels = []              # [{"opponent": str, "score": str}]
        self._current_duel_opponent = None  # временное хранилище между двумя под-шагами одного поединка
        self.other_tester_id = None  # если результат вносится за другого тестера
        self.comment = None

    def reset_for_new_result(self):
        """После отправки одного результата тестер может сразу вносить следующий -
        сбрасываем всё, кроме identity тестера."""
        tester_id, username = self.tester_id, self.tester_username
        self.__init__(tester_id, username)


# In-memory хранилище: user_id -> DialogState
_active_dialogs = {}


def start_dialog(tester_id: int, tester_username: str = None) -> DialogState:
    state = DialogState(tester_id, tester_username)
    _active_dialogs[tester_id] = state
    return state


def get_dialog(tester_id: int):
    return _active_dialogs.get(tester_id)


def end_dialog(tester_id: int):
    _active_dialogs.pop(tester_id, None)


# ==========================================
# Валидация ввода на каждом шаге
# ==========================================

def validate_player_name(text: str):
    """Возвращает (ok: bool, cleaned_value_or_error: str)."""
    name = text.strip()
    if not name:
        return False, "Ник не может быть пустым."
    if len(name) > 32:
        return False, "Слишком длинный ник (максимум 32 символа)."
    return True, name


SCORE_PATTERN_HINT = "Формат счёта: число-число, например 10-6"


def validate_score(text: str):
    import re
    text = text.strip()
    m = re.fullmatch(r"(\d{1,2})\s*-\s*(\d{1,2})", text)
    if not m:
        return False, SCORE_PATTERN_HINT
    return True, f"{m.group(1)}-{m.group(2)}"


def validate_comment(text: str):
    text = text.strip()
    if len(text) > 300:
        return False, "Комментарий слишком длинный (максимум 300 символов)."
    return True, text


def validate_duels_count(text: str):
    text = text.strip()
    if not text.isdigit():
        return False, "Введите число поединков (1-6)."
    n = int(text)
    if n < 1 or n > 6:
        return False, "Число поединков должно быть от 1 до 6."
    return True, n


# ==========================================
# Переходы между шагами
# ==========================================

def advance_after_test_or_admin(state: DialogState, is_test: bool):
    state.is_test = is_test
    state.step = STEP_PLAYER_NAME


def advance_after_player_name(state: DialogState, name: str):
    state.player_name = name
    state.step = STEP_KIT


def advance_after_kit(state: DialogState, kit: str):
    assert kit in VALID_KITS, f"Недопустимый кит: {kit}"
    state.kit = kit
    state.step = STEP_REGION


def advance_after_region(state: DialogState, region: str):
    assert region in REGIONS, f"Недопустимый регион: {region}"
    state.region = region
    state.step = STEP_TIER_BEFORE


def advance_after_tier_before(state: DialogState, tier: str):
    state.tier_before = tier
    if state.is_test:
        state.step = STEP_TIER_TESTED
    else:
        state.step = STEP_TIER_AFTER


def advance_after_tier_tested(state: DialogState, tier: str):
    state.tier_tested = tier
    state.step = STEP_PASSED


def advance_after_passed(state: DialogState, passed: bool):
    state.passed = passed
    # Итоговый тир для ветки "тест": сдал -> tier_tested, не сдал -> tier_before (без изменений)
    state.tier_after = state.tier_tested if passed else state.tier_before
    state.step = _step_after_final_tier_known(state)


def advance_after_tier_after(state: DialogState, tier: str):
    """Только ветка 'без теста' - тир вводится напрямую."""
    state.tier_after = tier
    state.step = STEP_NO_TEST_REASON


def advance_after_no_test_reason(state: DialogState, reason: str):
    state.no_test_reason = reason
    state.step = _step_after_final_tier_known(state)


def _step_after_final_tier_known(state: DialogState) -> str:
    """Общая точка веток: как только известен итоговый тир, решаем -
    предлагать ли кнопку Retired (только если тир HT3+)."""
    if state.tier_after in RETIRED_ELIGIBLE_TIERS:
        return STEP_RETIRED_CHOICE
    return _step_after_retired_choice(state)


def advance_after_retired_choice(state: DialogState, retired: bool):
    state.retired = retired
    state.step = _step_after_retired_choice(state)


def _step_after_retired_choice(state: DialogState) -> str:
    if state.is_test:
        return STEP_DUELS_COUNT
    return STEP_TESTER_SELECT


def advance_after_duels_count(state: DialogState, count: int):
    state.duels_expected = count
    state.duels = []
    state.step = STEP_DUEL_OPPONENT


def advance_after_duel_opponent(state: DialogState, opponent: str):
    state._current_duel_opponent = opponent
    state.step = STEP_DUEL_SCORE


def advance_after_duel_score(state: DialogState, score: str):
    state.duels.append({"opponent": state._current_duel_opponent, "score": score})
    state._current_duel_opponent = None
    if len(state.duels) < state.duels_expected:
        state.step = STEP_DUEL_OPPONENT
    else:
        state.step = STEP_TESTER_SELECT


def advance_after_tester_select(state: DialogState, tester_id: int):
    state.other_tester_id = tester_id
    state.step = STEP_COMMENT


def advance_after_comment(state: DialogState, comment: str):
    state.comment = comment if comment else None
    state.step = STEP_PREVIEW


def confirm_preview(state: DialogState):
    state.step = STEP_DONE
