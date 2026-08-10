// Официальная база данных игроков MultiCraftCISTiers (Финальная версия)
const players = [
    {
        name: "Sneger",
        region: "RU",
        tiers: {
            Crystal: "LT1",
            Mace: "HT1",
            Hardcore: "HT2",
            "Emerald Pot": "LT1",
            Beast: "HT1",
            Pickaxe: "LT1",
            Emerald: "HT1",
            "Diamond Pot": "LT1"
        }
    },
    {
        name: "-999-",
        region: "RU",
        tiers: {
            Dragonhide: "RLT1",
            Emerald: "RHT1",
            "Diamond Pot": "RLT1",
            SMP: "RHT1",
            Crystal: "LT1",
            Combo: "RHT1",
            Mace: "LT1",
            Hardcore: "HT1",
            "Emerald Pot": "HT1",
            RVM: "RHT1",
            Beast: "LT1",
            Pickaxe: "HT1"
        }
    },
    {
        name: "zor1kkqwix",
        region: "RU",
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
        tiers: {
            Hardcore: "RLT4",
            RVM: "RLT4"
        }
    },
    {
        name: "Dev1ce",
        region: "RU",
        tiers: {
            Hardcore: "RLT4",
            Diamond: "RHT4",
            RVM: "RHT4"
        }
    },
    {
        name: "_Xx_deras_xX",
        region: "UA",
        tiers: {
            "Emerald Pot": "LT2",
            SMP: "LT2",
            Hardcore: "HT2",
            Pickaxe: "HT2",
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
        tiers: {
            Crystal: "RHT5",
            Mace: "RLT5"
        }
    },
    {
        name: "Master",
        region: "RU",
        tiers: {
            RVM: "LT3",
            Dragonhide: "LT3",
            Mace: "LT3",
            Beast: "LT3",
            "Diamond Pot": "HT3",
            Pickaxe: "LT3",
            Emerald: "LT3",
            SMP: "LT3",
            "Emerald Pot": "LT3",
            Hardcore: "LT3",
            Crystal: "LT3",
            Combo: "LT4",
            Gapple: "HT4"
        }
    },
    {
        name: "Darius",
        region: "UA",
        tiers: {
            RVM: "RHT4",
            Beast: "HT5"
        }
    },
    {
        name: "OcM_sila",
        region: "RU",
        tiers: {
            SMP: "RHT4"
        }
    },
    {
        name: "OcM",
        region: "UA",
        tiers: {
            Hardcore: "RHT2",
            Mace: "LT2"
        }
    },
    {
        name: "Say",
        region: "RU",
        tiers: {
            RVM: "LT3",
            "Emerald Pot": "LT2"
        }
    },
    {
        name: "ZirtMobile",
        region: "RU",
        tiers: {
            RVM: "LT3",
            Dragonhide: "LT2",
            "Emerald Pot": "LT2",
            Mace: "HT3",
            Crystal: "HT4",
            "Diamond Pot": "LT1",
            Beast: "HT2",
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
        tiers: {
            RVM: "HT4",
            "Emerald Pot": "HT4",
            Crystal: "HT4",
            SMP: "LT3",
            Dragonhide: "LT3",
            Pickaxe: "LT3",
            Hardcore: "LT3",
            "Diamond Pot": "HT4"
        }
    },
    {
        name: "NeXoXoroshy2",
        region: "KG",
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
        tiers: {
            "Emerald Pot": "HT3",
            Crystal: "LT1",
            Hardcore: "LT3",
            Combo: "LT3"
        }
    },
    {
        name: "Nikos",
        region: "RU",
        tiers: {
            RVM: "HT5",
            "Emerald Pot": "LT4",
            Crystal: "HT5"
        }
    },
    {
        name: "Y-Japan",
        region: "RU",
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
        tiers: {
            Mace: "LT3",
            Dragonhide: "HT3",
            Beast: "HT3",
            Hardcore: "HT3",
            RVM: "LT3",
            Emerald: "HT3",
            "Diamond Pot": "LT3",
            SMP: "LT3",
            Pickaxe: "HT3",
            Crystal: "HT4",
            Gapple: "LT3"
        }
    },
    {
        name: "Hayzi",
        region: "RU",
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
        tiers: {
            Beast: "LT3",
            "Emerald Pot": "LT3",
            SMP: "LT3"
        }
    },
    {
        name: "boy",
        region: "UA",
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
        tiers: {
            Dragonhide: "LT3",
            RVM: "LT3",
            Crystal: "LT3",
            Mace: "LT3",
            SMP: "LT3"
        }
    },
    {
        name: "Igrok355",
        region: "RU",
        tiers: {
            Beast: "HT4",
            Emerald: "HT4",
            Dragonhide: "LT3"
        }
    },
    {
        name: "Prosto_oleg100-7",
        region: "RU",
        tiers: {
            Crystal: "LT1",
            RVM: "LT3",
            SMP: "LT3",
            "Diamond Pot": "HT3",
            Beast: "LT2",
            Emerald: "LT2",
            Dragonhide: "HT3",
            Mace: "LT2",
            "Emerald Pot": "LT3",
            Combo: "LT3",
            Gapple: "LT3",
            Hardcore: "LT3",
            Pickaxe: "LT3"
        }
    },
    {
        name: "BossKFC",
        region: "RU",
        tiers: {
            Hardcore: "LT3"
        }
    },
    {
        name: "Lolotrack",
        region: "UA",
        tiers: {
            Crystal: "HT5",
            Diamond: "HT5"
        }
    },
    {
        name: "Cira",
        region: "RU",
        tiers: {
            Hardcore: "LT2",
            "Emerald Pot": "LT1",
            Mace: "HT2"
        }
    },
    {
        name: "Gggg1029",
        region: "RU",
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
        name: "YouTubePvPXelp_999",
        region: "RU",
        tiers: {
            SMP: "LT4",
            "Emerald Pot": "LT4"
        }
    },
    {
        name: "Saxapok13373",
        region: "RU",
        tiers: {
            SMP: "HT4",
            Mace: "HT4"
        }
    },
    {
        name: "Dzhambulat1322",
        region: "RU",
        tiers: {
            RVM: "HT5",
            Mace: "HT5",
            Crystal: "LT4"
        }
    },
    {
        name: "D4rK_S1lA",
        region: "RU",
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
        tiers: {
            Hardcore: "HT5",
            Beast: "LT4",
            Mace: "HT4"
        }
    },
    {
        name: "Exponat",
        region: "RU",
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
        tiers: {
            RVM: "LT3",
            Crystal: "RLT3",
            "Emerald Pot": "RLT3"
        }
    },
    {
        name: "-_-nyschka-_-",
        region: "RU",
        tiers: {
            Mace: "LT3"
        }
    },
    {
        name: "Susla",
        region: "RU",
        tiers: {
            Mace: "HT4",
            Crystal: "LT4",
            SMP: "HT4"
        }
    },
    {
        name: "rrrr11",
        region: "RU",
        tiers: {
            Mace: "LT4",
            Crystal: "LT4"
        }
    },
    {
        name: "hohNagiBator",
        region: "RU",
        tiers: {
            Emerald: "LT3"
        }
    },
    {
        name: "Legenda_loytaba",
        region: "RU",
        tiers: {
            Hardcore: "LT4",
            Mace: "HT4",
            Crystal: "HT4"
        }
    },
    {
        name: "MAXTY",
        region: "RU",
        tiers: {
            RVM: "LT5",
            Emerald: "LT4",
            Beast: "LT4"
        }
    },
    {
        name: "saimon",
        region: "RU",
        tiers: {
            Mace: "HT5",
            Hardcore: "LT4"
        }
    },
    {
        name: "Grisha",
        region: "RU",
        tiers: {
            Mace: "LT4",
            Crystal: "HT5"
        }
    },
    {
        name: "Meteor",
        region: "UA",
        tiers: {
            RVM: "HT4"
        }
    },
    {
        name: "killdoIbaeb4455",
        region: "RU",
        tiers: {
            Hardcore: "LT2"
        }
    },
    {
        name: "Sneszok123",
        region: "RU",
        tiers: {
            Beast: "HT3",
            Mace: "LT3"
        }
    },
    {
        name: "Aliazo",
        region: "RU",
        tiers: {
            Hardcore: "HT5",
            SMP: "HT5"
        }
    },
    {
        name: "gftun",
        region: "RU",
        tiers: {
            Dragonhide: "LT4",
            "Emerald Pot": "HT5",
            RVM: "HT5"
        }
    },
    {
        name: "Vex",
        region: "RU",
        tiers: {
            Hardcore: "LT2",
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
        tiers: {
            RVM: "LT5"
        }
    },
    {
        name: "JANDELL",
        region: "RU",
        tiers: {
            Hardcore: "LT3",
            RVM: "LT3"
        }
    },
    {
        name: "Michael_59k_YT",
        region: "AM",
        tiers: {
            Beast: "LT4",
            Mace: "LT4",
            Pickaxe: "LT3"
        }
    },
    {
        name: "Aura",
        region: "RU",
        tiers: {
            Hardcore: "HT3",
            Emerald: "LT2",
            Beast: "LT2",
            "Diamond Pot": "HT2",
            SMP: "LT2",
            Dragonhide: "HT3",
            Crystal: "LT3",
            RVM: "LT3",
            "Emerald Pot": "LT3",
            Mace: "LT2",
            Pickaxe: "LT2",
            Combo: "LT2",
            Gapple: "HT3"
        }
    },
    {
        name: "Topor",
        region: "RU",
        tiers: {
            "Emerald Pot": "LT3",
            Combo: "LT3",
            SMP: "LT3",
            Hardcore: "HT3"
        }
    },
    {
        name: "DzIla_EDITSmob",
        region: "RU",
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
        region: "RU",
        tiers: {
            Hardcore: "LT5",
            Beast: "HT5"
        },
        device: "PH"
    },
    {
        name: "h9nto",
        region: "RU",
        tiers: {
            Mace: "LT2",
            "Emerald Pot": "LT3",
            RVM: "HT3",
            Beast: "LT2"
        }
    },
    {
        name: "1641085O8",
        region: "RU",
        tiers: {
            "Emerald Pot": "LT2",
            Dragonhide: "LT3"
        }
    },
    {
        name: "Top",
        region: "UA",
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
        name: "HAVCHIK",
        region: "UA",
        tiers: {
            "Emerald Pot": "LT3"
        }
    },
    {
        name: "Mirage",
        region: "RU",
        tiers: {
            "Emerald Pot": "LT3",
            RVM: "HT4"
        }
    },
    {
        name: "-Sorry-",
        region: "RU",
        tiers: {
            Mace: "HT4",
            Hardcore: "LT3"
        }
    },
    {
        name: "Fialka_",
        region: "RU",
        tiers: {
            SMP: "HT4",
            RVM: "RLT4"
        }
    },
    {
        name: "NOVENKIY1",
        region: "RU",
        tiers: {
            RVM: "LT4"
        }
    },
    {
        name: "zaxvatchik6",
        region: "RU",
        tiers: {
            RVM: "LT5",
            Beast: "LT4",
            Mace: "LT4",
            Crystal: "LT4",
            Hardcore: "LT4"
        }
    },
    {
        name: "-_MACKA_-",
        region: "RU",
        tiers: {
            Dragonhide: "LT3",
            RVM: "HT4"
        }
    },
    {
        name: "Karabasik",
        region: "RU",
        tiers: {
            Dragonhide: "HT4",
            Emerald: "LT3"
        }
    },
    {
        name: "ofofoffo",
        region: "UA",
        tiers: {
            "Emerald Pot": "LT3",
            Mace: "HT4"
        }
    },
    {
        name: "sw3don",
        region: "RU",
        tiers: {
            Hardcore: "LT4",
            Dragonhide: "LT4"
        }
    },
    {
        name: "xivivideking",
        region: "RU",
        tiers: {
            RVM: "LT3",
            Beast: "LT2"
        }
    },
    {
        name: "Yakov",
        region: "RU",
        tiers: {
            RVM: "LT3",
            Dragonhide: "LT3",
            Gapple: "LT3"
        }
    },
    {
        name: "_Dan41k",
        region: "RU",
        tiers: {
            Hardcore: "HT5"
        }
    },
    {
        name: "YTdrumv",
        region: "RU",
        device: "PH",
        tiers: {
            Beast: "LT5",
            Emerald: "LT4",
            Crystal: "LT4",
            Dragonhide: "HT5",
            "Diamond Pot": "HT5",
            Hardcore: "LT5",
            Pickaxe: "HT4",
            Mace: "LT4",
            SMP: "LT4"
        }
    }
];