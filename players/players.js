// Официальная база данных игроков MultiCraftCISTiers (Финальная версия)
const players = [
    {
        name: "Sneger",
        region: "RU",
        device: "PH",
        tiers: {
            Crystal: "LT1",
            Mace: "HT1",
            Hardcore: "HT2",
            "Emerald Pot": "LT1",
            Beast: "HT1",
            Pickaxe: "LT3",
            Emerald: "HT1"
        }
    },
    {
        name: "-999-",
        region: "RU",
        device: "TB",
        tiers: {
            Dragonhide: "RLT1",
            Emerald: "RHT1",
            "Diamond Pot": "RLT1",
            SMP: "RHT1",
            Crystal: "LT1",
            Combo: "RHT1",
            Mace: "LT1",
            Hardcore: "HT1",
            "Emerald Pot": "LT1",
            RVM: "RHT1",
            Beast: "LT1",
            Pickaxe: "HT1"
        }
    },
    {
        name: "zor1kkqwix",
        region: "RU",
        device: "PH",
        tiers: {
            Hardcore: "LT1",
            SMP: "HT3",
            "Emerald Pot": "HT3",
            Combo: "HT4",
            RVM: "HT3",
            Pickaxe: "LT3",
            Emerald: "LT3",
            "Diamond Pot": "HT3",
            Dragonhide: "HT3",
            Beast: "LT2",
            Crystal: "HT1",
            Mace: "LT1",
            Gapple: "LT3"
        }
    },
    {
        name: "Itz-Fake",
        region: "RU",
        device: "PH",
        tiers: {
            Hardcore: "RLT4"
        }
    },
    {
        name: "Dev1ce",
        region: "RU",
        device: "PH",
        tiers: {
            Hardcore: "RLT4",
            Diamond: "RHT4",
            RVM: "RHT4"
        }
    },
    {
        name: "_Xx_deras_xX",
        region: "UA",
        device: "PH",
        tiers: {
            "Emerald Pot": "LT2",
            SMP: "LT2",
            Hardcore: "LT2",
            Pickaxe: "LT3",
            RVM: "LT2",
            Emerald: "LT1",
            Dragonhide: "LT2",
            Beast: "LT1",
            Combo: "HT2",
            Gapple: "LT2",
            Mace: "LT1",
            Crystal: "HT2",
            "Diamond Pot": "HT2"
        }
    },
    {
        name: "2b2tPE",
        region: "KG",
        device: "PH",
        tiers: {
            Dragonhide: "HT2",
            RVM: "LT2",
            Emerald: "LT3",
            Hardcore: "HT3",
            "Emerald Pot": "HT3",
            Beast: "LT1",
            "Diamond Pot": "LT2",
            Mace: "LT2",
            SMP: "HT4"
        }
    },
    {
        name: "The_FV4005",
        region: "RU",
        device: "PH",
        tiers: {
            Emerald: "LT3",
            Hardcore: "HT4",
            SMP: "LT4",
            RVM: "LT3",
            "Emerald Pot": "HT4",
            Pickaxe: "LT3",
            "Diamond Pot": "LT3",
            Dragonhide: "LT3",
            Beast: "LT3",
            Crystal: "HT4",
            Mace: "HT4",
            Gapple: "LT3",
            Combo: "LT3"
        }
    },
    {
        name: "YouTube_ggs",
        region: "RU",
        device: "TB",
        tiers: {
            Crystal: "RHT5",
            Mace: "RLT5"
        }
    },
    {
        name: "iuqqkdkq",
        region: "RU",
        device: "PH",
        tiers: {
            Crystal: "RLT3"
        }
    },
    {
        name: "Master",
        region: "RU",
        device: "PH",
        tiers: {
            RVM: "LT3",
            Dragonhide: "LT3",
            Mace: "LT3",
            Beast: "LT3",
            "Diamond Pot": "HT3",
            Pickaxe: "LT3",
            Emerald: "HT4",
            SMP: "LT3",
            "Emerald Pot": "LT3",
            Hardcore: "LT3",
            Crystal: "LT3",
            Combo: "LT4",
            Gapple: "HT4"
        }
    },
    {
        name: "Fialka",
        region: "RU",
        device: "PH",
        tiers: {
            RVM: "RLT4"
        }
    },
    {
        name: "Darius",
        region: "UA",
        device: "PH",
        tiers: {
            RVM: "RHT4",
            Beast: "HT5"
        }
    },
    {
        name: "komi_lotik",
        region: "RU",
        device: "PH",
        tiers: {
            RVM: "RLT4"
        }
    },
    {
        name: "OcM_sila",
        region: "RU",
        device: "TB",
        tiers: {
            SMP: "RHT4"
        }
    },
    {
        name: "wkqwd",
        region: "RU",
        device: "PH",
        tiers: {
            "Emerald Pot": "RLT3"
        }
    },
    {
        name: "OcM",
        region: "UA",
        device: "TB",
        tiers: {
            Hardcore: "RHT2",
            Mace: "LT2"
        }
    },
    {
        name: "Say",
        region: "RU",
        device: "PH",
        tiers: {
            RVM: "LT3",
            "Emerald Pot": "LT2"
        }
    },
    {
        name: "ZirtMobile",
        region: "RU",
        device: "TB",
        tiers: {
            RVM: "LT3",
            Dragonhide: "LT2",
            "Emerald Pot": "LT2",
            Mace: "HT3",
            Crystal: "HT4",
            "Diamond Pot": "LT1",
            Beast: "LT2",
            Pickaxe: "LT3",
            Hardcore: "HT2",
            Gapple: "LT2",
            Combo: "LT2",
            SMP: "LT3",
            Emerald: "HT2"
        }
    },
    {
        name: "WezzikBigClop",
        region: "RU",
        device: "PH",
        tiers: {
            RVM: "HT4",
            "Emerald Pot": "HT4",
            Crystal: "LT3",
            SMP: "LT3",
            Dragonhide: "LT3",
            Pickaxe: "LT3",
            Hardcore: "LT3"
        }
    },
    {
        name: "NeXoXoroshy2",
        region: "KG",
        device: "PH",
        tiers: {
            "Emerald Pot": "HT4",
            SMP: "HT4",
            Hardcore: "LT4",
            RVM: "HT4",
            "Diamond Pot": "LT3",
            Dragonhide: "LT3",
            Emerald: "HT4",
            Mace: "LT3",
            Crystal: "LT3",
            Combo: "HT4",
            Gapple: "LT4"
        }
    },
    {
        name: "LEGENDAMETRO",
        region: "RU",
        device: "PH",
        tiers: {
            "Emerald Pot": "HT3",
            Crystal: "LT1",
            Hardcore: "LT3"
        }
    },
    {
        name: "Nikos",
        region: "RU",
        device: "PH",
        tiers: {
            RVM: "HT5",
            "Emerald Pot": "LT4",
            Crystal: "HT5"
        }
    },
    {
        name: "Y-Japan",
        region: "RU",
        device: "TB",
        tiers: {
            Crystal: "LT4",
            Mace: "LT5",
            SMP: "HT5",
            Hardcore: "LT5",
            Beast: "LT4"
        }
    },
    {
        name: "-BaCk-",
        region: "KZ",
        device: "PH",
        tiers: {
            Mace: "LT3",
            Dragonhide: "HT3",
            Beast: "LT3",
            Hardcore: "HT3",
            RVM: "LT3",
            Emerald: "HT3",
            "Diamond Pot": "LT3",
            SMP: "HT4",
            Pickaxe: "HT4",
            Crystal: "HT4"
        }
    },
    {
        name: "Hayzi",
        region: "RU",
        device: "PH",
        tiers: {
            Emerald: "LT5",
            Mace: "LT5",
            Combo: "LT5",
            RVM: "LT5"
        }
    },
    {
        name: "Samaelka",
        region: "RU",
        device: "PH",
        tiers: {
            Dragonhide: "HT4",
            RVM: "LT3",
            Beast: "HT4",
            SMP: "LT3",
            Hardcore: "LT3",
            Mace: "LT3",
            Pickaxe: "HT4",
            "Emerald Pot": "LT3"
        }
    },
    {
        name: "DzIla_EDITS",
        region: "RU",
        device: "TB",
        tiers: {
            Beast: "LT3",
            "Emerald Pot": "LT3",
            SMP: "LT3"
        }
    },
    {
        name: "boy",
        region: "UA",
        device: "PH",
        tiers: {
            Hardcore: "HT4",
            Crystal: "LT3",
            Pickaxe: "LT3",
            Emerald: "HT4",
            Beast: "HT3",
            Dragonhide: "LT3",
            "Emerald Pot": "LT3",
            RVM: "HT4",
            SMP: "HT4",
            "Diamond Pot": "HT4"
        }
    },
    {
        name: "Mirops",
        region: "RU",
        device: "PH",
        tiers: {
            Mace: "HT5",
            Beast: "HT4",
            Emerald: "LT4",
            RVM: "LT5",
            Crystal: "LT4",
            Dragonhide: "HT4"
        }
    },
    {
        name: "blablablublubluble",
        region: "RU",
        device: "PH",
        tiers: {
            Beast: "LT3",
            "Emerald Pot": "LT3",
            Crystal: "LT4",
            Dragonhide: "HT4",
            Diamond: "LT4"
        }
    },
    {
        name: "_-XKakTakX-_",
        region: "RU",
        device: "PH",
        tiers: {
            Dragonhide: "LT4",
            RVM: "LT3",
            Crystal: "LT3",
            Mace: "LT3"
        }
    },
    {
        name: "Igrok355",
        region: "RU",
        device: "PH",
        tiers: {
            Beast: "HT4",
            Emerald: "HT4",
            Dragonhide: "LT3"
        }
    },
    {
        name: "Prosto_oleg100-7",
        region: "RU",
        device: "PH",
        tiers: {
            Crystal: "LT1",
            RVM: "LT3",
            SMP: "LT3",
            "Diamond Pot": "HT3",
            Beast: "LT2",
            Emerald: "HT3",
            Dragonhide: "HT3"
        }
    },
    {
        name: "BossKFC",
        region: "RU",
        device: "PH",
        tiers: {
            Hardcore: "LT3"
        }
    },
    {
        name: "Lolotrack",
        region: "UA",
        device: "PH",
        tiers: {
            Crystal: "HT5",
            Diamond: "HT5"
        }
    },
    {
        name: "Cira",
        region: "RU",
        device: "TB",
        tiers: {
            Hardcore: "LT2",
            "Emerald Pot": "LT1"
        }
    },
    {
        name: "Gggg1029",
        region: "RU",
        device: "PH",
        tiers: {
            Mace: "LT3",
            "Emerald Pot": "HT4",
            Hardcore: "LT3",
            Combo: "HT4",
            RVM: "LT3",
            SMP: "HT4"
        }
    },
    {
        name: "767676_",
        region: "UA",
        device: "PC",
        tiers: {
            Hardcore: "HT3"
        }
    },
    {
        name: "YouTubePvPXelp_999",
        region: "RU",
        device: "PH",
        tiers: {
            SMP: "LT4",
            "Emerald Pot": "LT4"
        }
    },
    {
        name: "Saxapok13373",
        region: "RU",
        device: "PH",
        tiers: {
            SMP: "HT4",
            Mace: "HT4"
        }
    },
    {
        name: "Dzhambulat1322",
        region: "RU",
        device: "PH",
        tiers: {
            RVM: "HT5",
            Mace: "HT5",
            Crystal: "LT4"
        }
    },
    {
        name: "D4rK_S1lA",
        region: "RU",
        device: "PH",
        tiers: {
            Beast: "LT3",
            RVM: "LT3",
            Hardcore: "LT3",
            Mace: "LT3",
            Gapple: "HT4"
        }
    },
    {
        name: "7STARS",
        region: "RU",
        device: "PH",
        tiers: {
            Dragonhide: "LT3",
            RVM: "LT4",
            Hardcore: "HT5",
            SMP: "HT4",
            Mace: "LT4",
            Combo: "LT4",
            Beast: "LT4",
            "Diamond Pot": "LT4",
            Emerald: "LT3",
            Gapple: "LT4",
            "Emerald Pot": "LT3"
        }
    },
    {
        name: "Kenny13",
        region: "RU",
        device: "PH",
        tiers: {
            Hardcore: "HT5",
            Beast: "LT4",
            Mace: "HT4"
        }
    },
    {
        name: "Exponat",
        region: "RU",
        device: "PH",
        tiers: {
            "Emerald Pot": "HT4",
            Gapple: "LT3",
            Crystal: "HT4",
            RVM: "HT4",
            Mace: "LT3"
        }
    },
    {
        name: "Noch",
        region: "RU",
        device: "PH",
        tiers: {
            RVM: "LT3"
        }
    },
    {
        name: "-_-nyschka-_-",
        region: "RU",
        device: "PH",
        tiers: {
            Mace: "LT3"
        }
    },
    {
        name: "Susla",
        region: "RU",
        device: "PH",
        tiers: {
            Mace: "HT4",
            Crystal: "LT4",
            SMP: "HT4"
        }
    },
    {
        name: "rrrr11",
        region: "RU",
        device: "PH",
        tiers: {
            Mace: "LT4",
            Crystal: "LT4"
        }
    },
    {
        name: "hohNagiBator",
        region: "RU",
        device: "PH",
        tiers: {
            Emerald: "LT3"
        }
    },
    {
        name: "Legenda_loytaba",
        region: "RU",
        device: "PH",
        tiers: {
            Hardcore: "LT4",
            Mace: "HT4",
            Crystal: "HT4"
        }
    },
    {
        name: "MAXTY",
        region: "RU",
        device: "PH",
        tiers: {
            RVM: "LT5",
            Emerald: "LT4",
            Beast: "LT4"
        }
    },
    {
        name: "saimon",
        region: "RU",
        device: "PH",
        tiers: {
            Mace: "HT5",
            Hardcore: "LT4"
        }
    },
    {
        name: "Grisha",
        region: "RU",
        device: "PH",
        tiers: {
            Mace: "LT4",
            Crystal: "HT5"
        }
    },
    {
        name: "Meteor",
        region: "UA",
        device: "PH",
        tiers: {
            RVM: "HT4"
        }
    },
    {
        name: "killdoIbaeb4455",
        region: "RU",
        device: "PH",
        tiers: {
            Hardcore: "LT2"
        }
    },
    {
        name: "Sneszok123",
        region: "RU",
        device: "PH",
        tiers: {
            Beast: "HT3",
            Mace: "LT3"
        }
    },
    {
        name: "Aliazo",
        region: "RU",
        device: "PH",
        tiers: {
            Hardcore: "HT5",
            SMP: "HT5"
        }
    },
    {
        name: "gftun",
        region: "RU",
        device: "PH",
        tiers: {
            Dragonhide: "LT4",
            "Emerald Pot": "HT5",
            RVM: "HT5"
        }
    },
    {
        name: "Vex",
        region: "RU",
        device: "PH",
        tiers: {
            Hardcore: "HT3",
            Beast: "LT3",
            "Diamond Pot": "LT3",
            RVM: "HT4",
            Dragonhide: "HT4",
            Mace: "LT3"
        }
    },
    {
        name: "M_E_G_A",
        region: "RU",
        device: "PH",
        tiers: {
            RVM: "LT5"
        }
    },
    {
        name: "JANDELL",
        region: "RU",
        device: "PH",
        tiers: {
            Hardcore: "LT3",
            RVM: "LT3"
        }
    },
    {
        name: "JEAN",
        region: "FR",
        device: "PH",
        tiers: {
            Hardcore: "HT4",
            Beast: "HT5",
            RVM: "LT5"
        }
    },
    {
        name: "Karzer1",
        region: "EU",
        device: "PH",
        tiers: {
            "Emerald Pot": "LT3",
            RVM: "HT4",
            Beast: "LT3",
            Emerald: "LT3",
            Hardcore: "HT3",
            "Diamond Pot": "LT3",
            Crystal: "HT2",
            SMP: "LT3"
        }
    },
    {
        name: "Michael_59k_YT",
        region: "AM",
        device: "PH",
        tiers: {
            Beast: "LT4",
            Mace: "LT4",
            Pickaxe: "LT3"
        }
    },
    {
        name: "Aura",
        region: "RU",
        device: "TB",
        tiers: {
            Hardcore: "LT3",
            Emerald: "LT2",
            Beast: "HT2",
            "Diamond Pot": "HT3",
            SMP: "LT3",
            Dragonhide: "LT3",
            Crystal: "HT3",
            RVM: "HT4",
            "Emerald Pot": "LT3",
            Mace: "LT3",
            Pickaxe: "LT3",
            Combo: "LT3",
            Gapple: "LT3"
        }
    },
    {
        name: "Topor",
        region: "RU",
        device: "TB",
        tiers: {
            "Emerald Pot": "LT3",
            Combo: "LT3",
            SMP: "LT3",
            Hardcore: "HT3"
        }
    },
    {
        name: "MinatoBeast",
        region: "EU",
        device: "PH",
        tiers: {
            RVM: "LT4",
            Beast: "LT4"
        }
    },
    {
        name: "DzIla_EDITSmob",
        region: "RU",
        device: "PH",
        tiers: {
            "Emerald Pot": "LT1",
            "Diamond Pot": "HT2",
            Emerald: "LT1",
            Beast: "LT2",
            RVM: "LT1",
            Hardcore: "LT2",
            Dragonhide: "HT2"
        }
    },
    {
        name: "AMORE",
        region: "UA",
        device: "PH",
        tiers: {
            Hardcore: "LT5"
        }
    },
    {
        name: "h9nto",
        region: "RU",
        device: "PH",
        tiers: {
            Mace: "LT2",
            "Emerald Pot": "LT3",
            RVM: "HT3",
            Beast: "LT2"
        }
    },
    {
        name: "Straight",
        region: "FR",
        device: "PH",
        tiers: {
            Mace: "HT3",
            Dragonhide: "HT4",
            "Diamond Pot": "LT4",
            SMP: "HT5",
            Hardcore: "HT3",
            Emerald: "LT3",
            Crystal: "HT4",
            Beast: "LT4",
            RVM: "LT3",
            Pickaxe: "LT3"
        }
    },
    {
        name: "1641085O8",
        region: "RU",
        device: "PH",
        tiers: {
            "Emerald Pot": "LT2",
            Dragonhide: "LT3"
        }
    },
    {
        name: "heytem_",
        region: "EU",
        device: "PH",
        tiers: {
            "Diamond Pot": "LT4"
        }
    },
    {
        name: "Top",
        region: "UA",
        device: "PH",
        tiers: {
            Hardcore: "LT4",
            "Emerald Pot": "LT4",
            Beast: "HT4",
            Mace: "LT5",
            Dragonhide: "HT5",
            Gapple: "LT4"
        }
    },
    {
        name: "Lpbe",
        region: "EU",
        device: "PH",
        tiers: {
            Emerald: "LT4"
        }
    },
    {
        name: "HAVCHIK",
        region: "UA",
        device: "PH",
        tiers: {
            "Emerald Pot": "LT3"
        }
    },
    {
        name: "Devon",
        region: "EU",
        device: "PH",
        tiers: {
            "Emerald Pot": "HT5"
        }
    },
    {
        name: "Mirage",
        region: "RU",
        device: "PH",
        tiers: {
            "Emerald Pot": "LT3",
            RVM: "HT4"
        }
    },
    {
        name: "-Sorry-",
        region: "RU",
        device: "PH",
        tiers: {
            Mace: "HT4",
            Hardcore: "LT3"
        }
    },
    {
        name: "_MACKA_",
        region: "RU",
        device: "TB",
        tiers: {
            RVM: "HT4"
        }
    },
    {
        name: "Adridri137",
        region: "FR",
        device: "PH",
        tiers: {
            Hardcore: "LT4"
        }
    }
];