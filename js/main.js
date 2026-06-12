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

// Расчет общих очков игрока по массиву китов
function calcPoints(player, kits) {
    let total = 0;
    kits.forEach(kit => {
        const tier = player.tiers[kit] || "Unranked";
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
    
    const isRetired = player.retired === true;
    document.getElementById('modalPlayerName').innerHTML = player.name;
    
    let metaText = `${player.region} ${player.device}`;
    if (isRetired) {
        metaText += ` RETIRED`;
    }
    document.getElementById('modalPlayerMeta').innerText = metaText;
    
    // В профилях по-прежнему выводится стандартный бейдж без уточнений ранга тестера
    const roleContainer = document.getElementById('modalRoleContainer');
    if (player.name === "-999-" || player.name === "zor1kkqwix" || player.name === "Sneger") {
        roleContainer.innerHTML = `<span class="custom-role-badge">Tier-Tester</span>`;
    } else {
        roleContainer.innerHTML = '';
    }
    
    const mainRows = document.getElementById('modalMainRows');
    const subRows = document.getElementById('modalSubRows');
    
    mainRows.innerHTML = maintiers.map(kit => {
        const t = player.tiers[kit] || "Unranked";
        const iconSrc = kitImages[kit] || "";
        return `<div class="modal-row">
            <div class="modal-kit-left">
                <img class="modal-kit-icon" src="${iconSrc}" onerror="this.style.opacity='0'" alt="">
                <span class="m-kit">${kit}</span>
            </div>
            <div class="m-right-side">
                ${getTierBadge(t, isRetired)} 
                <span class="m-pts-box">(${tierPoints[t]} PTS)</span>
            </div>
        </div>`;
    }).join('');
    
    subRows.innerHTML = subtiers.map(kit => {
        const t = player.tiers[kit] || "Unranked";
        const iconSrc = kitImages[kit] || "";
        return `<div class="modal-row">
            <div class="modal-kit-left">
                <img class="modal-kit-icon" src="${iconSrc}" onerror="this.style.opacity='0'" alt="">
                <span class="m-kit">${kit}</span>
            </div>
            <div class="m-right-side">
                ${getTierBadge(t, isRetired)} 
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
        
        if (!showRetiredInPlace && player.retired === true) {
            return false;
        }
        
        if (targetKit !== 'all') {
            const tier = player.tiers[targetKit] || "Unranked";
            return matchesSearch && matchesRegion && matchesDevice && tier !== "Unranked";
        }
        
        return matchesSearch && matchesRegion && matchesDevice;
    });

    if (targetKit === 'all') {
        filtered.sort((a, b) => {
            const aRetired = a.retired === true;
            const bRetired = b.retired === true;
            if (showRetiredInPlace) {
                return calcPoints(b, maintiers) - calcPoints(a, maintiers);
            } else {
                if (aRetired !== bRetired) return aRetired ? 1 : -1;
                return calcPoints(b, maintiers) - calcPoints(a, maintiers);
            }
        });
    } else {
        filtered.sort((a, b) => {
            const tierA = a.tiers[targetKit] || "Unranked";
            const tierB = b.tiers[targetKit] || "Unranked";
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
        
        const isRetired = player.retired === true;

        // Фикс: Свечение топ-5 теперь применяется ВСЕГДА (и в Overall, и в конкретных китах)
        if (index === 0) topClass = 'top-rank-1';
        else if (index === 1) topClass = 'top-rank-2';
        else if (index === 2) topClass = 'top-rank-3';
        else if (index === 3) topClass = 'top-rank-4';
        else if (index === 4) topClass = 'top-rank-5';
        
        if (isRetired && showRetiredInPlace) {
            topClass = 'retired-status';
        }
        
        if (targetKit === 'all') {
            const mainPts = calcPoints(player, maintiers);
            rightColumnContent = `<span style="color: var(--accent);">${mainPts} PTS</span>`;
        } else {
            const currentTier = player.tiers[targetKit] || "Unranked";
            rightColumnContent = getTierBadge(currentTier, isRetired);
        }

        let quickTiersHTML = '';
        if (targetKit === 'all') {
            quickTiersHTML = `<div class="player-tiers-row">`;
            maintiers.forEach(kit => {
                const tier = player.tiers[kit] || "Unranked";
                const clr = tierColors[tier] || '#444b66';
                const iconSrc = kitImages[kit] || "";
                const labelText = (isRetired && tier !== "Unranked") ? `R${tier}` : tier;
                
                if (tier !== "Unranked") {
                    quickTiersHTML += `
                    <div class="tier-item-box">
                        <div class="tier-icon-circle" style="border-color: ${clr}cc; box-shadow: 0 0 6px ${clr}22;">
                            <img src="${iconSrc}" onerror="this.style.opacity=0" alt="">
                        </div>
                        <div class="tier-label-under" style="color: ${clr};">${labelText}</div>
                    </div>`;
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
                        ${isRetired ? `<span class="retired-meta-tag">RETIRED</span>` : ''}
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

// Таблица начисления PTS во вкладке FAQ
function buildFaqTable() {
    const tbody = document.getElementById('faqTableBody');
    if (!tbody) return;
    const order = ['HT1', 'LT1', 'HT2', 'LT2', 'HT3', 'LT3', 'HT4', 'LT4', 'HT5', 'LT5', 'Unranked'];
    tbody.innerHTML = order.map(tier => {
        const color = tierColors[tier];
        return `<tr>
            <td><span style="color: ${color}; font-weight:bold; padding: 2px 6px; border-radius:4px; border:1px solid ${color}44; background:${color}11;">${tier}</span></td>
            <td><span style="color: var(--accent); font-weight:bold;">${tierPoints[tier]} PTS</span></td>
        </tr>`;
    }).join('');
}

// Функция переключения вкладок
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
        if (tabId === 'faqTab') buildFaqTable();
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

// Инициализация при изменении фильтров
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
