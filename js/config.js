const CONFIG = {
    // Система начисления очков за тиры в режимах
    ptsValues: {
        "HT1": 100, "LT1": 90,
        "HT2": 80,  "LT2": 70,
        "HT3": 60,  "LT3": 50,
        "HT4": 40,  "LT4": 30,
        "HT5": 20,  "LT5": 10,
        "Unranked": 0
    },

    // Все киты (теперь 14 штук с SMP)
    kits: {
        "Hardcore": { icon: "assets/logos/hardcore.png", displayName: "Hardcore Kit" },
        "Manhunt": { icon: "assets/logos/manhunt.png", displayName: "Manhunt Kit" },
        "Diamond": { icon: "assets/logos/diamond.png", displayName: "Diamond Kit" },
        "Beast": { icon: "assets/logos/beast.png", displayName: "Beast Kit" },
        "Emerald": { icon: "assets/logos/emerald.png", displayName: "Emerald Kit" },
        "Emerald Pot": { icon: "assets/logos/emerald_pot.png", displayName: "Emerald Pot Kit" },
        "RVM": { icon: "assets/logos/rvm.png", displayName: "RVM Kit" },
        "Dragonhide": { icon: "assets/logos/dragonhide.png", displayName: "Dragonhide Kit" },
        "Pickaxe": { icon: "assets/logos/pickaxe.png", displayName: "Pickaxe Kit" },
        "Combo": { icon: "assets/logos/combo.png", displayName: "Combo Kit" },
        "Gapple": { icon: "assets/logos/gapple.png", displayName: "Gapple Kit" },
        "Mace": { icon: "assets/logos/mace.png", displayName: "Mace Kit" },
        "Crystal": { icon: "assets/logos/crystal.png", displayName: "Crystal Kit" },
        "SMP": { icon: "assets/logos/smp.png", displayName: "SMP Kit" }
    },

    // Описания для раздела Вики (все 14 китов)
    wikiDescriptions: {
        "Hardcore": "Классическое PvP на истощение. Важно следить за таймингами ударов и расходом брони. Ниже представлен стандартный сетап инвентаря для матчей.",
        "Manhunt": "Динамичный режим с упором на позиционирование, использование лавы, вёдер с водой и компаса для отслеживания цели.",
        "Diamond": "Сражения в алмазной броне. Классический баланс урона и защиты, требующий стабильного аима и контроля дистанции.",
        "Beast": "Режим с повышенным уроном или особыми характеристиками снаряжения, где любая ошибка может стать фатальной.",
        "Emerald": "Продвинутый уровень сражений с использованием изумрудных сетов, изменённой динамикой передвижения и тактическими элементами.",
        "Emerald Pot": "Скоростное PvP с упором на моментальное исцеление взрывными зельями (всплесками) на изумрудной арене.",
        "RVM": "Уникальный соревновательный сетап (Ресурс-Пак / Модификация), проверяющий чистый скилл микроконтроля игрока.",
        "Dragonhide": "Сражения в сверхпрочной броне из драконьей кожи. Затяжные и тактические бои, где важен менеджмент ресурсов.",
        "Pickaxe": "Режим, где главным инструментом боя или прорыва обороны соперника становится кирка. Нестандартные механики блоков.",
        "Combo": "PvP с отключённой задержкой на удары (no hitdelay). Главная задача — поймать оппонента в бесконечную серию ударов в воздухе.",
        "Gapple": "Бои на золотых яблоках. Бесконечная регенерация и упор на выталкивание, комбо-удары и поломку экипировки врага.",
        "Mace": "Сражения с использованием Булавы. Высокий акцент на вертикальный геймплей, прыжки и сокрушительные дроп-атаки.",
        "Crystal": "Кристальное PvP. Самый взрывоопасный и быстрый режим, где исход боя решается за доли секунды точной установкой кристаллов Энда.",
        "SMP": "Режим выживания в соревновательном стиле. Использование кастомных механик приватных серверов, тактического окружения и смешанного снаряжения."
    },

    // Изменённая структура тестеров по должностям
    staff: {
        seniorTesters: ["-999-", "Sneger"],
        qualifyingTesters: ["zor1kkqwix"]
    }
};
