// Глобальное хранилище данных
let gameData = { players: [], honors: [], testers: [] };

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('data.json');
        gameData = await response.json();
        
        renderLeaderboard();
        renderHonors();
        renderTesters();
        setupFilters();
    } catch (error) {
        console.error("Ошибка загрузки данных:", error);
    }
});

// Навигация между вкладками
function switchTab(tabId) {
    // Скрываем все секции
    document.querySelectorAll('.content-section').forEach(s => s.classList.add('hidden'));
    // Убираем активный класс у кнопок
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active-tab'));
    
    // Показываем нужную
    document.getElementById(sec-${tabId}).classList.remove('hidden');
    document.getElementById(tab-${tabId}).classList.add('active-tab');
}

// Красивое форматирование тира
function formatTier(tier) {
    if (!tier || tier === "Unranked") return '<span class="text-slate-600">Unranked</span>';
    const isHT = tier.startsWith('HT');
    return <span class="${isHT ? 'tier-ht' : 'tier-lt'}">${tier}</span>;
}

// Рендер таблицы лидеров
function renderLeaderboard() {
    const tableBody = document.getElementById('playerTable');
    const searchNick = document.getElementById('searchNick').value.toLowerCase();
    const kitFilter = document.getElementById('filterKit').value;
    const countryFilter = document.getElementById('filterCountry').value;
    const deviceFilter = document.getElementById('filterDevice').value;

    // Обновляем заголовок колонки кита
    document.getElementById('currentKitHead').innerText = Тир: ${kitFilter};

    // Фильтрация
    const filtered = gameData.players.filter(p => {
        const matchesNick = p.nickname.toLowerCase().includes(searchNick);
        const matchesCountry = countryFilter === 'all' || p.country === countryFilter;
        const matchesDevice = deviceFilter === 'all' || p.device === deviceFilter;
        return matchesNick && matchesCountry && matchesDevice;
    });

    // Сортировка по Elo (от большего к меньшему)
    filtered.sort((a, b) => b.elo - a.elo);

    tableBody.innerHTML = filtered.map(p => 
        <tr class="border-b border-slate-800 row-hover transition-all">
            <td class="p-4">
                <div class="flex items-center">
                    <span class="font-bold text-lg mr-2">${p.nickname}</span>
                    ${p.isCoach ? <span class="bg-green-500/20 text-green-400 text-[10px] px-2 py-0.5 rounded-full border border-green-500/30" title="Тренер: ${p.coachDetails.price}">COACH</span> : ''}
                </div>
            </td>
            <td class="p-4">
                <span class="bg-slate-800 px-2 py-1 rounded text-sm">${p.country}</span>
            </td>
            <td class="p-4 font-mono text-blue-400">${p.elo}</td>
            <td class="p-4">${formatTier(p.tiers[kitFilter])}</td>
            <td class="p-4">
                <div class="text-sm text-slate-400">${p.device}</div>
                <div class="text-[11px] text-slate-500 italic">via ${p.tester}</div>
            </td>
        </tr>
    ).join('');
}

// Рендер Зала Славы
function renderHonors() {
    const container = document.getElementById('honorsList');
    container.innerHTML = gameData.honors.map(h => 
        <div class="glass p-6 rounded-2xl border-l-4 border-yellow-500 shadow-lg">
            <h3 class="text-xl font-bold text-yellow-500 mb-2">${h.nickname}</h3>
            <p class="text-slate-300 text-sm italic">"${h.reason}"</p>
        </div>
    ).join('');
}

// Рендер Тестеров
function renderTesters() {
    const container = document.getElementById('testersList');
  container.innerHTML = gameData.testers.map(t => 
        <div class="glass p-5 rounded-2xl hover:border-blue-500/50 transition-all">
            <div class="font-bold text-lg mb-1">${t.nickname}</div>
            <div class="text-blue-400 text-sm mb-3 font-mono">${t.discord}</div>
            <div class="flex flex-wrap gap-2">
                ${t.kits.map(k => <span class="text-[10px] bg-slate-800 px-2 py-0.5 rounded border border-slate-700">${k}</span>).join('')}
            </div>
        </div>
    ).join('');
}

// Слушатели событий для фильтров
function setupFilters() {
    ['searchNick', 'filterKit', 'filterCountry', 'filterDevice'].forEach(id => {
        document.getElementById(id).addEventListener('input', renderLeaderboard);
    });
}
