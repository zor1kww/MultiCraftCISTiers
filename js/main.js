// Звуковое сопровождение интерфейса
const clickSound = new Audio('assets/sounds/click.mp3');
function playInterfaceClick() {
    clickSound.currentTime = 0;
    clickSound.play().catch(err => {});
}

// Глобальный слушатель кликов для эффекта нажатия кнопок
document.addEventListener('click', (e) => {
    const t = e.target;
    if (
        t.tagName === 'BUTTON' || 
        t.tagName === 'A' || 
        t.tagName === 'SELECT' || 
        t.tagName === 'INPUT' ||
        t.closest('.player-card-row') ||
        t.closest('.sidebar a')
    ) {
        playInterfaceClick();
    }
});

// Переключение тем оформления (Dark/Light)
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const targetTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', targetTheme);
    const btn = document.getElementById('themeToggleBtn');
    if (btn) {
        btn.innerHTML = targetTheme === 'light' ? '🌙 Темная тема' : '☀️ Светлая тема';
    }
}

// Хелпер для определения, является ли конкретный кит игрока "Retired"
function isKitRetired(player, kit) {
    if (player.retired === true) return true;
    const kitData = player.tiers[kit];
    if (!kitData) return false;
    
    if (typeof kitData === 'object' && kitData.retired === true) {
        return true;
    }
    if (typeof kitData === 'string' && kitData.startsWith('R') && kitData.length > 2) {
        return true;
    }
    return false;
}

// Проверка: есть ли у игрока ХОТЯ БЫ ОДИН кит со статусом retired
function hasAnyRetiredKit(player) {
    if (player.retired === true) return true;
    const allKits = [...maintiers, ...subtiers];
    for (let i = 0; i < allKits.length; i++) {
        if (isKitRetired(player, allKits[i])) {
            const tier = getCleanTier(player, allKits[i]);
            if (tier !== "Unranked") {
                return true;
            }
        }
    }
    return false;
}

// Хелпер для получения чистого названия тира (без префикса R)
function getCleanTier(player, kit) {
    const kitData = player.tiers[kit];
    if (!kitData) return "Unranked";
    if (typeof kitData === 'object') {
        return kitData.tier || "Unranked";
    }
    if (typeof kitData === 'string') {
        if (kitData.startsWith('R') && kitData.length > 2) {
            return kitData.substring(1);
        }
        return kitData;
    }
    return "Unranked";
}

// Расчет общих очков игрока по массиву китов с учетом индивидуального/глобального Retired-статуса
function calcPoints(player, kits) {
    let total = 0;
    const showRetiredInPlace = document.getElementById('retiredToggle') ? document.getElementById('retiredToggle').checked : true;
    kits.forEach(kit => {
        if (!showRetiredInPlace && isKitRetired(player, kit)) {
            return;
        }
        const tier = getCleanTier(player, kit);
        total += tierPoints[tier] || 0;
    });
    return total;
}

// Генерация HTML-бейдж-тиров
function getTierBadge(tier, appendR = false) {
    const color = tierColors[tier] || '#fff';
    const displayLabel = appendR && tier !== "Unranked" ? `R${tier}` : tier;
    return `<span class="tier-badge" style="color: ${color}; border: 1px solid ${color}44; background: ${color}11;">${displayLabel}</span>`;
}

// Открытие детального профиля игрока в модальном окне
function openProfile(idx, filteredPlayersJSON) {
    const localFiltered = JSON.parse(decodeURIComponent(filteredPlayersJSON));
    const player = localFiltered[idx];
    document.getElementById('modalPlayerName').innerHTML = player.name;
    let metaText = `${player.region} ${player.device}`;
    if (hasAnyRetiredKit(player)) {
        metaText += ` RETIRED`;
    }
    document.getElementById('modalPlayerMeta').innerText = metaText;
    const roleContainer = document.getElementById('modalRoleContainer');
    if (player.name === "-999-" || player.name === "zor1kkqwix" || player.name === "Sneger") {
        roleContainer.innerHTML = `<span class="custom-role-badge">Tier-Tester</span>`;
    } else {
        roleContainer.innerHTML = '';
    }
    const mainRows = document.getElementById('modalMainRows');
    const subRows = document.getElementById('modalSubRows');
    
    mainRows.innerHTML = maintiers.map(kit => {
        const t = getCleanTier(player, kit);
        const iconSrc = kitImages[kit] || "";
        const ret = isKitRetired(player, kit);
        return `<div class="modal-row" style="${ret ? 'opacity:0.6;' : ''}">
            <div class="modal-kit-left">
                <img class="modal-kit-icon" src="${iconSrc}" onerror="this.style.opacity='0'" alt="">
                <span class="m-kit">${kit}</span>
            </div>
            <div class="m-right-side">
                ${getTierBadge(t, ret)}
                <span class="m-pts-box">(${tierPoints[t]} PTS)</span>
            </div>
        </div>`;
    }).join('');
    
    subRows.innerHTML = subtiers.map(kit => {
        const t = getCleanTier(player, kit);
        const iconSrc = kitImages[kit] || "";
        const ret = isKitRetired(player, kit);
        return `<div class="modal-row" style="${ret ? 'opacity:0.6;' : ''}">
            <div class="modal-kit-left">
                <img class="modal-kit-icon" src="${iconSrc}" onerror="this.style.opacity='0'" alt="">
                <span class="m-kit">${kit}</span>
            </div>
            <div class="m-right-side">
                ${getTierBadge(t, ret)}
                <span class="m-pts-box">(${tierPoints[t]} PTS)</span>
            </div>
        </div>`;
    }).join('');
    
    document.getElementById('modalMainTotal').innerText = `Всего за Main: ${calcPoints(player, maintiers)} PTS`;
    document.getElementById('modalSubTotal').innerText = `Всего за Sub: ${calcPoints(player, subtiers)} PTS`;
    document.getElementById('profileModal').classList.add('active');
}

// Закрытие модального окна профиля
function closeModal() {
    document.getElementById('profileModal').classList.remove('active');
}

// Навигация по табам страниц
function switchTab(tabId) {
    const tabs = ['mainPage', 'wikiTab', 'hallTab', 'infoCenterTab'];
    tabs.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = (id === tabId) ? 'block' : 'none';
    });
    const sidebar = document.getElementById('sidebar');
    if (sidebar) sidebar.classList.remove('active');
}

function backHome() {
    switchTab('mainPage');
}

// Навигация по под-вкладкам страницы информации
function switchInfoSubTab(subTabId, btnEl) {
    const subTabs = ['tierTestSubTab', 'ptsSubTab', 'testersSubTab', 'rulesSubTab', 'faqSubTab'];
    subTabs.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = (id === subTabId) ? 'block' : 'none';
    });
    const buttons = document.querySelectorAll('.info-nav-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    if (btnEl) btnEl.classList.add('active');
}

// Главная функция рендеринга и фильтрации списка игроков
function renderPlayers() {
    const list = document.getElementById('playersList');
    if (!list) return;
    
    const search = document.getElementById('searchInput').value.toLowerCase();
    const region = document.getElementById('regionFilter').value;
    const device = document.getElementById('deviceFilter').value;
    const targetKit = document.getElementById('kitFilter').value;
    const showRetiredInPlace = document.getElementById('retiredToggle').checked;
    
    if (typeof players === 'undefined' || !Array.isArray(players)) {
        list.innerHTML = `<div style="text-align:center;color:#ffcc47;padding:40px;">Загрузка базы данных игроков...</div>`;
        return;
    }
    
    if (targetKit === 'all') {
        document.getElementById('leaderboardTitle').innerText = "OVERALL PVP TOP";
        document.getElementById('tableSubtitle').innerText = "OVERALL LEADERBOARD";
    } else {
        document.getElementById('leaderboardTitle').innerText = `${targetKit.toUpperCase()} TOP`;
        document.getElementById('tableSubtitle').innerText = `${targetKit.toUpperCase()} LEADERBOARD`;
    }
    
    let filtered = players.filter(player => {
        const matchesSearch = player.name.toLowerCase().includes(search);
        const matchesRegion = (region === 'all' || player.region === region);
        const matchesDevice = (device === 'all' || player.device === device);
        
        if (targetKit !== 'all') {
            const tier = getCleanTier(player, targetKit);
            const ret = isKitRetired(player, targetKit);
            if (!showRetiredInPlace && ret) {
                return false;
            }
            return matchesSearch && matchesRegion && matchesDevice && tier !== "Unranked";
        }
        
        if (!showRetiredInPlace) {
            let hasActiveMainKit = false;
            maintiers.forEach(k => {
                if (getCleanTier(player, k) !== "Unranked" && !isKitRetired(player, k)) {
                    hasActiveMainKit = true;
                }
            });
            if (!hasActiveMainKit) return false;
        }
        return matchesSearch && matchesRegion && matchesDevice;
    });
    
    if (targetKit === 'all') {
        filtered.sort((a, b) => {
            return calcPoints(b, maintiers) - calcPoints(a, maintiers);
        });
    } else {
        filtered.sort((a, b) => {
            const tierA = getCleanTier(a, targetKit);
            const tierB = getCleanTier(b, targetKit);
            return (tierPoints[tierB] || 0) - (tierPoints[tierA] || 0);
        });
    }
    
    if (filtered.length === 0) {
        list.innerHTML = `<div style="text-align:center;color:var(--text-muted);padding:40px;">Игроки не найдены</div>`;
        return;
    }
    
    const encodedData = encodeURIComponent(JSON.stringify(filtered));
    
    list.innerHTML = filtered.map((player, index) => {
        const isGlobalRet = player.retired === true;
        let totalPts = 0;
        let tierDisplayHtml = "";
        
        if (targetKit === 'all') {
            totalPts = calcPoints(player, maintiers);
            const activeMainKits = maintiers.filter(k => getCleanTier(player, k) !== "Unranked");
            tierDisplayHtml = `<span style="color:var(--text-muted);font-size:13px;">Kits: ${activeMainKits.length}</span>`;
        } else {
            const cleanT = getCleanTier(player, targetKit);
            totalPts = tierPoints[cleanT] || 0;
            const kitRet = isKitRetired(player, targetKit);
            tierDisplayHtml = getTierBadge(cleanT, kitRet);
        }
        
        return `<div class="player-card-row" style="${isGlobalRet ? 'opacity:0.55;' : ''}" onclick="openProfile(${index}, '${encodedData}')">
            <div class="p-rank-box">#${index + 1}</div>
            <div class="p-info-box">
                <div class="p-name">${player.name}</div>
                <div class="p-meta">${player.region} • ${player.device}</div>
            </div>
            <div class="p-tiers-box">
                ${tierDisplayHtml}
            </div>
            <div class="p-pts-box">${totalPts} PTS</div>
        </div>`;
    }).join('');
}

// Заполнение таблицы распределения очков в FAQ
function initFaqTable() {
    const tbody = document.getElementById('faqTableBody');
    if (!tbody) return;
    const sortedTiers = Object.keys(tierPoints).filter(t => t !== 'Unranked');
    tbody.innerHTML = sortedTiers.map(t => {
        const color = tierColors[t] || '#fff';
        return `<tr>
            <td style="color: ${color}; font-weight: bold;">${t}</td>
            <td>${tierPoints[t]} PTS</td>
        </tr>`;
    }).join('');
}

// Раскраска уровней в тексте FAQ
function colorizeFaqText() {
    const mapping = {
        'faqColorLT3_1': 'LT3', 'faqColorLT3_2': 'LT3', 'faqColorLT3_3': 'LT3', 'faqColorLT3_4': 'LT3',
        'faqColorLT2_1': 'LT2',
        'faqColorHT2_1': 'HT2',
        'faqColorHT1_1': 'HT1', 'faqColorHT1_2': 'HT1', 'faqColorHT1_3': 'HT1', 'faqColorHT1_4': 'HT1',
        'faqColorLT1_1': 'LT1', 'faqColorLT1_2': 'LT1', 'faqColorLT1_3': 'LT1'
    };
    for (let id in mapping) {
        const el = document.getElementById(id);
        if (el) {
            const tier = mapping[id];
            el.style.color = tierColors[tier] || 'inherit';
            el.style.fontWeight = 'bold';
        }
    }
}

// Логика открытия/закрытия бокового меню на мобильных устройствах
function initSidebarToggle() {
    const menuBtn = document.getElementById('menuBtn');
    const sidebar = document.getElementById('sidebar');
    if (menuBtn && sidebar) {
        menuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('active');
        });
        document.addEventListener('click', (e) => {
            if (!sidebar.contains(e.target) && sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
            }
        });
    }
}

// Точка входа инициализации данных
function initSite() {
    initFaqTable();
    colorizeFaqText();
    initSidebarToggle();
    
    const searchInp = document.getElementById('searchInput');
    const kitSel = document.getElementById('kitFilter');
    const regSel = document.getElementById('regionFilter');
    const devSel = document.getElementById('deviceFilter');
    const retTgl = document.getElementById('retiredToggle');
    
    if (searchInp) searchInp.addEventListener('input', renderPlayers);
    if (kitSel) kitSel.addEventListener('change', renderPlayers);
    if (regSel) regSel.addEventListener('change', renderPlayers);
    if (devSel) devSel.addEventListener('change', renderPlayers);
    if (retTgl) retTgl.addEventListener('change', renderPlayers);
    
    renderPlayers();
}