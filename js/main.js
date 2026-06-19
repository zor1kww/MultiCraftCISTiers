// Глобальные переменные состояния
let currentTab = 'mainPage';
let currentTheme = 'dark';

// Абсолютно безопасная инициализация (ждет загрузки DOM и проверяет зависимости)
function initSite() {
    // Если глобальные базы еще не созданы, создаем пустые заглушки, чтобы код не падал
    if (typeof window.CONFIG === 'undefined') {
        window.CONFIG = {
            kits: { main: ['Hardcore', 'Manhunt', 'Combo'], sub: ['Diamond', 'Classic'] },
            ptsWeights: { 'HT1': 100, 'HT2': 80, 'HT3': 60, 'LT1': 40, 'LT2': 30, 'LT3': 20 },
            tierColors: { 'HT1': '#ff4747', 'HT2': '#ff8747', 'HT3': '#ffcc47', 'LT1': '#47adff', 'LT2': '#47ffd0', 'LT3': '#be47ff' }
        };
    }
    if (typeof window.players === 'undefined') {
        window.players = [];
    }

    setupEventListeners();
    applyTheme(currentTheme);
    renderLeaderboard();
    fillFAQTable();
    applyFAQColors();
}

// Запуск инициализации при полной готовности страницы
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSite);
} else {
    initSite();
}

// Настройка слушателей событий с проверкой на существование элементов
function setupEventListeners() {
    const ids = ['searchInput', 'kitFilter', 'regionFilter', 'deviceFilter', 'retiredToggle'];
    ids.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            const eventType = (id === 'searchInput') ? 'input' : 'change';
            el.addEventListener(eventType, () => {
                if (id === 'kitFilter') updateLeaderboardTitles();
                renderLeaderboard();
            });
        }
    });

    const menuBtn = document.getElementById('menuBtn');
    const sidebar = document.getElementById('sidebar');
    if (menuBtn && sidebar) {
        menuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('active');
        });
        document.addEventListener('click', (e) => {
            if (!sidebar.contains(e.target) && e.target !== menuBtn) {
                sidebar.classList.remove('active');
            }
        });
    }
}

// Переключение вкладок меню
function switchTab(tabId) {
    currentTab = tabId;
    const tabs = ['mainPage', 'wikiTab', 'hallTab', 'infoCenterTab'];
    tabs.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = (id === tabId) ? 'block' : 'none';
    });

    const sidebar = document.getElementById('sidebar');
    if (sidebar) sidebar.classList.remove('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function backHome() {
    switchTab('mainPage');
}

// Переключение подвкладок в Инфо-центре
function switchInfoSubTab(subTabId, btn) {
    const contents = document.querySelectorAll('.info-sub-tab-content');
    contents.forEach(el => el.style.display = 'none');
    
    const target = document.getElementById(subTabId);
    if (target) target.style.display = 'block';

    const buttons = document.querySelectorAll('.info-nav-btn');
    buttons.forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
}

// Изменение заголовков
function updateLeaderboardTitles() {
    const kitFilter = document.getElementById('kitFilter');
    const leaderboardTitle = document.getElementById('leaderboardTitle');
    const tableSubtitle = document.getElementById('tableSubtitle');
    if (!kitFilter || !leaderboardTitle || !tableSubtitle) return;

    const val = kitFilter.value;
    if (val === 'all') {
        leaderboardTitle.innerText = "OVERALL PVP TOP";
        tableSubtitle.innerText = "OVERALL LEADERBOARD";
    } else {
        const upper = val.toUpperCase();
        leaderboardTitle.innerText = `${upper} PVP TOP`;
        tableSubtitle.innerText = `${upper} LEADERBOARD`;
    }
}

// Поиск ключа кита без учета регистра (защита от опечаток в базе игроков)
function findKitValueIgnoreCase(tiersObj, targetKitName) {
    if (!tiersObj) return 'Unranked';
    const keys = Object.keys(tiersObj);
    const foundKey = keys.find(k => k.toLowerCase().trim() === targetKitName.toLowerCase().trim());
    return foundKey ? tiersObj[foundKey] : 'Unranked';
}

// Разбор строки тира (вырезает "R", если она есть в начале)
function parseTierString(rawTier) {
    if (!rawTier) return { tier: 'Unranked', isRetired: false };
    let clean = String(rawTier).trim();
    if (clean === 'Unranked' || clean === '') return { tier: 'Unranked', isRetired: false };
    
    if (clean.toUpperCase().startsWith('R') && clean.length > 1) {
        return { tier: clean.substring(1).toUpperCase(), isRetired: true };
    }
    return { tier: clean.toUpperCase(), isRetired: false };
}

// Безопасный подсчет PTS игрока
function calculatePlayerPTS(player, targetKit = 'all') {
    let mainTotal = 0;
    let subTotal = 0;
    let hasActiveMain = false;

    const pTiers = player.tiers || {};
    const cfg = window.CONFIG;

    // Считаем Main
    if (cfg && cfg.kits && cfg.kits.main) {
        cfg.kits.main.forEach(kitName => {
            const rawTier = findKitValueIgnoreCase(pTiers, kitName);
            const parsed = parseTierString(rawTier);
            
            if (parsed.tier !== 'Unranked') {
                const pts = (cfg.ptsWeights && cfg.ptsWeights[parsed.tier]) || 0;
                mainTotal += pts;
                if (!parsed.isRetired) {
                    hasActiveMain = true; 
                }
            }
        });
    }

    // Считаем Sub
    if (cfg && cfg.kits && cfg.kits.sub) {
        cfg.kits.sub.forEach(kitName => {
            const rawTier = findKitValueIgnoreCase(pTiers, kitName);
            const parsed = parseTierString(rawTier);
            
            if (parsed.tier !== 'Unranked') {
                const pts = (cfg.ptsWeights && cfg.ptsWeights[parsed.tier]) || 0;
                subTotal += pts;
            }
        });
    }

    if (targetKit === 'all') {
        return {
            pts: mainTotal,
            subPts: subTotal,
            isFullyRetired: !hasActiveMain
        };
    } else {
        const rawTier = findKitValueIgnoreCase(pTiers, targetKit);
        const parsed = parseTierString(rawTier);
        const isSub = (cfg.kits && cfg.kits.sub) ? cfg.kits.sub.some(k => k.toLowerCase() === targetKit.toLowerCase()) : false;
        const pts = (parsed.tier === 'Unranked') ? 0 : ((cfg.ptsWeights && cfg.ptsWeights[parsed.tier]) || 0);

        return {
            pts: isSub ? 0 : pts,
            subPts: isSub ? pts : 0,
            isFullyRetired: parsed.isRetired,
            singleTier: parsed.tier,
            isSingleRetired: parsed.isRetired
        };
    }
}

// Основная функция рендеринга топа
function renderLeaderboard() {
    const listContainer = document.getElementById('playersList');
    if (!listContainer) return;

    const searchInput = document.getElementById('searchInput');
    const kitFilter = document.getElementById('kitFilter');
    const regionFilter = document.getElementById('regionFilter');
    const deviceFilter = document.getElementById('deviceFilter');
    const retiredToggle = document.getElementById('retiredToggle');

    const searchVal = searchInput ? searchInput.value.toLowerCase().trim() : '';
    const kitFilterVal = kitFilter ? kitFilter.value : 'all';
    const regionFilterVal = regionFilter ? regionFilter.value : 'all';
    const deviceFilterVal = deviceFilter ? deviceFilter.value : 'all';
    const showRetired = retiredToggle ? retiredToggle.checked : true;

    const cfg = window.CONFIG;

    // 1. Фильтрация
    let processed = (window.players || []).filter(p => {
        if (!p || !p.name) return false;
        if (searchVal && !p.name.toLowerCase().includes(searchVal)) return false;
        if (regionFilterVal !== 'all' && p.region !== regionFilterVal) return false;
        if (deviceFilterVal !== 'all' && p.device !== deviceFilterVal) return false;
        return true;
    }).map(p => {
        const calc = calculatePlayerPTS(p, kitFilterVal);
        return {
            originalData: p,
            pts: calc.pts,
            subPts: calc.subPts,
            isFullyRetired: calc.isFullyRetired,
            singleTier: calc.singleTier,
            isSingleRetired: calc.isSingleRetired
        };
    });

    if (kitFilterVal !== 'all') {
        processed = processed.filter(item => item.singleTier !== 'Unranked');
    } else {
        processed = processed.filter(item => item.pts > 0);
    }

    // 2. Сортировка
    processed.sort((a, b) => {
        if (kitFilterVal === 'all') {
            if (b.pts !== a.pts) return b.pts - a.pts;
            return b.subPts - a.subPts;
        } else {
            const weightA = (cfg.ptsWeights && cfg.ptsWeights[a.singleTier]) || 0;
            const weightB = (cfg.ptsWeights && cfg.ptsWeights[b.singleTier]) || 0;
            return weightB - weightA;
        }
    });

    // 3. Вычисление Рангов
    let currentRank = 0;
    let activeCount = 0;
    
    const finalItems = processed.map((item) => {
        const isRetiredNow = (kitFilterVal === 'all') ? item.isFullyRetired : item.isSingleRetired;
        
        if (!isRetiredNow) {
            activeCount++;
            currentRank = activeCount;
            return { ...item, rank: currentRank, displayRetired: false };
        } else {
            let theoreticalRank = 1;
            for (let i = 0; i < processed.length; i++) {
                const other = processed[i];
                const otherIsRetired = (kitFilterVal === 'all') ? other.isFullyRetired : other.isSingleRetired;
                if (!otherIsRetired) {
                    if (kitFilterVal === 'all') {
                        if (other.pts > item.pts || (other.pts === item.pts && other.subPts > item.subPts)) {
                            theoreticalRank++;
                        }
                    } else {
                        const wOther = (cfg.ptsWeights && cfg.ptsWeights[other.singleTier]) || 0;
                        const wItem = (cfg.ptsWeights && cfg.ptsWeights[item.singleTier]) || 0;
                        if (wOther > wItem) {
                            theoreticalRank++;
                        }
                    }
                }
            }

            if (theoreticalRank <= 5) {
                return { ...item, rank: theoreticalRank, displayRetired: false }; 
            } else {
                return { ...item, rank: '', displayRetired: true };
            }
        }
    });

    let visibleItems = finalItems;
    if (!showRetired) {
        visibleItems = finalItems.filter(item => !item.displayRetired);
    }

    listContainer.innerHTML = '';
    if (visibleItems.length === 0) {
        listContainer.innerHTML = `<div class="no-results">Игроки не найдены</div>`;
        return;
    }

    // 4. Генерация интерфейса
    visibleItems.forEach((item) => {
        const p = item.originalData;
        const isRetiredNow = (kitFilterVal === 'all') ? item.isFullyRetired : item.isSingleRetired;
        
        const card = document.createElement('div');
        card.className = 'player-card';
        if (item.rank && item.rank <= 3 && !item.displayRetired) {
            card.classList.add(`top-${item.rank}`);
        }
        if (item.displayRetired) {
            card.classList.add('retired-status');
        }

        card.onclick = () => renderPlayerModal(p);

        let rankBadge = `<div class="player-rank">#${item.rank}</div>`;
        if (item.displayRetired) {
            rankBadge = `<div class="player-rank retired-text" style="font-size:12px; color:#ff4747;">Retired</div>`;
        }

        let pointsBlock = '';
        if (kitFilterVal === 'all') {
            pointsBlock = `
                <div class="player-card-right-inner">
                    <div class="player-pts">${item.pts} <span style="font-size:11px; opacity:0.6;">PTS</span></div>
                    <div class="player-sub-pts">${item.subPts} sub</div>
                </div>
            `;
        } else {
            const tColor = (cfg.tierColors && cfg.tierColors[item.singleTier]) || '#fff';
            const rPrefix = isRetiredNow ? `<span style="color:#ff4747; font-weight:bold; margin-right:2px;">R</span>` : '';
            pointsBlock = `<div class="player-tier-badge" style="color: ${tColor}; border-color: ${tColor};">${rPrefix}${item.singleTier}</div>`;
        }

        card.innerHTML = `
            <div class="player-card-left">
                ${rankBadge}
                <div class="player-info">
                    <div class="player-name">${p.name}</div>
                    <div class="player-meta">${p.region || '??'} • ${p.device || '??'}</div>
                </div>
            </div>
            <div class="player-card-right">
                ${pointsBlock}
            </div>
        `;
        listContainer.appendChild(card);
    });
}

// Открытие модального окна профиля игрока
function renderPlayerModal(player) {
    const modal = document.getElementById('profileModal');
    if (!modal) return;

    document.getElementById('modalPlayerName').innerText = player.name;
    document.getElementById('modalPlayerMeta').innerText = `${player.region || '??'} [${player.device || '??'}]`;

    const roleContainer = document.getElementById('modalRoleContainer');
    if (roleContainer) {
        roleContainer.innerHTML = '';
        const n = String(player.name).trim();
        if (n === '-999-' || n === 'Sneger') {
            roleContainer.innerHTML = `<span class="tester-badge senior">Старший Тестер</span>`;
        } else if (n === 'zor1kkqwix' || n === '_Xx_deras_xX') {
            roleContainer.innerHTML = `<span class="tester-badge qual">Квалификационный Тестер</span>`;
        }
    }

    const mainRows = document.getElementById('modalMainRows');
    const subRows = document.getElementById('modalSubRows');
    if (mainRows) mainRows.innerHTML = '';
    if (subRows) subRows.innerHTML = '';

    const pTiers = player.tiers || {};
    const cfg = window.CONFIG;

    // Рендер Main
    if (mainRows && cfg && cfg.kits && cfg.kits.main) {
        cfg.kits.main.forEach(kit => {
            const rawTier = findKitValueIgnoreCase(pTiers, kit);
            const parsed = parseTierString(rawTier);
            const tColor = (cfg.tierColors && cfg.tierColors[parsed.tier]) || 'var(--text-muted)';
            const pts = (parsed.tier === 'Unranked') ? 0 : ((cfg.ptsWeights && cfg.ptsWeights[parsed.tier]) || 0);

            const row = document.createElement('div');
            row.className = 'modal-tier-row';
            if (parsed.isRetired || parsed.tier === 'Unranked') row.style.opacity = '0.6';

            const rPrefix = parsed.isRetired ? `<span style="color:#ff4747; font-weight:bold; margin-right:4px;">R</span>` : '';
            row.innerHTML = `
                <div class="modal-kit-left"><span class="modal-kit-icon">🔹</span><span class="modal-kit-name">${kit}</span></div>
                <div class="modal-kit-right"><span style="color: ${tColor}; font-weight:600;">${rPrefix}${parsed.tier}</span><span class="modal-kit-pts">${pts} PTS</span></div>
            `;
            mainRows.appendChild(row);
        });
    }

    // Рендер Sub
    if (subRows && cfg && cfg.kits && cfg.kits.sub) {
        cfg.kits.sub.forEach(kit => {
            const rawTier = findKitValueIgnoreCase(pTiers, kit);
            const parsed = parseTierString(rawTier);
            const tColor = (cfg.tierColors && cfg.tierColors[parsed.tier]) || 'var(--text-muted)';

            const row = document.createElement('div');
            row.className = 'modal-tier-row';
            if (parsed.isRetired || parsed.tier === 'Unranked') row.style.opacity = '0.6';

            const rPrefix = parsed.isRetired ? `<span style="color:#ff4747; font-weight:bold; margin-right:4px;">R</span>` : '';
            row.innerHTML = `
                <div class="modal-kit-left"><span class="modal-kit-icon">🔸</span><span class="modal-kit-name">${kit}</span></div>
                <div class="modal-kit-right"><span style="color: ${tColor}; font-weight:600;">${rPrefix}${parsed.tier}</span></div>
            `;
            subRows.appendChild(row);
        });
    }

    const calc = calculatePlayerPTS(player, 'all');
    const mTotal = document.getElementById('modalMainTotal');
    const sTotal = document.getElementById('modalSubTotal');
    if (mTotal) mTotal.innerText = `Всего за Main: ${calc.pts} PTS`;
    if (sTotal) sTotal.innerText = `Всего за Sub: ${calc.subPts} PTS`;

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modal = document.getElementById('profileModal');
    if (modal) modal.classList.remove('active');
    document.body.style.overflow = '';
}

// Заполнение таблицы распределения PTS в FAQ
function fillFAQTable() {
    const tbody = document.getElementById('faqTableBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    
    const cfg = window.CONFIG;
    const order = ['HT1', 'HT2', 'HT3', 'LT1', 'LT2', 'LT3'];
    order.forEach(tier => {
        const pts = (cfg && cfg.ptsWeights && cfg.ptsWeights[tier]) || 0;
        const color = (cfg && cfg.tierColors && cfg.tierColors[tier]) || '#fff';
        const tr = document.createElement('tr');
        tr.innerHTML = `<td style="color: ${color}; font-weight: bold;">${tier}</td><td>${pts} PTS</td>`;
        tbody.appendChild(tr);
    });
}

// Покраска названий тиров внутри текста FAQ
function applyFAQColors() {
    const cfg = window.CONFIG;
    const pairs = [
        { id: 'faqColorLT3_1', tier: 'LT3' }, { id: 'faqColorLT3_2', tier: 'LT3' },
        { id: 'faqColorLT3_3', tier: 'LT3' }, { id: 'faqColorLT3_4', tier: 'LT3' },
        { id: 'faqColorLT2_1', tier: 'LT2' }, { id: 'faqColorHT2_1', tier: 'HT2' },
        { id: 'faqColorHT1_1', tier: 'HT1' }, { id: 'faqColorHT1_2', tier: 'HT1' },
        { id: 'faqColorHT1_3', tier: 'HT1' }, { id: 'faqColorHT1_4', tier: 'HT1' },
        { id: 'faqColorLT1_1', tier: 'LT1' }, { id: 'faqColorLT1_2', tier: 'LT1' },
        { id: 'faqColorLT1_3', tier: 'LT1' }
    ];

    pairs.forEach(p => {
        const el = document.getElementById(p.id);
        if (el && cfg && cfg.tierColors) {
            el.style.color = cfg.tierColors[p.tier] || '#fff';
            el.style.fontWeight = 'bold';
        }
    });
}

// Изменение тем оформления
function toggleTheme() {
    currentTheme = (currentTheme === 'dark') ? 'light' : 'dark';
    applyTheme(currentTheme);
}

function applyTheme(theme) {
    const root = document.documentElement;
    const btn = document.getElementById('themeToggleBtn');
    if (!root) return;
    
    if (theme === 'light') {
        root.style.setProperty('--bg-main', '#f4f6f9');
        root.style.setProperty('--bg-card', '#ffffff');
        root.style.setProperty('--text-main', '#1e293b');
        root.style.setProperty('--text-muted', '#64748b');
        root.style.setProperty('--border-color', '#e2e8f0');
        root.style.setProperty('--bg-modal', '#ffffff');
        if (btn) btn.innerText = '🌙 Тёмная тема';
    } else {
        root.style.setProperty('--bg-main', '#090d16');
        root.style.setProperty('--bg-card', '#111827');
        root.style.setProperty('--text-main', '#f3f4f6');
        root.style.setProperty('--text-muted', '#9ca3af');
        root.style.setProperty('--border-color', '#1f2937');
        root.style.setProperty('--bg-modal', '#111827');
        if (btn) btn.innerText = '☀️ Светлая тема';
    }
}

// Копирование инвайт-кода
function copyInviteCode() {
    const btn = document.getElementById('inviteBtn');
    if (!btn) return;
    const code = btn.innerText;
    navigator.clipboard.writeText(code).then(() => {
        const oldText = btn.innerText;
        btn.innerText = 'Скопировано!';
        btn.style.background = '#10b981';
        setTimeout(() => {
            btn.innerText = oldText;
            btn.style.background = '';
         }, 1500);
    }).catch(() => {
        alert('Код: ' + code);
    });
}
    