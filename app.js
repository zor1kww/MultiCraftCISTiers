const fallbackData = {
    players: [
        {
            nickname: "Shadow",
            country: "RU",
            device: "Phone",
            tester: "Ares",
            isCoach: true,
            coachPrice: "12$/hour",
            discord: "shadow_pro",
            kits: {
                Vanilla: "HT1",
                Mace: "LT1",
                Sword: "HT2",
                Axe: "HT1",
                UHC: "HT2",
                Pot: "LT1",
                NethOP: "HT3"
            }
        },
        {
            nickname: "Berserk",
            country: "UA",
            device: "PC",
            tester: "Vortex",
            isCoach: false,
            coachPrice: "",
            discord: "",
            kits: {
                Vanilla: "HT2",
                Mace: "HT3",
                Sword: "HT1",
                Axe: "LT1",
                UHC: "HT2",
                Pot: "HT1",
                NethOP: "LT2"
            }
        },
        {
            nickname: "Nomad",
            country: "KZ",
            device: "Tablet",
            tester: "Reaper",
            isCoach: false,
            coachPrice: "",
            discord: "",
            kits: {
                Vanilla: "LT2",
                Mace: "HT4",
                Sword: "LT1",
                Axe: "HT3",
                UHC: "HT2",
                Pot: "Unranked",
                NethOP: "LT3"
            }
        },
        {
            nickname: "Inferno",
            country: "AM",
            device: "Otg",
            tester: "Ares",
            isCoach: true,
            coachPrice: "20$/hour",
            discord: "inferno_yt",
            kits: {
                Vanilla: "HT1",
                Mace: "HT1",
                Sword: "HT1",
                Axe: "HT2",
                UHC: "HT1",
                Pot: "HT2",
                NethOP: "HT1"
            }
        }
    ],

    honors: [
        {
            nickname: "LegendX",
            country: "RU",
            description: "Легендарный игрок СНГ сцены MultiCraft. Организовывал турниры и помогал развитию PvP-комьюнити."
        },
        {
            nickname: "DarkBlade",
            country: "UA",
            description: "Известный Sword и UHC дуэлянт ранней эпохи MultiCraft."
        }
    ],

    testers: [
        {
            nickname: "Ares",
            discord: "ares_admin",
            kits: ["Vanilla", "Sword", "Pot"]
        },
        {
            nickname: "Vortex",
            discord: "vortex_ranker",
            kits: ["Mace", "UHC", "NethOP"]
        },
        {
            nickname: "Reaper",
            discord: "reaper_mc",
            kits: ["Axe", "Vanilla", "Mace"]
        }
    ]
};

let database = fallbackData;

const leaderboardBody = document.getElementById("leaderboardBody");
const honorsContainer = document.getElementById("honorsContainer");
const testersContainer = document.getElementById("testersContainer");

const searchInput = document.getElementById("searchInput");
const countryFilter = document.getElementById("countryFilter");
const kitFilter = document.getElementById("kitFilter");
const deviceFilter = document.getElementById("deviceFilter");

async function loadData() {

    try {

        const response = await fetch("./data.json");

        if (!response.ok) {
            throw new Error("JSON load error");
        }

        const jsonData = await response.json();

        if (jsonData) {
            database = jsonData;
        }

    } catch (error) {

        console.warn("Не удалось загрузить data.json");
        console.warn("Используется fallbackData");

        database = fallbackData;
    }

    renderLeaderboard(database.players || []);
    renderHonors(database.honors || []);
    renderTesters(database.testers || []);
}

function getTierClass(tier) {

    if (!tier) {
        return "text-zinc-500";
    }

    if (tier === "HT1") {
        return "text-yellow-300 font-black";
    }

    if (tier === "LT1") {
        return "text-orange-300 font-bold";
    }

    if (tier.includes("HT")) {
        return "text-red-300";
    }

    if (tier.includes("LT")) {
        return "text-zinc-300";
    }

    return "text-zinc-500";
}

function createKitCell(kitName, tier) {

    return `
        <td class="p-4">
            <div class="flex items-center gap-2">

                <img
                    src="assets/items/${kitName.toLowerCase()}.png"
                    class="w-6 h-6"
                    onerror="this.src='assets/items/vanilla.png'"
                >

                <span class="${getTierClass(tier)}">
                    ${tier || "Unranked"}
                </span>

            </div>
        </td>
    `;
}

function renderLeaderboard(players) {

    leaderboardBody.innerHTML = "";

    if (!players.length) {

        leaderboardBody.innerHTML = `
            <tr>
                <td colspan="11" class="p-10 text-center text-zinc-400">
                    Игроки пока отсутствуют.
                </td>
            </tr>
        `;

        return;
    }

    players.forEach(player => {

        const row = document.createElement("tr");

        row.className = `
            hover-row
            transition-all
            duration-300
            border-b
            border-white/5
        `;

        row.innerHTML = `
            <td class="p-4">

                <div class="flex items-center gap-3">

                    <img
                        src="assets/skins/${player.nickname}.png"
                        class="w-12 h-12 rounded-xl border border-orange-500/30"
                        onerror="this.src='assets/skins/default.png'"
                    >

                    <div>

                        <div class="font-black flex items-center gap-2">

                            ${player.nickname}

                            ${
                                player.isCoach
                                    ? `
                                    <span class="bg-orange-500 text-black text-xs px-2 py-1 rounded-lg">
                                        COACH
                                    </span>
                                    `
                                    : ""
                            }

                        </div>

                        ${
                            player.isCoach
                                ? `
                                <div class="text-xs text-orange-300">
                                    ${player.coachPrice} • ${player.discord}
                                </div>
                                `
                                : ""
                        }

                    </div>

                </div>

            </td>

            <td class="p-4">${player.country}</td>
            <td class="p-4">${player.device}</td>
            <td class="p-4">${player.tester}</td>

            ${createKitCell("Vanilla", player.kits?.Vanilla)}
            ${createKitCell("Mace", player.kits?.Mace)}
            ${createKitCell("Sword", player.kits?.Sword)}
            ${createKitCell("Axe", player.kits?.Axe)}
            ${createKitCell("UHC", player.kits?.UHC)}
            ${createKitCell("Pot", player.kits?.Pot)}
            ${createKitCell("NethOP", player.kits?.NethOP)}
        `;

        leaderboardBody.appendChild(row);
    });
}

function renderHonors(honors) {

    honorsContainer.innerHTML = "";

    if (!honors.length) {

        honorsContainer.innerHTML = `
            <div class="glass rounded-2xl p-8 text-center text-zinc-400">
                Доска почета пока пуста.
            </div>
        `;

        return;
    }

    honors.forEach(player => {

        const card = document.createElement("div");

        card.className = `
            glass
            rounded-2xl
            p-6
            tier-glow
            transition-all
            duration-300
            hover:-translate-y-1
        `;

        card.innerHTML = `
            <div class="flex items-center gap-4">

                <img
                    src="assets/skins/${player.nickname}.png"
                    class="w-20 h-20 rounded-2xl border border-yellow-500/30"
                    onerror="this.src='assets/skins/default.png'"
                >

                <div>

                    <h3 class="text-2xl font-black text-yellow-300">
                        ${player.nickname}
                    </h3>

                    <p class="text-orange-300">
                        ${player.country}
                    </p>

                </div>

            </div>

            <p class="mt-5 text-zinc-300 leading-7">
                ${player.description}
            </p>
        `;

        honorsContainer.appendChild(card);
    });
}

function renderTesters(testers) {

    testersContainer.innerHTML = "";

    if (!testers.length) {

        testersContainer.innerHTML = `
            <div class="glass rounded-2xl p-8 text-center text-zinc-400">
                Официальные тир-тестеры пока не назначены.
            </div>
        `;

        return;
    }

    testers.forEach(tester => {

        const card = document.createElement("div");

        card.className = `
            glass
            rounded-2xl
            p-6
            transition-all
            duration-300
            hover:-translate-y-1
            hover:border-orange-500/40
        `;

        card.innerHTML = `
            <h3 class="text-2xl font-black text-orange-300">
                ${tester.nickname}
            </h3>

            <p class="text-zinc-400 mt-2">
                Discord: ${tester.discord}
            </p>

            <div class="mt-5 flex flex-wrap gap-2">

                ${tester.kits.map(kit => `
                    <span class="bg-orange-500/15 border border-orange-500/30 px-3 py-1 rounded-lg text-sm">
                        ${kit}
                    </span>
                `).join("")}

            </div>
        `;

        testersContainer.appendChild(card);
    });
}

function applyFilters() {

    const search = searchInput.value.toLowerCase();
    const country = countryFilter.value;
    const kit = kitFilter.value;
    const device = deviceFilter.value;

    const filteredPlayers = database.players.filter(player => {

        const matchSearch =
            player.nickname.toLowerCase().includes(search);

        const matchCountry =
            !country || player.country === country;

        const matchDevice =
            !device || player.device === device;

        const matchKit =
            !kit || player.kits[kit] !== "Unranked";

        return (
            matchSearch &&
            matchCountry &&
            matchDevice &&
            matchKit
        );
    });

    renderLeaderboard(filteredPlayers);
}

searchInput.addEventListener("input", applyFilters);
countryFilter.addEventListener("change", applyFilters);
kitFilter.addEventListener("change", applyFilters);
deviceFilter.addEventListener("change", applyFilters);

const tabButtons = document.querySelectorAll(".tab-btn");

tabButtons.forEach(button => {

    button.addEventListener("click", () => {

        tabButtons.forEach(btn => {
            btn.classList.remove("active-tab");
            btn.classList.add("glass");
        });

        button.classList.add("active-tab");

        document.getElementById("leaderboardTab").classList.add("hidden");
        document.getElementById("honorsTab").classList.add("hidden");
        document.getElementById("testersTab").classList.add("hidden");
        document.getElementById("guideTab").classList.add("hidden");

        const tabName = button.dataset.tab;

        document
            .getElementById(tabName + "Tab")
            .classList.remove("hidden");
    });
});

loadData();
