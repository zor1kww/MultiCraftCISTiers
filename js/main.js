// Основная инициализация сайта
function initSite() {
    calculatePlayersPTS();
    renderLeaderboard();
    renderTesters();
    renderWiki();
    setupFilters();
}

// Подсчет PTS игроков на основе конфигурации
function calculatePlayersPTS() {
    players.forEach(player => {
        let total = 0;
        Object.keys(player.tiers).forEach(kit => {
            const tier = player.tiers[kit];
            if (CONFIG.ptsValues[tier]) {
                total += CONFIG.ptsValues[tier];
            }
        });
        player.totalPTS = total;
    });
}

// Рендеринг таблицы лидеров с динамическим добавлением свечений ТОП 1-5
function renderLeaderboard() {
    const container = document.getElementById('leaderboard-container'); // или твой ID списка
    if (!container) return;

    const searchVal = document.getElementById('search-input')?.value.toLowerCase() || "";
    const kitFilter = document.getElementById('kit-filter')?.value || "Overall";
    const regionFilter = document.getElementById('region-filter')?.value || "All";
    const deviceFilter = document.getElementById('device-filter')?.value || "All";
    const showRetired = document.getElementById('retired-checkbox')?.checked ?? true;

    // Сортировка и фильтрация
    let filtered = [...players];

    if (kitFilter !== "Overall") {
        filtered = filtered.filter(p => p.tiers[kitFilter] && p.tiers[kitFilter] !== "Unranked");
        filtered.sort((a, b) => CONFIG.ptsValues[b.tiers[kitFilter]] - CONFIG.ptsValues[a.tiers[kitFilter]]);
    } else {
        filtered.sort((a, b) => b.totalPTS - a.totalPTS);
    }

    if (searchVal) filtered = filtered.filter(p => p.name.toLowerCase().includes(searchVal));
    if (regionFilter !== "All") filtered = filtered.filter(p => p.region === regionFilter);
    if (deviceFilter !== "All") filtered = filtered.filter(p => p.device === deviceFilter);
    if (!showRetired) filtered = filtered.filter(p => !p.retired);

    container.innerHTML = "";

    filtered.forEach((player, index) => {
        const card = document.createElement('div');
        card.className = 'player-card';
        
        // ПУНКТ 4: Добавляем свечение ТОП 1-5 на абсолютно любом выбранном режиме!
        if (index === 0) card.classList.add('top1');
        else if (index === 1) card.classList.add('top2');
        else if (index === 2) card.classList.add('top3');
        else if (index === 3) card.classList.add('top4');
        else if (index === 4) card.classList.add('top5');

        // Логика отображения тиров в карточке
        let scoreDisplay = kitFilter === "Overall" ? `${player.totalPTS} PTS` : player.tiers[kitFilter];
        
        card.innerHTML = `
            <div class="player-info">
                <span class="rank-number">#${index + 1}</span>
                <span class="player-name">${player.name} ${player.retired ? '<span class="retired-tag">RETIRED</span>' : ''}</span>
            </div>
            <div class="player-stats">
                <span class="player-meta">${player.region} | ${player.device}</span>
                <span class="player-score">${scoreDisplay}</span>
            </div>
        `;
        container.appendChild(card);
    });
}

// ПУНКТ 2: Рендеринг тестеров с разделением на Старших и Квалификационных
function renderTesters() {
    const container = document.getElementById('testers-list-container');
    if (!container) return;

    container.innerHTML = `
        <div class="staff-section">
            <h3 class="staff-role-title">Старшие Тестеры</h3>
            <div id="senior-testers" class="testers-grid"></div>
        </div>
        <div class="staff-section" style="margin-top: 20px;">
            <h3 class="staff-role-title">Квалификационные Тестеры</h3>
            <div id="qualifying-testers" class="testers-grid"></div>
        </div>
    `;

    // Выводим Старших
    const seniorBlock = document.getElementById('senior-testers');
    CONFIG.staff.seniorTesters.forEach(name => {
        seniorBlock.innerHTML += createTesterCard(name);
    });

    // Выводим Квалификационных
    const qualBlock = document.getElementById('qualifying-testers');
    CONFIG.staff.qualifyingTesters.forEach(name => {
        qualBlock.innerHTML += createTesterCard(name);
    });
}

function createTesterCard(name) {
    // Внутри профиля плашка остается стандартной по ТЗ: Tier-Tester
    return `
        <div class="tester-card">
            <span class="tester-name">${name}</span>
            <span class="tester-badge">Tier-Tester</span>
        </div>
    `;
}

// ПУНКТ 3: Рендеринг Вики с иконками слева от названий китов
function renderWiki() {
    const container = document.getElementById('wiki-list-container');
    if (!container) return;

    container.innerHTML = "";

    Object.keys(CONFIG.kits).forEach(kitKey => {
        const kit = CONFIG.kits[kitKey];
        const desc = CONFIG.wikiDescriptions[kitKey] || "Описание режима готовится к публикации.";
        
        // Генерируем название для файла скриншота инвентаря
        const imgName = kitKey.toLowerCase().replace(/ /g, "_") + "_inv.png";

        const wikiCard = document.createElement('div');
        wikiCard.className = 'wiki-card';
        wikiCard.innerHTML = `
            <div class="wiki-header-container">
                <img src="${kit.icon}" class="wiki-kit-icon" alt="${kitKey}">
                <h3>${kit.displayName}</h3>
            </div>
            <p class="wiki-text">${desc}</p>
            <div class="wiki-inv-preview">
                <img src="assets/wiki/${imgName}" onerror="this.parentElement.innerHTML='<div class=\"no-img\">[Скриншот инвентаря ${kitKey}]</div>'" alt="Инвентарь ${kitKey}">
            </div>
        `;
        container.appendChild(wikiCard);
    });
}

// Функция переключения вкладок/экранов сайта
function switchScreen(screenId) {
    document.querySelectorAll('.screen-content').forEach(el => el.classList.add('hidden'));
    const activeScreen = document.getElementById(`${screenId}-screen`);
    if (activeScreen) activeScreen.classList.remove('hidden');
}

// Настройка слушателей событий для фильтров
function setupFilters() {
    document.getElementById('search-input')?.addEventListener('input', renderLeaderboard);
    document.getElementById('kit-filter')?.addEventListener('change', renderLeaderboard);
    document.getElementById('region-filter')?.addEventListener('change', renderLeaderboard);
    document.getElementById('device-filter')?.addEventListener('change', renderLeaderboard);
    document.getElementById('retired-checkbox')?.addEventListener('change', renderLeaderboard);
}
