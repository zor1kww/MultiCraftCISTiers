// Официальная база данных игроков MultiCraftCISTiers (Финальная версия)
const players = [
    {
        name: "Sneger",
        region: "RU",
        tiers: {
            Crystal: {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "HT1",
                date: "2026-08-18",
                retired: false
            },
            Hardcore: {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "LT1",
                date: "2026-08-21",
                retired: false
            },
            Pickaxe: {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            Emerald: {
                tier: "LT1",
                date: "2026-08-21",
                retired: false
            },
            "Diamond Pot": {
                tier: "HT1",
                date: "2026-08-28",
                retired: false
            },
            Combo: {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            SMP: {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            Gapple: {
                tier: "LT1",
                date: "2026-08-21",
                retired: false
            },
            RVM: {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            }
        },
        matchHistory: [
            {
                date: "2026-08-28",
                kit: "Diamond Pot",
                tester: "-999-",
                tierBefore: "LT1",
                tierAfter: "HT1",
                scoreTester: 6,
                scorePlayer: 16,
                winner: "player",
                comment: null
            }
        ],
        penaltyByKit: {}
    },
    {
        name: "-999-",
        region: "RU",
        tiers: {
            Dragonhide: {
                tier: "HT1",
                date: "2026-08-25",
                retired: false
            },
            Emerald: {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            "Diamond Pot": {
                tier: "LT1",
                date: "2026-08-27",
                retired: false
            },
            SMP: {
                tier: "HT1",
                date: "2026-08-25",
                retired: false
            },
            Crystal: {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            Combo: {
                tier: "HT1",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            Hardcore: {
                tier: "HT1",
                date: "2026-08-28",
                retired: false
            },
            "Emerald Pot": {
                tier: "HT1",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "HT1",
                date: "2026-08-21",
                retired: false
            },
            Beast: {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            Pickaxe: {
                tier: "HT1",
                date: "2026-08-18",
                retired: false
            },
            Gapple: {
                tier: "HT1",
                date: "2026-08-21",
                retired: false
            }
        },
        matchHistory: [
            {
                date: "2026-08-25",
                kit: "Dragonhide",
                tester: "Sneger",
                tierBefore: "LT1",
                tierAfter: "HT1",
                scoreTester: 2,
                scorePlayer: 4,
                winner: "player",
                comment: null
            },
            {
                date: "2026-08-25",
                kit: "SMP",
                tester: "Sneger",
                tierBefore: "LT1",
                tierAfter: "HT1",
                scoreTester: 2,
                scorePlayer: 4,
                winner: "player",
                comment: null
            },
            {
                date: "2026-08-27",
                kit: "Diamond Pot",
                tester: "Sneger",
                tierBefore: "LT1",
                tierAfter: "LT1",
                scoreTester: 4,
                scorePlayer: 3,
                winner: "tester",
                comment: null
            },
            {
                date: "2026-08-28",
                kit: "Hardcore",
                tester: "DzIla_EDITmob",
                tierBefore: "Unranked",
                tierAfter: "LT1",
                scoreTester: 7,
                scorePlayer: 2,
                winner: "tester",
                comment: null
            }
        ],
        penaltyByKit: {
            Hardcore: {
                points: 1.0,
                firstPenaltyDate: "2026-08-28"
            }
        }
    },
    {
        name: "zor1kkqwix",
        region: "RU",
        tiers: {
            Hardcore: {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            SMP: {
                tier: "HT3",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "LT3",
                date: "2026-08-23",
                retired: false
            },
            Combo: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            Pickaxe: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            Emerald: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            "Diamond Pot": {
                tier: "HT4",
                date: "2026-08-25",
                retired: false
            },
            Dragonhide: {
                tier: "HT3",
                date: "2026-08-23",
                retired: false
            },
            Beast: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "HT1",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            Gapple: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            }
        },
        penaltyByKit: {
            Dragonhide: {
                points: 0.0,
                firstPenaltyDate: "2026-08-23"
            },
            "Diamond Pot": {
                points: 0.0,
                firstPenaltyDate: "2026-08-25"
            },
            "Emerald Pot": {
                points: 1.0,
                firstPenaltyDate: "2026-08-23"
            },
            Beast: {
                points: 1.6,
                firstPenaltyDate: "2026-08-25"
            },
            Pickaxe: {
                points: 1.5,
                firstPenaltyDate: "2026-08-25"
            }
        },
        matchHistory: [
            {
                date: "2026-08-23",
                kit: "Dragonhide",
                tester: "система",
                tierBefore: "HT3",
                tierAfter: "LT3",
                scoreTester: 0,
                scorePlayer: 0,
                winner: "tester",
                comment: "Автопонижение: накоплено 2 штрафных очка"
            },
            {
                date: "2026-08-23",
                kit: "Diamond Pot",
                tester: "система",
                tierBefore: "HT3",
                tierAfter: "LT3",
                scoreTester: 0,
                scorePlayer: 0,
                winner: "tester",
                comment: "Автопонижение: накоплено 2 штрафных очка"
            },
            {
                date: "2026-08-23",
                kit: "Dragonhide",
                tester: "test",
                tierBefore: "LT3",
                tierAfter: "HT3",
                scoreTester: 0,
                scorePlayer: 4,
                winner: "player",
                comment: null
            },
            {
                date: "2026-08-23",
                kit: "Emerald Pot",
                tester: "система",
                tierBefore: "HT3",
                tierAfter: "LT3",
                scoreTester: 0,
                scorePlayer: 0,
                winner: "tester",
                comment: "Автопонижение: накоплено 2 штрафных очка"
            },
            {
                date: "2026-08-25",
                kit: "Diamond Pot",
                tester: "система",
                tierBefore: "LT3",
                tierAfter: "HT4",
                scoreTester: 0,
                scorePlayer: 0,
                winner: "tester",
                comment: "Автопонижение: накоплено 2 штрафных очка"
            },
            {
                date: "2026-08-28",
                kit: "Hardcore",
                opponent: "keik1029",
                tierBefore: "LT1",
                tierAfter: "LT1",
                scorePlayer: 2,
                scoreOpponent: 0,
                winner: "player",
                comment: null
            },
            {
                date: "2026-08-28",
                kit: "Emerald",
                opponent: "keik1029",
                tierBefore: "LT3",
                tierAfter: "LT3",
                scorePlayer: 4,
                scoreOpponent: 0,
                winner: "player",
                comment: null
            },
            {
                date: "2026-08-29",
                kit: "RVM",
                opponent: "Say",
                tierBefore: "LT2",
                tierAfter: "LT2",
                scorePlayer: 4,
                scoreOpponent: 2,
                winner: "player",
                comment: null
            },
            {
                date: "2026-08-29",
                kit: "Emerald Pot",
                opponent: "Master",
                tierBefore: "LT3",
                tierAfter: "LT3",
                scorePlayer: 2,
                scoreOpponent: 4,
                winner: "opponent",
                comment: null
            }
        ]
    },
    {
        name: "Itz-Fake",
        region: "RU",
        tiers: {
            Hardcore: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Dev1ce",
        region: "RU",
        tiers: {
            Hardcore: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            "Diamond Pot": {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "_Xx_deras_xX",
        region: "UA",
        tiers: {
            "Emerald Pot": {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            SMP: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            Hardcore: {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            Pickaxe: {
                tier: "HT2",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            Emerald: {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            Dragonhide: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "HT1",
                date: "2026-08-27",
                retired: false
            },
            Combo: {
                tier: "HT2",
                date: "2026-08-18",
                retired: false
            },
            Gapple: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "HT2",
                date: "2026-08-18",
                retired: false
            },
            "Diamond Pot": {
                tier: "HT2",
                date: "2026-08-18",
                retired: false
            }
        },
        matchHistory: [
            {
                date: "2026-08-27",
                kit: "Beast",
                tester: "firary67",
                tierBefore: "LT1",
                tierAfter: "HT1",
                scoreTester: 3,
                scorePlayer: 6,
                winner: "player",
                comment: null
            }
        ],
        penaltyByKit: {}
    },
    {
        name: "2b2tPE",
        region: "KG",
        tiers: {
            Dragonhide: {
                tier: "HT2",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            Emerald: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Hardcore: {
                tier: "HT3",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "HT3",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            "Diamond Pot": {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            SMP: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "The_FV4005",
        region: "RU",
        tiers: {
            Emerald: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Hardcore: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            SMP: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Pickaxe: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            "Diamond Pot": {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Dragonhide: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Gapple: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Combo: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "YouTube_ggs",
        region: "RU",
        tiers: {
            Crystal: {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "LT5",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Master",
        region: "RU",
        tiers: {
            RVM: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Dragonhide: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            "Diamond Pot": {
                tier: "HT3",
                date: "2026-08-18",
                retired: false
            },
            Pickaxe: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Emerald: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            SMP: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "HT3",
                date: "2026-08-29",
                retired: false
            },
            Hardcore: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Combo: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Gapple: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            }
        },
        matchHistory: [
            {
                date: "2026-08-29",
                kit: "Emerald Pot",
                opponent: "zor1kkqwix",
                tierBefore: "LT3",
                tierAfter: "HT3",
                scorePlayer: 4,
                scoreOpponent: 2,
                winner: "player",
                comment: null
            }
        ],
        penaltyByKit: {}
    },
    {
        name: "Darius",
        region: "UA",
        tiers: {
            RVM: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "OcM_sila",
        region: "RU",
        tiers: {
            SMP: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "OcM",
        region: "UA",
        tiers: {
            Hardcore: {
                tier: "HT2",
                date: "2026-06-18",
                retired: true
            },
            Mace: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Say",
        region: "RU",
        tiers: {
            RVM: {
                tier: "HT3",
                date: "2026-08-29",
                retired: false
            },
            "Emerald Pot": {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            }
        },
        matchHistory: [
            {
                date: "2026-08-29",
                kit: "RVM",
                opponent: "zor1kkqwix",
                tierBefore: "LT3",
                tierAfter: "HT3",
                scorePlayer: 2,
                scoreOpponent: 4,
                winner: "opponent",
                comment: null
            }
        ],
        penaltyByKit: {
            RVM: {
                points: 1.0,
                firstPenaltyDate: "2026-08-29"
            }
        }
    },
    {
        name: "ZirtMobile",
        region: "RU",
        tiers: {
            RVM: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Dragonhide: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "HT3",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            "Diamond Pot": {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "HT2",
                date: "2026-08-18",
                retired: false
            },
            Pickaxe: {
                tier: "HT2",
                date: "2026-08-21",
                retired: false
            },
            Hardcore: {
                tier: "HT2",
                date: "2026-08-18",
                retired: false
            },
            Gapple: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            Combo: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            SMP: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Emerald: {
                tier: "HT2",
                date: "2026-08-18",
                retired: false
            }
        },
        penaltyByKit: {
            Emerald: {
                points: 0.4,
                firstPenaltyDate: "2026-08-25"
            }
        }
    },
    {
        name: "WezzikBigClop",
        region: "RU",
        tiers: {
            RVM: {
                tier: "LT3",
                date: "2026-08-25",
                retired: false
            },
            "Emerald Pot": {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            SMP: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Dragonhide: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Pickaxe: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Hardcore: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            "Diamond Pot": {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            }
        },
        matchHistory: [
            {
                date: "2026-08-25",
                kit: "RVM",
                tester: "-999-",
                tierBefore: "HT4",
                tierAfter: "LT3",
                scoreTester: 4,
                scorePlayer: 0,
                winner: "tester",
                comment: null
            }
        ],
        penaltyByKit: {}
    },
    {
        name: "NeXoXoroshy2",
        region: "KG",
        tiers: {
            "Emerald Pot": {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            SMP: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Hardcore: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            "Diamond Pot": {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Dragonhide: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Emerald: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Combo: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Gapple: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "LEGENDAMETRO",
        region: "RU",
        tiers: {
            "Emerald Pot": {
                tier: "HT3",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            Hardcore: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Combo: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "LT3",
                date: "2026-08-21",
                retired: false
            }
        }
    },
    {
        name: "Nikos",
        region: "RU",
        tiers: {
            RVM: {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Y-Japan",
        region: "RU",
        tiers: {
            Crystal: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "LT5",
                date: "2026-08-18",
                retired: false
            },
            SMP: {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            },
            Hardcore: {
                tier: "LT5",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "-BaCk-",
        region: "KZ",
        tiers: {
            Mace: {
                tier: "LT3",
                date: "2026-08-22",
                retired: false
            },
            Dragonhide: {
                tier: "HT3",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "HT3",
                date: "2026-08-18",
                retired: false
            },
            Hardcore: {
                tier: "HT3",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Emerald: {
                tier: "HT3",
                date: "2026-08-18",
                retired: false
            },
            "Diamond Pot": {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            SMP: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Pickaxe: {
                tier: "HT3",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Gapple: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            }
        },
        matchHistory: [
            {
                date: "2026-08-22",
                kit: "Mace",
                tester: "_Xx_deras_xX",
                tierBefore: "LT3",
                tierAfter: "LT3",
                scoreTester: 10,
                scorePlayer: 0,
                winner: "tester",
                comment: null
            },
            {
                date: "2026-08-29",
                kit: "RVM",
                opponent: "Aura",
                tierBefore: "LT3",
                tierAfter: "LT3",
                scorePlayer: 1,
                scoreOpponent: 4,
                winner: "opponent",
                comment: null
            }
        ],
        penaltyByKit: {
            Hardcore: {
                points: 1.5,
                firstPenaltyDate: "2026-08-25"
            },
            RVM: {
                points: 1.5,
                firstPenaltyDate: "2026-08-29"
            }
        }
    },
    {
        name: "Hayzi",
        region: "RU",
        tiers: {
            Emerald: {
                tier: "LT5",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "LT5",
                date: "2026-08-18",
                retired: false
            },
            Combo: {
                tier: "LT5",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "LT5",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Samaelka",
        region: "RU",
        tiers: {
            Dragonhide: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            SMP: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Hardcore: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Pickaxe: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "DzIla_EDITS",
        region: "RU",
        tiers: {
            Beast: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            SMP: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "boy",
        region: "UA",
        tiers: {
            Hardcore: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Pickaxe: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Emerald: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "HT3",
                date: "2026-08-18",
                retired: false
            },
            Dragonhide: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            SMP: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            "Diamond Pot": {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Mirops",
        region: "RU",
        tiers: {
            Mace: {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Emerald: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "LT5",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Dragonhide: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "blablablublubluble",
        region: "RU",
        tiers: {
            Beast: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Dragonhide: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            "Diamond Pot": {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "_-XKakTakX-_",
        region: "RU",
        tiers: {
            Dragonhide: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "LT2",
                date: "2026-08-27",
                retired: false
            },
            Crystal: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            SMP: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Pickaxe: {
                tier: "LT3",
                date: "2026-08-21",
                retired: false
            },
            "Diamond Pot": {
                tier: "LT2",
                date: "2026-08-25",
                retired: false
            },
            Beast: {
                tier: "HT2",
                date: "2026-08-25",
                retired: false
            }
        },
        matchHistory: [
            {
                date: "2026-08-25",
                kit: "Diamond Pot",
                tester: "zor1kkqwix",
                tierBefore: "LT3",
                tierAfter: "LT2",
                scoreTester: 0,
                scorePlayer: 4,
                winner: "player",
                comment: null
            },
            {
                date: "2026-08-25",
                kit: "Beast",
                tester: "zor1kkqwix",
                tierBefore: "LT3",
                tierAfter: "HT2",
                scoreTester: 1,
                scorePlayer: 6,
                winner: "player",
                comment: null
            },
            {
                date: "2026-08-27",
                kit: "RVM",
                tester: "DzIla_EDITSmob",
                tierBefore: "LT3",
                tierAfter: "LT2",
                scoreTester: 4,
                scorePlayer: 2,
                winner: "tester",
                comment: null
            }
        ],
        penaltyByKit: {
            RVM: {
                points: 1.0,
                firstPenaltyDate: "2026-08-27"
            }
        }
    },
    {
        name: "Igrok355",
        region: "RU",
        tiers: {
            Beast: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Emerald: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Dragonhide: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Prosto_oleg100-7",
        region: "RU",
        tiers: {
            Crystal: {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "LT2",
                date: "2026-08-25",
                retired: false
            },
            SMP: {
                tier: "LT2",
                date: "2026-08-21",
                retired: false
            },
            "Diamond Pot": {
                tier: "LT2",
                date: "2026-08-27",
                retired: false
            },
            Beast: {
                tier: "HT2",
                date: "2026-08-22",
                retired: false
            },
            Emerald: {
                tier: "LT2",
                date: "2026-08-25",
                retired: false
            },
            Dragonhide: {
                tier: "LT3",
                date: "2026-08-23",
                retired: false
            },
            Mace: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "HT4",
                date: "2026-08-28",
                retired: false
            },
            Combo: {
                tier: "HT3",
                date: "2026-08-18",
                retired: false
            },
            Gapple: {
                tier: "HT4",
                date: "2026-08-28",
                retired: false
            },
            Hardcore: {
                tier: "LT2",
                date: "2026-08-25",
                retired: false
            },
            Pickaxe: {
                tier: "LT3",
                date: "2026-08-21",
                retired: false
            }
        },
        matchHistory: [
            {
                date: "2026-08-22",
                kit: "Beast",
                tester: "zor1kkqwix",
                tierBefore: "LT2",
                tierAfter: "HT2",
                scoreTester: 3,
                scorePlayer: 6,
                winner: "player",
                comment: null
            },
            {
                date: "2026-08-22",
                kit: "Dragonhide",
                tester: "zor1kkqwix",
                tierBefore: "HT3",
                tierAfter: "LT3",
                scoreTester: 6,
                scorePlayer: 0,
                winner: "tester",
                comment: null
            },
            {
                date: "2026-08-23",
                kit: "Dragonhide",
                tester: "zor1kkqwix",
                tierBefore: "HT3",
                tierAfter: "LT3",
                scoreTester: 6,
                scorePlayer: 0,
                winner: "tester",
                comment: "тест"
            },
            {
                date: "2026-08-23",
                kit: "Gapple",
                tester: "zor1kkqwix",
                tierBefore: "LT3",
                tierAfter: "HT4",
                scoreTester: 2,
                scorePlayer: 0,
                winner: "tester",
                comment: null
            },
            {
                date: "2026-08-24",
                kit: "Emerald Pot",
                tester: "zor1kkqwix",
                tierBefore: "LT3",
                tierAfter: "HT4",
                scoreTester: 5,
                scorePlayer: 0,
                winner: "tester",
                comment: null
            },
            {
                date: "2026-08-24",
                kit: "Emerald",
                tester: "_Xx_deras_xX",
                tierBefore: "LT2",
                tierAfter: "HT3",
                scoreTester: 4,
                scorePlayer: 0,
                winner: "tester",
                comment: null
            },
            {
                date: "2026-08-24",
                kit: "Emerald",
                tester: "система",
                tierBefore: "HT3",
                tierAfter: "LT3",
                scoreTester: 0,
                scorePlayer: 0,
                winner: "tester",
                comment: "Автопонижение: накоплено 2 штрафных очка"
            },
            {
                date: "2026-08-25",
                kit: "Hardcore",
                tester: "-BaCk-",
                tierBefore: "LT3",
                tierAfter: "LT2",
                scoreTester: 1,
                scorePlayer: 4,
                winner: "player",
                comment: null
            },
            {
                date: "2026-08-25",
                kit: "RVM",
                tester: "HAVCHIK",
                tierBefore: "HT3",
                tierAfter: "LT2",
                scoreTester: 2,
                scorePlayer: 4,
                winner: "player",
                comment: null
            },
            {
                date: "2026-08-25",
                kit: "Emerald",
                tester: "ZirtMobile",
                tierBefore: "HT3",
                tierAfter: "LT2",
                scoreTester: 4,
                scorePlayer: 6,
                winner: "player",
                comment: null
            },
            {
                date: "2026-08-27",
                kit: "Diamond Pot",
                tester: "DzIla_EDITSmob",
                tierBefore: "LT2",
                tierAfter: "LT2",
                scoreTester: 4,
                scorePlayer: 2,
                winner: "tester",
                comment: "анрил играть на даймонт кб после отдачи новой"
            },
            {
                date: "2026-08-28",
                kit: "Gapple",
                opponent: "zor1kkqwix",
                tierBefore: "HT4",
                tierAfter: "HT4",
                scorePlayer: 0,
                scoreOpponent: 4,
                winner: "opponent",
                comment: null
            },
            {
                date: "2026-08-28",
                kit: "Emerald Pot",
                opponent: "zor1kkqwix",
                tierBefore: "HT4",
                tierAfter: "HT4",
                scorePlayer: 0,
                scoreOpponent: 4,
                winner: "opponent",
                comment: null
            }
        ],
        penaltyByKit: {
            Emerald: {
                points: 0.0,
                firstPenaltyDate: "2026-08-24"
            },
            "Diamond Pot": {
                points: 1.0,
                firstPenaltyDate: "2026-08-27"
            }
        }
    },
    {
        name: "BossKFC",
        region: "RU",
        tiers: {
            Hardcore: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "LT3",
                date: "2026-08-24",
                retired: false
            }
        },
        matchHistory: [
            {
                date: "2026-08-24",
                kit: "Emerald Pot",
                tester: "zor1kkqwix",
                tierBefore: "Unranked",
                tierAfter: "LT3",
                scoreTester: 0,
                scorePlayer: 4,
                winner: "player",
                comment: null
            }
        ],
        penaltyByKit: {}
    },
    {
        name: "Lolotrack",
        region: "UA",
        tiers: {
            Crystal: {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            },
            "Diamond Pot": {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Cira",
        region: "RU",
        tiers: {
            Hardcore: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "HT2",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "HT3",
                date: "2026-08-18",
                retired: false
            },
            Pickaxe: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Gggg1029",
        region: "RU",
        tiers: {
            Mace: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Hardcore: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Combo: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            SMP: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "YouTubePvPXelp_999",
        region: "RU",
        tiers: {
            SMP: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Saxapok13373",
        region: "RU",
        tiers: {
            SMP: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Dzhambulat1322",
        region: "RU",
        tiers: {
            RVM: {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "D4rK_S1lA",
        region: "RU",
        tiers: {
            Beast: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Hardcore: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Gapple: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "7STARS",
        region: "RU",
        tiers: {
            Dragonhide: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Hardcore: {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            },
            SMP: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Combo: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            "Diamond Pot": {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Emerald: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Gapple: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Kenny13",
        region: "RU",
        tiers: {
            Hardcore: {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Exponat",
        region: "RU",
        tiers: {
            "Emerald Pot": {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Gapple: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Noch",
        region: "RU",
        tiers: {
            RVM: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "-_-nyschka-_-",
        region: "RU",
        tiers: {
            Mace: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Susla",
        region: "RU",
        tiers: {
            Mace: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            SMP: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "rrrr11",
        region: "RU",
        tiers: {
            Mace: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "hohNagiBator",
        region: "RU",
        tiers: {
            Emerald: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Legenda_loytaba",
        region: "RU",
        tiers: {
            Hardcore: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "MAXTY",
        region: "RU",
        tiers: {
            RVM: {
                tier: "LT5",
                date: "2026-08-18",
                retired: false
            },
            Emerald: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "saimon",
        region: "RU",
        tiers: {
            Mace: {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            },
            Hardcore: {
                tier: "HT5",
                date: "2026-08-21",
                retired: false
            }
        }
    },
    {
        name: "Grisha",
        region: "RU",
        tiers: {
            Mace: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Meteor",
        region: "UA",
        tiers: {
            RVM: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "killdoIbaeb4455",
        region: "RU",
        tiers: {
            Hardcore: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Sneszok123",
        region: "RU",
        tiers: {
            Beast: {
                tier: "HT3",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Aliazo",
        region: "RU",
        tiers: {
            Hardcore: {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            },
            SMP: {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "gftun",
        region: "RU",
        tiers: {
            Dragonhide: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Vex",
        region: "RU",
        tiers: {
            Hardcore: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            "Diamond Pot": {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Dragonhide: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "M_E_G_A",
        region: "RU",
        tiers: {
            RVM: {
                tier: "LT5",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "HT5",
                date: "2026-08-22",
                retired: false
            }
        },
        matchHistory: [
            {
                date: "2026-08-22",
                kit: "Beast",
                tester: "-BaCk-",
                tierBefore: "LT5",
                tierAfter: "HT5",
                scoreTester: 4,
                scorePlayer: 0,
                winner: "tester",
                comment: null
            }
        ]
    },
    {
        name: "JANDELL",
        region: "RU",
        tiers: {
            Hardcore: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Michael_59k_YT",
        region: "AM",
        tiers: {
            Beast: {
                tier: "HT3",
                date: "2026-08-25",
                retired: false
            },
            Mace: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Pickaxe: {
                tier: "LT2",
                date: "2026-08-22",
                retired: false
            },
            Hardcore: {
                tier: "LT3",
                date: "2026-08-22",
                retired: false
            },
            Emerald: {
                tier: "HT4",
                date: "2026-08-23",
                retired: false
            },
            "Diamond Pot": {
                tier: "LT3",
                date: "2026-08-25",
                retired: false
            }
        },
        matchHistory: [
            {
                date: "2026-08-22",
                kit: "Hardcore",
                tester: "zor1kkqwix",
                tierBefore: "HT4",
                tierAfter: "LT3",
                scoreTester: 4,
                scorePlayer: 0,
                winner: "tester",
                comment: null
            },
            {
                date: "2026-08-22",
                kit: "Pickaxe",
                tester: "zor1kkqwix",
                tierBefore: "LT3",
                tierAfter: "LT2",
                scoreTester: 4,
                scorePlayer: 3,
                winner: "tester",
                comment: "проходит бридж лт2"
            },
            {
                date: "2026-08-23",
                kit: "Emerald",
                tester: "zor1kkqwix",
                tierBefore: "Unranked",
                tierAfter: "HT4",
                scoreTester: 4,
                scorePlayer: 0,
                winner: "tester",
                comment: null
            },
            {
                date: "2026-08-23",
                kit: "Beast",
                tester: "zor1kkqwix",
                tierBefore: "LT3",
                tierAfter: "HT3",
                scoreTester: 6,
                scorePlayer: 3,
                winner: "tester",
                comment: null
            },
            {
                date: "2026-08-25",
                kit: "Beast",
                tester: "zor1kkqwix",
                tierBefore: "LT3",
                tierAfter: "HT3",
                scoreTester: 6,
                scorePlayer: 3,
                winner: "tester",
                comment: null
            },
            {
                date: "2026-08-25",
                kit: "Diamond Pot",
                tester: "_Xx_deras_xX",
                tierBefore: "Unranked",
                tierAfter: "LT3",
                scoreTester: 4,
                scorePlayer: 0,
                winner: "tester",
                comment: null
            }
        ],
        penaltyByKit: {
            Beast: {
                points: 1.6,
                firstPenaltyDate: "2026-08-23"
            }
        }
    },
    {
        name: "Aura",
        region: "RU",
        tiers: {
            Hardcore: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            Emerald: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            "Diamond Pot": {
                tier: "HT2",
                date: "2026-08-18",
                retired: false
            },
            SMP: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            Dragonhide: {
                tier: "HT3",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "HT3",
                date: "2026-08-29",
                retired: false
            },
            "Emerald Pot": {
                tier: "LT2",
                date: "2026-08-23",
                retired: false
            },
            Mace: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            Pickaxe: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            Combo: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            Gapple: {
                tier: "HT3",
                date: "2026-08-18",
                retired: false
            }
        },
        matchHistory: [
            {
                date: "2026-08-23",
                kit: "Emerald Pot",
                tester: "zor1kkqwix",
                tierBefore: "HT3",
                tierAfter: "LT2",
                scoreTester: 0,
                scorePlayer: 4,
                winner: "player",
                comment: null
            },
            {
                date: "2026-08-29",
                kit: "RVM",
                opponent: "-BaCk-",
                tierBefore: "LT3",
                tierAfter: "HT3",
                scorePlayer: 4,
                scoreOpponent: 1,
                winner: "player",
                comment: null
            }
        ],
        penaltyByKit: {}
    },
    {
        name: "Topor",
        region: "RU",
        tiers: {
            "Emerald Pot": {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Combo: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            SMP: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Hardcore: {
                tier: "HT3",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "DzIla_EDITSmob",
        region: "RU",
        tiers: {
            "Emerald Pot": {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            "Diamond Pot": {
                tier: "HT2",
                date: "2026-08-18",
                retired: false
            },
            Emerald: {
                tier: "LT1",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "HT2",
                date: "2026-08-27",
                retired: false
            },
            RVM: {
                tier: "LT2",
                date: "2026-08-27",
                retired: false
            },
            Hardcore: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            Dragonhide: {
                tier: "HT2",
                date: "2026-08-18",
                retired: false
            },
            Pickaxe: {
                tier: "HT2",
                date: "2026-08-25",
                retired: false
            },
            SMP: {
                tier: "LT1",
                date: "2026-08-27",
                retired: false
            }
        },
        matchHistory: [
            {
                date: "2026-08-22",
                kit: "Beast",
                tester: "Sneger",
                tierBefore: "LT2",
                tierAfter: "LT1",
                scoreTester: 5,
                scorePlayer: 6,
                winner: "tester",
                comment: null
            },
            {
                date: "2026-08-25",
                kit: "Pickaxe",
                tester: "zor1kkqwix",
                tierBefore: "Unranked",
                tierAfter: "HT2",
                scoreTester: 1,
                scorePlayer: 4,
                winner: "player",
                comment: null
            },
            {
                date: "2026-08-27",
                kit: "SMP",
                tester: "-999-",
                tierBefore: "Unranked",
                tierAfter: "LT1",
                scoreTester: 4,
                scorePlayer: 2,
                winner: "tester",
                comment: null
            },
            {
                date: "2026-08-27",
                kit: "Beast",
                tester: "-999-",
                tierBefore: "LT1",
                tierAfter: "HT2",
                scoreTester: 3,
                scorePlayer: 6,
                winner: "tester",
                comment: null
            },
            {
                date: "2026-08-27",
                kit: "RVM",
                tester: "zor1kkqwix",
                tierBefore: "LT1",
                tierAfter: "LT2",
                scoreTester: 3,
                scorePlayer: 4,
                winner: "player",
                comment: null
            }
        ],
        penaltyByKit: {}
    },
    {
        name: "AMORE",
        region: "RU",
        tiers: {
            Hardcore: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "LT5",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "h9nto",
        region: "RU",
        tiers: {
            Mace: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "HT3",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "1641085O8",
        region: "RU",
        tiers: {
            "Emerald Pot": {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            },
            Dragonhide: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Top",
        region: "UA",
        tiers: {
            Hardcore: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "HT4",
                date: "2026-08-28",
                retired: false
            },
            Mace: {
                tier: "LT5",
                date: "2026-08-18",
                retired: false
            },
            Dragonhide: {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            },
            Gapple: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            }
        },
        matchHistory: [
            {
                date: "2026-08-28",
                kit: "Beast",
                tester: "zor1kkqwix",
                tierBefore: "HT4",
                tierAfter: "HT4",
                scoreTester: 5,
                scorePlayer: 0,
                winner: "tester",
                comment: null
            }
        ],
        penaltyByKit: {}
    },
    {
        name: "HAVCHIK",
        region: "RU",
        tiers: {
            "Emerald Pot": {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "HT3",
                date: "2026-08-21",
                retired: false
            }
        },
        penaltyByKit: {
            RVM: {
                points: 1.0,
                firstPenaltyDate: "2026-08-25"
            }
        }
    },
    {
        name: "Mirage",
        region: "RU",
        tiers: {
            "Emerald Pot": {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "-Sorry-",
        region: "RU",
        tiers: {
            Mace: {
                tier: "HT4",
                date: "2026-08-21",
                retired: false
            },
            Hardcore: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Fialka_",
        region: "RU",
        tiers: {
            SMP: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "NOVENKIY1",
        region: "RU",
        tiers: {
            RVM: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Dragonhide: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "zaxvatchik6",
        region: "RU",
        tiers: {
            RVM: {
                tier: "LT5",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Hardcore: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "-_MACKA_-",
        region: "RU",
        tiers: {
            Dragonhide: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "LT3",
                date: "2026-08-21",
                retired: false
            }
        }
    },
    {
        name: "Karabasik",
        region: "RU",
        tiers: {
            Dragonhide: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Emerald: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "ofofoffo",
        region: "UA",
        tiers: {
            "Emerald Pot": {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "sw3don",
        region: "RU",
        tiers: {
            Hardcore: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Dragonhide: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "xivivideking",
        region: "RU",
        tiers: {
            RVM: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "LT2",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "qak1ow",
        region: "RU",
        tiers: {
            RVM: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Dragonhide: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Gapple: {
                tier: "LT3",
                date: "2026-08-18",
                retired: false
            },
            Beast: {
                tier: "LT3",
                date: "2026-08-27",
                retired: false
            }
        },
        matchHistory: [
            {
                date: "2026-08-27",
                kit: "Beast",
                tester: "DzIla_EDITSmob",
                tierBefore: "Unranked",
                tierAfter: "LT3",
                scoreTester: 5,
                scorePlayer: 0,
                winner: "tester",
                comment: "слаба но урон наносил может дойти до хт3. Квалификационный тест пройден"
            }
        ],
        penaltyByKit: {}
    },
    {
        name: "YTdrumv",
        region: "RU",
        tiers: {
            Beast: {
                tier: "LT5",
                date: "2026-08-18",
                retired: false
            },
            Emerald: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Crystal: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Dragonhide: {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            },
            "Diamond Pot": {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            },
            Hardcore: {
                tier: "LT5",
                date: "2026-08-18",
                retired: false
            },
            Pickaxe: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Mace: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            SMP: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Gapple: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            Combo: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "Zock",
        region: "RU",
        tiers: {
            RVM: {
                tier: "LT4",
                date: "2026-08-18",
                retired: false
            },
            "Emerald Pot": {
                tier: "HT4",
                date: "2026-08-21",
                retired: false
            }
        }
    },
    {
        name: "-Dan41k",
        region: "RU",
        tiers: {
            Mace: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Hardcore: {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "vov4ikusss",
        region: "RU",
        tiers: {
            Beast: {
                tier: "HT5",
                date: "2026-08-18",
                retired: false
            },
            RVM: {
                tier: "LT5",
                date: "2026-08-18",
                retired: false
            }
        }
    },
    {
        name: "firary67",
        region: "RU",
        tiers: {
            Hardcore: {
                tier: "LT2",
                date: "2026-08-29",
                retired: false
            },
            Emerald: {
                tier: "HT1",
                date: "2026-08-21",
                retired: false
            },
            Beast: {
                tier: "LT1",
                date: "2026-08-27",
                retired: false
            }
        },
        matchHistory: [
            {
                date: "2026-08-27",
                kit: "Beast",
                tester: "DzIla_EDITSmob",
                tierBefore: "Unranked",
                tierAfter: "LT1",
                scoreTester: 6,
                scorePlayer: 5,
                winner: "tester",
                comment: null
            },
            {
                date: "2026-08-29",
                kit: "Hardcore",
                opponent: "DzIla_EDITmob",
                tierBefore: "LT3",
                tierAfter: "LT2",
                scorePlayer: 3,
                scoreOpponent: 4,
                winner: "opponent",
                comment: null
            }
        ],
        penaltyByKit: {
            Beast: {
                points: 0.8,
                firstPenaltyDate: "2026-08-27"
            }
        }
    },
    {
        name: "bob_ara_1029",
        region: "RU",
        tiers: {
            Mace: {
                tier: "HT4",
                date: "2026-08-18",
                retired: false
            },
            Pickaxe: {
                tier: "LT3",
                date: "2026-08-21",
                retired: false
            }
        }
    },
    {
        name: "Egoiste",
        region: "UA",
        tiers: {
            RVM: {
                tier: "HT5",
                date: "2026-08-21",
                retired: false
            },
            Mace: {
                tier: "HT4",
                date: "2026-08-21",
                retired: false
            }
        }
    },
    {
        name: "SoLoGeMs",
        region: "RU",
        tiers: {
            Crystal: {
                tier: "LT4",
                date: "2026-08-21",
                retired: false
            },
            RVM: {
                tier: "LT5",
                date: "2026-08-21",
                retired: false
            },
            Pickaxe: {
                tier: "LT5",
                date: "2026-08-21",
                retired: false
            },
            Beast: {
                tier: "LT4",
                date: "2026-08-21",
                retired: false
            },
            Dragonhide: {
                tier: "LT4",
                date: "2026-08-21",
                retired: false
            }
        }
    },
    {
        name: "meker_pvp",
        region: "UA",
        tiers: {
            RVM: {
                tier: "LT4",
                date: "2026-08-21",
                retired: false
            }
        }
    },
    {
        name: "Domchikr",
        region: "RU",
        tiers: {
            Hardcore: {
                tier: "LT5",
                date: "2026-08-21",
                retired: false
            }
        }
    },
    {
        name: "FASTER-cq-q",
        region: "RU",
        tiers: {
            Hardcore: {
                tier: "HT3",
                date: "2026-08-21",
                retired: false
            }
        }
    },
    {
        name: "_UnU_",
        region: "RU",
        tiers: {
            Mace: {
                tier: "LT4",
                date: "2026-08-21",
                retired: false
            }
        }
    },
    {
        name: "BBBOOOSSS",
        region: "RU",
        tiers: {
            RVM: {
                tier: "HT5",
                date: "2026-08-21",
                retired: false
            }
        }
    },
    {
        name: "test",
        region: "RU",
        tiers: {
            Dragonhide: {
                tier: "LT3",
                date: "2026-08-23",
                retired: false
            },
            "Diamond Pot": {
                tier: "HT3",
                date: "2026-08-23",
                retired: false
            }
        },
        matchHistory: [
            {
                date: "2026-08-23",
                kit: "Dragonhide",
                tester: "zor1kkqwix",
                tierBefore: "LT3",
                tierAfter: "HT3",
                scoreTester: 0,
                scorePlayer: 6,
                winner: "player",
                comment: null
            },
            {
                date: "2026-08-23",
                kit: "Diamond Pot",
                tester: "zor1kkqwix",
                tierBefore: "LT3",
                tierAfter: "HT3",
                scoreTester: 2,
                scorePlayer: 4,
                winner: "player",
                comment: null
            },
            {
                date: "2026-08-23",
                kit: "Diamond Pot",
                tester: "zor1kkqwix",
                tierBefore: "LT3",
                tierAfter: "HT3",
                scoreTester: 2,
                scorePlayer: 4,
                winner: "player",
                comment: null
            },
            {
                date: "2026-08-23",
                kit: "Dragonhide",
                tester: "система",
                tierBefore: "HT3",
                tierAfter: "LT3",
                scoreTester: 0,
                scorePlayer: 0,
                winner: "tester",
                comment: "Автопонижение: накоплено 2 штрафных очка"
            }
        ],
        penaltyByKit: {
            Dragonhide: {
                points: 0.0,
                firstPenaltyDate: "2026-08-23"
            }
        }
    },
    {
        name: "aetherelegantius",
        region: "RU",
        tiers: {
            RVM: {
                tier: "LT3",
                date: "2026-08-25",
                retired: false
            }
        },
        matchHistory: [
            {
                date: "2026-08-25",
                kit: "RVM",
                tester: "-BaCk-",
                tierBefore: "Unranked",
                tierAfter: "LT3",
                scoreTester: 0,
                scorePlayer: 4,
                winner: "player",
                comment: "квалификационный тест пройден"
            }
        ],
        penaltyByKit: {}
    },
    {
        name: "_-XKakTak-_",
        region: "RU",
        tiers: {
            Hardcore: {
                tier: "LT3",
                date: "2026-08-27",
                retired: false
            }
        },
        matchHistory: [
            {
                date: "2026-08-27",
                kit: "Hardcore",
                tester: "-BaCk-",
                tierBefore: "Unranked",
                tierAfter: "LT3",
                scoreTester: 1,
                scorePlayer: 4,
                winner: "player",
                comment: "Квалификационный тест пройден"
            }
        ],
        penaltyByKit: {}
    },
    {
        name: "keik1029",
        region: "BY",
        tiers: {
            Hardcore: {
                tier: "LT5",
                date: "2026-08-28",
                retired: false
            },
            Emerald: {
                tier: "LT5",
                date: "2026-08-28",
                retired: false
            }
        },
        matchHistory: [
            {
                date: "2026-08-28",
                kit: "Hardcore",
                opponent: "zor1kkqwix",
                tierBefore: "Unranked",
                tierAfter: "LT5",
                scorePlayer: 0,
                scoreOpponent: 2,
                winner: "opponent",
                comment: null
            },
            {
                date: "2026-08-28",
                kit: "Emerald",
                opponent: "zor1kkqwix",
                tierBefore: "Unranked",
                tierAfter: "LT5",
                scorePlayer: 0,
                scoreOpponent: 4,
                winner: "opponent",
                comment: null
            }
        ],
        penaltyByKit: {}
    },
    {
        name: "DzIla_EDITmob",
        region: "",
        tiers: {},
        matchHistory: [
            {
                date: "2026-08-29",
                kit: "Hardcore",
                opponent: "firary67",
                tierBefore: null,
                tierAfter: null,
                scorePlayer: 4,
                scoreOpponent: 3,
                winner: "player",
                comment: null
            }
        ],
        penaltyByKit: {}
    }
];
