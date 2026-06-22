// Официальная база данных игроков MultiCraftCISTiers
const players = [
    {
        name: "Sneger",
        region: "RU",
        device: "PH",
        tiers: {
            "Dragonhide": "RHT1",
            "Emerald": "RLT1",
            "Diamond": "RHT1",
            "RVM": "RHT1",
            "Crystal": "RHT2",
            "Combo": "RLT1",
            "Mace": "RHT1",
            "Hardcore": "RHT2",
            "Emerald Pot": "LT1",
            "SMP": "RLT1"
        }
    },
    {
        name: "-999-",
        region: "RU",
        device: "TB",
        tiers: {
            "Dragonhide": "RLT1",
            "Emerald": "RHT1",
            "Diamond": "RLT1",
            "SMP": "RHT1",
            "Crystal": "LT1",
            "Combo": "RHT1",
            "Mace": "RHT1",
            "Hardcore": "RHT1",
            "Emerald Pot": "LT1",
            "RVM": "RHT1"
        }
    },
    {
        name: "zor1kkqwix",
        region: "RU",
        device: "PH",
        tiers: {
            "Hardcore": "RLT1",
            "SMP": "HT3",
            "Emerald Pot": "HT3",
            "Combo": "HT4",
            "RVM": "HT3",
            "Pickaxe": "HT2",
            "Emerald": "LT3",
            "Diamond": "HT3",
            "Dragonhide": "HT3",
            "Beast": "LT2",
            "Crystal": "HT1",
            "Mace": "LT1",
            "Gapple": "LT3"
        }
    },
    {
        name: "Itz-Fake",
        region: "RU",
        device: "PH",
        tiers: {
            "Hardcore": "RLT4"
        }
    },
    {
        name: "Dev1ce",
        region: "RU",
        device: "PH",
        tiers: {
            "Hardcore": "RLT4",
            "Diamond": "RHT4",
            "RVM": "RHT4"
        }
    },
    {
        name: "_Xx_deras_xX",
        region: "UA",
        device: "PH",
        tiers: {
            "Emerald Pot": "LT2",
            "SMP": "LT2",
            "Hardcore": "LT2",
            "Pickaxe": "HT2",
            "RVM": "LT2",
            "Emerald": "LT1",
            "Dragonhide": "LT2",
            "Beast": "LT1",
            "Combo": "LT3",
            "Gapple": "LT2",
            "Mace": "LT2",
            "Crystal": "LT3",
            "Diamond": "HT2"
        }
    },
    {
        name: "2b2tPE",
        region: "KG",
        device: "PH",
        tiers: {
            "Dragonhide": "RLT3",
            "RVM": "LT2",
            "Emerald": "RHT3",
            "Hardcore": "LT3",
            "Emerald Pot": "LT3",
            "Beast": "LT3",
            "Diamond": "LT3"
        }
    },
    {
        name: "The_FV4005",
        region: "RU",
        device: "PH",
        tiers: {
            "Emerald": "RLT3"
        }
    },
    {
        name: "YouTube_ggs",
        region: "RU",
        device: "TB",
        tiers: {
            "Crystal": "RHT5",
            "Mace": "RLT5"
        }
    },
    {
        name: "iuqqkdkq",
        region: "RU",
        device: "PH",
        tiers: {
            "Crystal": "RLT3"
        }
    },
    {
        name: "Master",
        region: "RU",
        device: "PH",
        tiers: {
            "RVM": "HT4",
            "Dragonhide": "HT4",
            "Mace": "LT3",
            "Beast": "LT3",
            "Diamond": "HT4",
            "Pickaxe": "LT3",
            "Emerald": "HT4"
        }
    },
    {
        name: "Fialka",
        region: "RU",
        device: "PH",
        tiers: {
            "RVM": "RLT4"
        }
    },
    {
        name: "Darius",
        region: "RU",
        device: "PH",
        tiers: {
            "RVM": "RHT4"
        }
    },
    {
        name: "komi_lotik",
        region: "RU",
        device: "PH",
        tiers: {
            "RVM": "RLT4"
        }
    },
    {
        name: "OcM_sila",
        region: "RU",
        device: "TB",
        tiers: {
            "SMP": "RHT4"
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
            "Hardcore": "RHT2",
            "Mace": "LT2"
        }
    },
    {
        name: "Say",
        region: "RU",
        device: "PH",
        tiers: {
            "RVM": "LT3",
            "Emerald Pot": "HT3"
        }
    },
    {
        name: "ZirtMobile",
        region: "RU",
        device: "TB",
        tiers: {
            "RVM": "LT3",
            "Dragonhide": "LT2",
            "Emerald Pot": "LT3",
            "Mace": "LT3",
            "Crystal": "LT4",
            "Diamond Pot": "LT1",
            "Beast": "LT3",
            "Pickaxe": "LT3",
            "Hardcore": "HT3",
            "Gapple": "LT2",
            "Combo": "LT3",
            "SMP": "HT4"
        }
    },
    {
        name: "WezzikBigClop",
        region: "RU",
        device: "PH",
        tiers: {
            "RVM": "LT3",
            "Emerald Pot": "HT4",
            "Crystal": "LT3",
            "SMP": "LT3",
            "Dragonhide": "LT3"
        }
    },
    {
        name: "NeXoXoroshy2",
        region: "KG",
        device: "PH",
        tiers: {
            "Emerald Pot": "HT4",
            "SMP": "HT4",
            "Hardcore": "LT4",
            "RVM": "HT4",
            "Diamond Pot": "LT3",
            "Dragonhide": "LT3",
            "Emerald": "HT4",
            "Mace": "LT3",
            "Crystal": "LT3",
            "Combo": "HT4",
            "Gapple": "LT4"
        }
    },
    {
        name: "LEGENDAMETRO",
        region: "RU",
        device: "PH",
        tiers: {
            "Emerald Pot": "LT3",
            "Crystal": "HT3",
            "Hardcore": "HT4"
        }
    },
    {
        name: "Nikos",
        region: "RU",
        device: "PH",
        tiers: {
            "RVM": "HT5",
            "Emerald Pot": "LT4"
        }
    },
    {
        name: "Y-Japan",
        region: "RU",
        device: "TB",
        tiers: {
            "Crystal": "LT4",
            "Mace": "LT5",
            "SMP": "HT5",
            "Hardcore": "LT5",
            "Beast": "LT4"
        }
    },
    {
        name: "-BaCk-",
        region: "KZ",
        device: "PH",
        tiers: {
            "Mace": "HT5"
        }
    },
    {
        name: "Hayzi",
        region: "RU",
        device: "PH",
        tiers: {
            "Emerald": "LT5",
            "Mace": "LT5",
            "Combo": "LT5",
            "RVM": "LT5"
        }
    },
    {
        name: "Samaelka",
        region: "RU",
        device: "PH",
        tiers: {
            "Dragonhide": "HT4",
            "RVM": "LT3",
            "Beast": "HT4",
            "SMP": "LT3",
            "Hardcore": "LT3",
            "Mace": "LT3"
        }
    },
    {
        name: "DzIla_EDITS",
        region: "RU",
        device: "TB",
        tiers: {
            "Beast": "LT3",
            "Emerald Pot": "LT3",
            "SMP": "LT3"
        }
    },
    {
        name: "boy",
        region: "UA",
        device: "PH",
        tiers: {
            "Hardcore": "HT4",
            "Crystal": "LT3"
        }
    },
    {
        name: "Mirops",
        region: "RU",
        device: "PH",
        tiers: {
            "Mace": "HT5",
            "Beast": "HT4",
            "Emerald": "LT4",
            "RVM": "LT5",
            "Crystal": "LT4",
            "Dragonhide": "HT4"
        }
    },
    {
        name: "blablablublubluble",
        region: "RU",
        device: "PH",
        tiers: {
            "Beast": "LT3",
            "Emerald Pot": "LT3",
            "Crystal": "LT4",
            "Dragonhide": "HT4"
        }
    },
    {
        name: "_-XKaKTakX-_",
        region: "RU",
        device: "TB",
        tiers: {
            "Dragonhide": "LT3"
        }
    },
    {
        name: "Igrok355",
        region: "RU",
        device: "PH",
        tiers: {
            "Beast": "HT4",
            "Emerald": "HT4",
            "Dragonhide": "LT3"
        }
    },
    {
        name: "Prosto_oleg100-7",
        region: "RU",
        device: "PH",
        tiers: {
            "Hardcore": "LT3",
            "Crystal": "LT1"
        }
    },
    {
        name: "BossKFC",
        region: "RU",
        device: "PH",
        tiers: {
            "Hardcore": "LT3"
        }
    },
    {
        name: "Lolotrack",
        region: "UA",
        device: "PH",
        tiers: {
            "Crystal": "HT5",
            "Diamond": "HT5"
        }
    },
    {
        name: "Cira",
        region: "RU",
        device: "TB",
        tiers: {
            "Hardcore": "LT2"
        }
    },
    {
        name: "Gggg1029",
        region: "RU",
        device: "PH",
        tiers: {
            "Mace": "LT3"
        }
    }
];
