// ==========================================
// ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ И ОБРАБОТКА ДАННЫХ
// ==========================================

// Очистка названия тира от префикса Retired 'R' (например: "RHT1" -> "HT1")
function getCleanTierName(rawTier) {
    if (!rawTier) return "Unranked";
    if (typeof rawTier === 'string' && rawTier.startsWith('R')) {
        return rawTier.substring(1);
    }
    return rawTier;
}

// Получение чистого тира игрока по конкретному киту
function getCleanTier(player, kit) {
    if (!player || !player.maintiers || !player.maintiers[kit]) {
        return "Unranked";
    }
    const val = player.maintiers[kit];
    if (typeof val === 'object' && val !== null) {
        return getCleanTierName(val.tier);
    }
    return getCleanTierName(val);
}

// Проверка, является ли кит Retired
function isKitRetired(player, kit) {
    if (!player || !player.maintiers || !player.maintiers[kit]) {
        return false;
    }
    const val = player.maintiers[kit];
    if (typeof val === 'object' && val !== null) {
        return !!val.retired;
    }
    if (typeof val === 'string') {
        return val.startsWith('R');
    }
    return false;
}

// Проверка, есть ли у игрока хоть один Retired кит
function hasAnyRetiredKit(player) {
    if (!player) return false;
    if (player.retired) return true;
    if (!player.maintiers) return false;
    
    for (const kit in player.maintiers) {
        if (isKitRetired(player, kit)) {
            return true;
        }
    }
    return false;
}

// Расчёт среднего тира игрока по всем активным Main-китам
function calcAverageTier(player) {
    if (!player || !player.maintiers) return "Unranked";
    
    const weights = {
        "HT1": 10, "LT1": 9,
        "HT2": 8,  "LT2": 7,
        "HT3": 6,  "LT3": 5,
        "HT4": 4,  "LT4": 3,
        "HT5": 2,  "LT5": 1
    };
    
    let totalScore = 0;
    let count = 0;

    for (const kit in player.maintiers) {
        const cleanTier = getCleanTier(player, kit);
        if (cleanTier && cleanTier !== "Unranked" && weights[cleanTier] !== undefined) {
            totalScore += weights[cleanTier];
            count++;
        }
    }

    if (count === 0) return "Unranked";

    const avgWeight = Math.round(totalScore / count);

    for (const [tier, weight] of Object.entries(weights)) {
        if (weight === avgWeight) {
            return tier;
        }
    }

    return "Unranked";
}

// Расчёт общих очков игрока для Overall PVP TOP
function calculateTotalPoints(player) {
    if (!player || !player.maintiers) return 0;
    
    const activePts = (typeof tierPoints !== 'undefined') ? tierPoints : {};
    let total = 0;

    for (const kit in player.maintiers) {
        const cleanTier = getCleanTier(player, kit);
        if (cleanTier && activePts[cleanTier] !== undefined) {
            total += activePts[cleanTier];
        }
    }

    return total;
}

// ==========================================
// МОДАЛЬНОЕ ОКНО ПРОФИЛЯ
// ==========================================

function openProfile(playerName) {
    if (typeof players === 'undefined') return;
    
    const player = players.find(p => p.name.toLowerCase() === playerName.toLowerCase());
    if (!player) return;

    const modal = document.getElementById('profileModal');
    if (!modal) return;

    const modalName = document.getElementById('modalPlayerName');
    if (modalName) modalName.innerHTML = player.name;
    
    // Генерация красивых тегов оформления для профиля в ряд
    let metaHTML = '';
    if (player.region) {
        metaHTML += `<span class="player-meta-tag">${player.region}</span>`;
    }
    
    const metaContainer = document.getElementById('modalPlayerMeta');
    if (metaContainer) metaContainer.innerHTML = metaHTML;

    // Сетка Main-китов
    const mainKitsContainer = document.getElementById('modalMainKits');
    if (mainKitsContainer) {
        let mainHTML = '';
        const activeMaintiers = (typeof maintiers !== 'undefined') ? maintiers : [];
        const activeColors = (typeof tierColors !== 'undefined') ? tierColors : {};
        const activeKitImages = (typeof kitImages !== 'undefined') ? kitImages : {};

        activeMaintiers.forEach(kit => {
            const cleanTier = getCleanTier(player, kit);
            const retired = isKitRetired(player, kit);
            const color = activeColors[cleanTier] || '#888';
            const img = activeKitImages[kit] || '';

            mainHTML += `
                <div class="modal-kit-card">
                    <img src="${img}" alt="${kit}" class="modal-kit-icon">
                    <div class="modal-kit-info">
                        <span class="modal-kit-name">${kit.toUpperCase()}</span>
                        <span class="modal-kit-tier" style="color: ${color}">
                            ${cleanTier}${retired ? ' (R)' : ''}
                        </span>
                    </div>
                </div>
            `;
        });
        mainKitsContainer.innerHTML = mainHTML;
    }

    // Сетка Sub-китов
    const subKitsContainer = document.getElementById('modalSubKits');
    if (subKitsContainer) {
        let subHTML = '';
        if (player.subtiers && Object.keys(player.subtiers).length > 0) {
            for (const [subKit, rawTier] of Object.entries(player.subtiers)) {
                const cleanTier = getCleanTierName(rawTier);
                const activeColors = (typeof tierColors !== 'undefined') ? tierColors : {};
                const color = activeColors[cleanTier] || '#888';

                subHTML += `
                    <div class="modal-kit-card sub-card">
                        <div class="modal-kit-info">
                            <span class="modal-kit-name">${subKit.toUpperCase()}</span>
                            <span class="modal-kit-tier" style="color: ${color}">${cleanTier}</span>
                        </div>
                    </div>
                `;
            }
        } else {
            subHTML = '<div class="no-subtiers">Нет подкатегорий</div>';
        }
        subKitsContainer.innerHTML = subHTML;
    }

    modal.style.display = 'flex';
}

function closeProfile() {
    const modal = document.getElementById('profileModal');
    if (modal) modal.style.display = 'none';
}

// ==========================================
// ОСНОВНОЙ РЕНДЕР ТАБЛИЦЫ ЛИДЕРОВ
// ==========================================

function renderPlayers() {
    const list = document.getElementById('playersList');
    if (!list) return;

    const searchInput = document.getElementById('searchInput');
    const search = searchInput ? searchInput.value.toLowerCase().trim() : '';
    
    const regionFilter = document.getElementById('regionFilter');
    const region = regionFilter ? regionFilter.value : 'all';
    
    const kitFilter = document.getElementById('kitFilter');
    const targetKit = kitFilter ? kitFilter.value : 'all';
    
    const retiredToggle = document.getElementById('retiredToggle');
    const showRetiredInPlace = retiredToggle ? retiredToggle.checked : false;

    if (typeof players === 'undefined' || !Array.isArray(players)) {
        list.innerHTML = '<div style="text-align:center;color:#ffcc47;padding:40px;">Загрузка базы данных игроков...</div>';
        return;
    }

    const titleEl = document.getElementById('leaderboardTitle');
    const subtitleEl = document.getElementById('tableSubtitle');

    if (targetKit === 'all') {
        if (titleEl) titleEl.innerText = 'OVERALL PVP TOP';
        if (subtitleEl) subtitleEl.innerText = 'OVERALL LEADERBOARD';
    } else {
        if (titleEl) titleEl.innerText = `${targetKit.toUpperCase()} TOP`;
        if (subtitleEl) subtitleEl.innerText = `${targetKit.toUpperCase()} LEADERBOARD`;
    }

    const activeMaintiers = (typeof maintiers !== 'undefined') ? maintiers : [];
    const activePts = (typeof tierPoints !== 'undefined') ? tierPoints : {};
    const activeColors = (typeof tierColors !== 'undefined') ? tierColors : {};
    const activeKitImages = (typeof kitImages !== 'undefined') ? kitImages : {};

    // Фильтрация игроков
    let filtered = players.filter(player => {
        const matchesSearch = player.name.toLowerCase().includes(search);
        const matchesRegion = (region === 'all' || player.region === region);
        
        if (targetKit !== 'all') {
            const tier = getCleanTier(player, targetKit);
            const ret = isKitRetired(player, targetKit);
            if (!showRetiredInPlace && ret) {
                return false;
            }
            return matchesSearch && matchesRegion && tier !== "Unranked";
        }
        
        if (!showRetiredInPlace && hasAnyRetiredKit(player)) {
            return false;
        }
        
        return matchesSearch && matchesRegion;
    });

    // Сортировка игроков
    if (targetKit === 'all') {
        filtered.sort((a, b) => calculateTotalPoints(b) - calculateTotalPoints(a));
    } else {
        filtered.sort((a, b) => {
            const tierA = getCleanTier(a, targetKit);
            const tierB = getCleanTier(b, targetKit);
            const ptA = activePts[tierA] || 0;
            const ptB = activePts[tierB] || 0;
            return ptB - ptA;
        });
    }

    if (filtered.length === 0) {
        list.innerHTML = '<div style="text-align:center;color:#888;padding:40px;">Игроки не найдены</div>';
        return;
    }

    // Генерация HTML
    let html = '';
    filtered.forEach((player, index) => {
        const rank = index + 1;
        
        // Постоянная плашка с рангом
        let rankClass = 'rank-badge';
        if (rank === 1) rankClass += ' rank-1';
        else if (rank === 2) rankClass += ' rank-2';
        else if (rank === 3) rankClass += ' rank-3';

        // Формирование тегов мета-информации для карточки игрока
        let metaTagsHTML = '';
        if (player.region) {
            metaTagsHTML += `<span class="player-meta-tag">${player.region}</span>`;
        }

        // Рендер китов
        let kitsHTML = '';
        if (targetKit === 'all') {
            activeMaintiers.forEach(kit => {
                const cleanTier = getCleanTier(player, kit);
                const retired = isKitRetired(player, kit);
                const color = activeColors[cleanTier] || '#888';
                const img = activeKitImages[kit] || '';

                if (cleanTier !== "Unranked") {
                    kitsHTML += `
                        <div class="kit-item-badge">
                            <img src="${img}" alt="${kit}">
                            <span style="color: ${color}">${cleanTier}${retired ? ' (R)' : ''}</span>
                        </div>
                    `;
                }
            });
        } else {
            const cleanTier = getCleanTier(player, targetKit);
            const retired = isKitRetired(player, targetKit);
            const color = activeColors[cleanTier] || '#888';
            const img = activeKitImages[targetKit] || '';

            kitsHTML = `
                <div class="kit-item-badge single-kit">
                    <img src="${img}" alt="${targetKit}">
                    <span style="color: ${color}">${cleanTier}${retired ? ' (R)' : ''}</span>
                </div>
            `;
        }

        const avgTier = calcAverageTier(player);
        const avgColor = activeColors[avgTier] || '#888';
        const totalPts = calculateTotalPoints(player);

        html += `
            <div class="player-card" onclick="openProfile('${player.name}')">
                <div class="${rankClass}">#${rank}</div>
                <div class="player-info-section">
                    <div class="player-name-row">
                        <span class="player-main-name">${player.name}</span>
                        <div class="player-meta-group">
                            ${metaTagsHTML}
                        </div>
                    </div>
                    <div class="player-kits-row">
                        ${kitsHTML}
                    </div>
                </div>
                <div class="player-stats-section">
                    <div class="stat-box">
                        <span class="stat-label">AVG TIER</span>
                        <span class="stat-value" style="color: ${avgColor}">${avgTier}</span>
                    </div>
                    <div class="stat-box">
                        <span class="stat-label">PTS</span>
                        <span class="stat-value pts-value">${totalPts}</span>
                    </div>
                </div>
            </div>
        `;
    });

    list.innerHTML = html;
}

// Инициализация при первой загрузке
function initSite() {
    renderPlayers();
}

// Слушатели событий
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const regionFilter = document.getElementById('regionFilter');
    const kitFilter = document.getElementById('kitFilter');
    const retiredToggle = document.getElementById('retiredToggle');

    if (searchInput) searchInput.addEventListener('input', renderPlayers);
    if (regionFilter) regionFilter.addEventListener('change', renderPlayers);
    if (kitFilter) kitFilter.addEventListener('change', renderPlayers);
    if (retiredToggle) retiredToggle.addEventListener('change', renderPlayers);

    // Закрытие модалки при клике вне её контента
    window.addEventListener('click', (e) => {
        const modal = document.getElementById('profileModal');
        if (e.target === modal) {
            closeProfile();
        }
    });

    // Первичная отрисовка
    initSite();
});
