# -*- coding: utf-8 -*-
"""
Реакции бота на собственные карточки результатов.

Telegram позволяет боту поставить ТОЛЬКО ОДНУ реакцию на сообщение, поэтому
для каждой ситуации задан пул эмодзи, из которого берётся случайная.

Правила (первое подходящее):
  1. Итоговый тир LT5 или LT4 - любое действие на этих тирах: насмешливые.
  2. Понижение (итоговый тир ниже прежнего): грусть.
  3. Тир не изменился (закрепление): нейтральные.
  4. Повышение (в том числе первый ранг на ките): празднование.
Если итоговый тир неизвестен (не из TIER_ORDER) - реакция не ставится.

Все эмодзи - из списка разрешённых Telegram для реакций. Чат должен
разрешать реакции (настройки чата -> Реакции), иначе Telegram откажет;
сбой реакции никогда не мешает публикации результата.
"""

import json
import random

from bot_config import TIER_ORDER

LOW_TIERS = {"LT5", "LT4"}

REACTIONS_LOW_TIER = ["🤣", "🤮", "💩", "🤡"]
REACTIONS_DEMOTION = ["😢", "😭", "💔"]
REACTIONS_HOLD = ["👌", "😐", "🤝", "🗿"]
REACTIONS_PROMOTION = ["🏆", "🎉", "🍾", "🔥", "👏"]


def choose_reaction_emoji(tier_before, tier_after, rng=random):
    """Возвращает эмодзи для смены тира tier_before -> tier_after или None."""
    if tier_after not in TIER_ORDER:
        return None
    if tier_after in LOW_TIERS:
        return rng.choice(REACTIONS_LOW_TIER)
    if tier_before not in TIER_ORDER:
        return rng.choice(REACTIONS_PROMOTION)  # первый ранг на ките
    before_idx = TIER_ORDER.index(tier_before)
    after_idx = TIER_ORDER.index(tier_after)
    if after_idx > before_idx:
        return rng.choice(REACTIONS_DEMOTION)
    if after_idx == before_idx:
        return rng.choice(REACTIONS_HOLD)
    return rng.choice(REACTIONS_PROMOTION)


def set_reaction(bot, chat_id, message_id, emoji):
    """
    Ставит реакцию emoji на сообщение (emoji=None/"" - снимает реакции).
    Не бросает исключений, возвращает True/False.
    """
    try:
        if hasattr(bot, "set_message_reaction"):
            from telebot import types
            reaction = [types.ReactionTypeEmoji(emoji)] if emoji else []
            bot.set_message_reaction(chat_id, message_id, reaction)
        else:
            # Старая версия pyTelegramBotAPI без set_message_reaction
            from telebot import apihelper
            payload = [{"type": "emoji", "emoji": emoji}] if emoji else []
            apihelper._make_request(
                bot.token, 'setMessageReaction',
                params={"chat_id": chat_id, "message_id": message_id,
                        "reaction": json.dumps(payload)},
                method='post',
            )
        return True
    except Exception as e:
        print(f"[reactions] Не удалось поставить реакцию {emoji!r} на {chat_id}/{message_id}: {e}")
        return False


def react_to_tier_change(bot, chat_id, message_id, tier_before, tier_after):
    """Выбирает и ставит реакцию на карточку. Возвращает выбранное эмодзи или None."""
    emoji = choose_reaction_emoji(tier_before, tier_after)
    if emoji:
        set_reaction(bot, chat_id, message_id, emoji)
    return emoji
