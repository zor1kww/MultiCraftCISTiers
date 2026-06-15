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
        list.innerHTML = '<div style="text-align:center;color:#ffcc47;padding:40px;">Загрузка базы данных игроков...</div>';
        return;
    }

    if (targetKit === 'all') {
        document.getElementById('leaderboardTitle').innerText = 'OVERALL PVP TOP';
        document.getElementById('tableSubtitle').innerText = 'OVERALL LEADERBOARD';
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

    list.innerHTML = '';
    
    if (filtered.length === 0) {
        list.innerHTML = '<div style="text-align:center;color:#8892b0;padding:20px;">Игроки не найдены</div>';
        return;
    }

    const filteredJSON = encodeURIComponent(JSON.stringify(filtered));
    let htmlFragment = '';

    filtered.forEach((player, index) => {
        let rightColumnContent = '';
        let rankPrefix = `#${index + 1}`; 
        let topClass = '';
        
        if (index === 0) topClass = 'top-rank-1';
        else if (index === 1) topClass = 'top-rank-2';
        else if (index === 2) topClass = 'top-rank-3';
        else if (index === 3) topClass = 'top-rank-4';
        else if (index === 4) topClass = 'top-rank-5';
        
        if (targetKit !== 'all' && isKitRetired(player, targetKit)) {
            topClass = 'retired-status';
        }
        if (targetKit === 'all') {
            let allMainRetired = true;
            maintiers.forEach(k => {
                if (getCleanTier(player, k) !== "Unranked" && !isKitRetired(player, k)) {
                    allMainRetired = false;
                }
            });
            if (allMainRetired) topClass = 'retired-status';
        }
        
        if (targetKit === 'all') {
            const mainPts = calcPoints(player, maintiers);
            rightColumnContent = `<span style="color: var(--accent);">${mainPts} PTS</span>`;
        } else {
            const currentTier = getCleanTier(player, targetKit);
            const ret = isKitRetired(player, targetKit);
            rightColumnContent = getTierBadge(currentTier, ret);
        }

        let quickTiersHTML = '';
        if (targetKit === 'all') {
            // Создаем массив объектов китов текущего игрока, чтобы отсортировать их по весу результата
            let playerKitsObjects = maintiers.map(kit => {
                const tier = getCleanTier(player, kit);
                const ret = isKitRetired(player, kit);
                
                // Рассчитываем приоритет сортировки:
                // 1. Активные киты (сортировка от HT1 к LT5 по количеству PTS)
                // 2. Retired киты (сортировка от RHT1 к RLT5 по количеству PTS)
                // 3. Unranked киты (самый низший приоритет)
                let sortWeight = -1000;
                if (tier !== "Unranked") {
                    const pts = tierPoints[tier] || 0;
                    if (!ret) {
                        sortWeight = pts; // Активный кит: вес от 1000 до 100
                    } else {
                        sortWeight = pts - 5000; // Retired кит: вес от -4000 до -4900
                    }
                } else {
                    sortWeight = -10000; // Unranked кит: минимальный вес
                }
                
                return { kit, tier, ret, sortWeight };
            });

            // Сортировка мейн-китов слева направо (от наибольшего sortWeight к наименьшему)
            playerKitsObjects.sort((a, b) => b.sortWeight - a.sortWeight);

            quickTiersHTML = `<div class="player-tiers-row">`;
            playerKitsObjects.forEach(item => {
                const kit = item.kit;
                const tier = item.tier;
                const ret = item.ret;
                const clr = tierColors[tier] || '#444b66';
                const iconSrc = kitImages[kit] || "";
                const labelText = (ret && tier !== "Unranked") ? `R${tier}` : tier;
                
                if (tier !== "Unranked") {
                    if (!showRetiredInPlace && ret) {
                        quickTiersHTML += `
                        <div class="tier-item-box" style="opacity: 0.25;">
                            <div class="tier-icon-circle unranked">
                                <img src="${iconSrc}" onerror="this.style.opacity=0" alt="">
                            </div>
                            <div class="tier-label-under" style="color: #444b66;">-</div>
                        </div>`;
                    } else {
                        quickTiersHTML += `
                        <div class="tier-item-box" style="${ret ? 'opacity:0.4;' : ''}">
                            <div class="tier-icon-circle" style="border-color: ${clr}cc; box-shadow: 0 0 6px ${clr}22;">
                                <img src="${iconSrc}" onerror="this.style.opacity=0" alt="">
                            </div>
                            <div class="tier-label-under" style="color: ${clr};">${labelText}</div>
                        </div>`;
                    }
                } else {
                    quickTiersHTML += `
                    <div class="tier-item-box">
                        <div class="tier-icon-circle unranked">
                            <img src="${iconSrc}" onerror="this.style.opacity=0" alt="">
                        </div>
                        <div class="tier-label-under" style="color: #444b66;">-</div>
                    </div>`;
                }
            });
            quickTiersHTML += `</div>`;
        }

        // Проверка на вывод тега RETIRED в карточке
        let displayProfileRetiredTag = hasAnyRetiredKit(player);

        htmlFragment += `
        <div class="player-container ${topClass}">
            <div class="player-card-row" onclick="openProfile(${index}, '${filteredJSON}')">
                <div class="player-left">
                    <div class="player-rank">${rankPrefix}</div>
                    <div class="player-name-wrapper">
                        <div class="player-name">${player.name}</div>
                    </div>
                </div>
                <div class="player-center">
                    <div class="player-meta-box">
                        <span class="player-meta-tag">${player.region}</span>
                        <span class="player-meta-tag">${player.device}</span>
                        ${displayProfileRetiredTag ? `<span class="retired-meta-tag">RETIRED</span>` : ''}
                    </div>
                    ${quickTiersHTML}
                </div>
                <div class="player-right">
                    ${rightColumnContent}
                </div>
            </div>
        </div>`;
    });
    
    list.innerHTML = htmlFragment;
}

// Автоматическая сборка таблицы начисления PTS внутри объединенного инфо-центра
function buildFaqTable() {
    const tbody = document.getElementById('faqTableBody');
    if (!tbody) return;
    const order = ['HT1', 'LT1', 'HT2', 'LT2', 'HT3', 'LT3', 'HT4', 'LT4', 'HT5', 'LT5', 'Unranked'];
    tbody.innerHTML = order.map(tier => {
        const color = tierColors[tier];
        return `<tr>
            <td><span class="tier-badge" style="color: ${color}; border: 1px solid ${color}44; background:${color}11;">${tier}</span></td>
            <td><span style="color: var(--accent); font-weight:bold;">${tierPoints[tier]} PTS</span></td>
        </tr>`;
    }).join('');
}

// Навешивание кастомных цветов на тиры внутри FAQ текста
function applyFaqTierColors() {
    const tiersToColor = ['HT1', 'HT2', 'LT1', 'LT2', 'LT3'];
    tiersToColor.forEach(tier => {
        const color = tierColors[tier] || 'var(--accent)';
        // Находим все элементы-заглушки во вкладке FAQ и красим их
        for (let i = 1; i <= 4; i++) {
            const element = document.getElementById(`faqColor${tier}_${i}`);
            if (element) {
                element.style.color = color;
                element.style.fontWeight = 'bold';
            }
        }
    });
}

// Навигация по под-вкладкам внутри Информации
function switchInfoSubTab(subTabId, btnElement) {
    document.querySelectorAll('.info-sub-tab-content').forEach(subTab => {
        subTab.style.display = 'none';
    });
    document.querySelectorAll('.info-nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const targetSubTab = document.getElementById(subTabId);
    if (targetSubTab) {
        targetSubTab.style.display = 'block';
    }
    if (btnElement) {
        btnElement.classList.add('active');
    }
    
    if (subTabId === 'ptsSubTab') {
        buildFaqTable();
    }
    if (subTabId === 'faqSubTab') {
        applyFaqTierColors();
    }
}

// Переключение вкладок (Обновленный роутинг)
function switchTab(tabId) {
    const sb = document.getElementById('sidebar');
    if (sb) sb.classList.remove('active');
    
    const mp = document.getElementById('mainPage');
    if (mp) mp.style.display = 'none';
    
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    
    if (tabId === 'mainPage') {
        if (mp) mp.style.display = 'block';
        renderPlayers();
    } else {
        const target = document.getElementById(tabId);
        if (target) target.style.display = 'block';
        
        if (tabId === 'infoCenterTab') {
            const firstNavBtn = document.querySelector('.info-nav-btn');
            switchInfoSubTab('tierTestSubTab', firstNavBtn);
        }
    }
    window.scrollTo(0, 0);
}

function backHome() {
    switchTab('mainPage');
}

// Работа с боковым меню (Sidebar)
const menuBtn = document.getElementById('menuBtn');
const sidebar = document.getElementById('sidebar');

if (menuBtn && sidebar) {
    menuBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        sidebar.classList.toggle('active');
    });

    window.addEventListener('click', (e) => {
        if (!sidebar.contains(e.target) && e.target !== menuBtn) {
            sidebar.classList.remove('active');
        }
    });
}

// Инициализация обработчиков фильтров
if (document.getElementById('searchInput')) {
    document.getElementById('searchInput').addEventListener('input', renderPlayers);
    document.getElementById('regionFilter').addEventListener('change', renderPlayers);
    document.getElementById('deviceFilter').addEventListener('change', renderPlayers);
    document.getElementById('kitFilter').addEventListener('change', renderPlayers);
    document.getElementById('retiredToggle').addEventListener('change', renderPlayers);
}

function initSite() {
    renderPlayers();
}

let currentLanguage = localStorage.getItem("language") || "ru";

function applyLanguage() {
    const ruElements =
        document.querySelectorAll(".lang-ru");

    const enElements =
        document.querySelectorAll(".lang-en");

    if (currentLanguage === "en") {
        ruElements.forEach(el =>
            el.style.display = "none"
        );

        enElements.forEach(el =>
            el.style.display = ""
        );
    } else {
        ruElements.forEach(el =>
            el.style.display = ""
        );

        enElements.forEach(el =>
            el.style.display = "none"
        );
    }

    const searchInput =
        document.getElementById("searchInput");

    if (searchInput) {
        searchInput.placeholder =
            currentLanguage === "en"
                ? "Search player..."
                : "Поиск игрока...";
    }

    renderPlayers();
}

function toggleLanguage() {
    currentLanguage =
        currentLanguage === "ru"
            ? "en"
            : "ru";

    localStorage.setItem(
        "language",
        currentLanguage
    );

    applyLanguage();
}

document.addEventListener(
    "DOMContentLoaded",
    () => {
        applyLanguage();
    }
);