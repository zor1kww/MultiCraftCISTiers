// Загрузка PTS (киты) из GET /api/pts. Заменяет чтение players.js.
// Подключать ПОСЛЕ config.js и classic.js (нужен window.PTS), до или после main.js.
// Данные приходят в том же виде, что был players.js:
//   { updatedAt, players: [{ name, region, tiers, matchHistory, penaltyByKit }] }

(() => {
    const FIRST_LOAD_TIMEOUT_MS = 60000;   // бесплатный Render "просыпается" почти минуту
    const REFRESH_TIMEOUT_MS = 20000;
    const SLOW_HINT_MS = 8000;

    let loading = false;
    let loaded = false;
    let updatedAt = null;
    let loadedAt = 0;

    function apiUrl() {
        const base = (typeof API_BASE_URL !== 'undefined') ? String(API_BASE_URL).replace(/\/+$/, '') : '';
        return `${base}/api/pts`;
    }

    function listEl() {
        return document.getElementById('kitsPlayersList');
    }

    function showMessage(html) {
        const el = listEl();
        if (el && !loaded) el.innerHTML = html;
    }

    async function fetchPts(timeoutMs) {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), timeoutMs);
        try {
            const response = await fetch(apiUrl(), { cache: 'no-store', signal: controller.signal });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            if (!data || !Array.isArray(data.players)) throw new Error('неожиданный формат ответа');
            return data;
        } finally {
            clearTimeout(timer);
        }
    }

    async function loadPts(isInitial) {
        if (loading || !window.PTS) return false;
        loading = true;

        let hintTimer = null;
        if (isInitial) {
            hintTimer = setTimeout(() => {
                showMessage('<div class="board-empty">Сервер просыпается, это может занять до минуты…</div>');
            }, SLOW_HINT_MS);
        }

        try {
            const data = await fetchPts(isInitial ? FIRST_LOAD_TIMEOUT_MS : REFRESH_TIMEOUT_MS);
            const changed = (data.updatedAt || null) !== updatedAt;
            updatedAt = data.updatedAt || null;
            loadedAt = Date.now();
            if (changed || !loaded) {
                loaded = true;
                window.PTS.setPlayers(data.players);   // перерисует рейтинг, дуэли и главную
            }
            return true;
        } catch (e) {
            console.warn('Не удалось загрузить PTS:', e);
            showMessage(
                '<div class="board-empty">Не удалось загрузить рейтинг. ' +
                '<button class="load-retry-btn" onclick="retryLoadPts()">Повторить</button></div>'
            );
            return false;
        } finally {
            if (hintTimer) clearTimeout(hintTimer);
            loading = false;
        }
    }

    window.retryLoadPts = () => {
        showMessage('<div class="board-empty">Загрузка PTS-рейтинга…</div>');
        loadPts(true);
    };

    function startAutoRefresh() {
        const seconds = (typeof PLAYERS_REFRESH_SECONDS !== 'undefined') ? PLAYERS_REFRESH_SECONDS : 60;
        setInterval(() => {
            if (!document.hidden && loaded) loadPts(false);
        }, seconds * 1000);
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && loaded && Date.now() - loadedAt > seconds * 1000) loadPts(false);
        });
    }

    function start() {
        if (!window.PTS) {
            console.warn('pts-loader: window.PTS не найден - classic.js должен подключаться раньше.');
            return;
        }
        loadPts(true);
        startAutoRefresh();
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
    else start();
})();
