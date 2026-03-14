// app.js
//
// This client‑side script powers the geopolitical dashboard.  It fetches
// JSON data from the parent `data` directory, applies simple filters and
// renders four panels: battlefield updates, escalation signals, energy
// shocks and financial stress indicators.  Users can filter by
// category and region using the controls at the top of the page.

document.addEventListener('DOMContentLoaded', () => {
  const updateInfo = document.getElementById('update-info');
  const categorySelect = document.getElementById('category-select');
  const regionInput = document.getElementById('region-input');

  const lists = {
    battlefield: document.getElementById('battlefield-list'),
    escalation: document.getElementById('escalation-list'),
    energy_shock: document.getElementById('energy-list'),
    market_shock: document.getElementById('market-list'),
  };

  let newsItems = [];
  let marketItems = [];

  // Load status to display last update time
  fetch('./data/status.json')
    .then((resp) => resp.ok ? resp.json() : Promise.reject())
    .then((status) => {
      if (status && status.last_updated) {
        const date = new Date(status.last_updated);
        updateInfo.textContent = `Last updated: ${date.toLocaleString()}`;
      }
    })
    .catch(() => {
      updateInfo.textContent = '';
    });

  // Fetch news and markets in parallel
  Promise.all([
    fetch('./data/news.json').then((r) => r.ok ? r.json() : []),
    fetch('./data/markets.json').then((r) => r.ok ? r.json() : []),
  ]).then(([news, markets]) => {
    newsItems = Array.isArray(news) ? news : [];
    marketItems = Array.isArray(markets) ? markets : [];
    render();
  });

  function render() {
    // Clear lists
    Object.values(lists).forEach((ul) => {
      while (ul.firstChild) ul.removeChild(ul.firstChild);
    });
    // Determine filters
    const selectedCategory = categorySelect.value;
    const regionFilter = regionInput.value.trim().toLowerCase();
    // Prepare containers
    const grouped = {
      battlefield: [],
      escalation: [],
      energy_shock: [],
      market_shock: [],
    };
    // Filter news entries
    for (const item of newsItems) {
      const cat = item.category;
      if (selectedCategory && cat !== selectedCategory) continue;
      if (regionFilter && !(item.region || '').toLowerCase().includes(regionFilter)) continue;
      if (grouped[cat]) grouped[cat].push(item);
    }
    // Render news
    for (const cat of Object.keys(grouped)) {
      const ul = lists[cat];
      grouped[cat].slice(0, 20).forEach((item) => {
        const li = document.createElement('li');
        li.className = 'entry';
        const link = document.createElement('a');
        link.href = item.url;
        link.textContent = item.title || '(untitled)';
        link.target = '_blank';
        const meta = document.createElement('div');
        meta.className = 'meta';
        const time = new Date(item.timestamp);
        meta.textContent = `${time.toLocaleString()} | ${item.source}`;
        const summary = document.createElement('div');
        summary.className = 'summary';
        summary.textContent = (item.summary || '').slice(0, 200) + (item.summary && item.summary.length > 200 ? '…' : '');
        li.appendChild(link);
        li.appendChild(meta);
        li.appendChild(summary);
        ul.appendChild(li);
      });
    }
    // Render markets
    const energyNames = new Set(['Brent Crude', 'WTI Crude', 'Natural Gas']);
    const energyList = lists.energy_shock;
    const marketList = lists.market_shock;
    marketItems.forEach((m) => {
      const li = document.createElement('li');
      li.className = 'entry';
      const nameEl = document.createElement('span');
      nameEl.className = 'market-name';
      nameEl.textContent = m.name;
      const priceEl = document.createElement('span');
      priceEl.className = 'market-price';
      priceEl.textContent = typeof m.price === 'number' ? m.price.toFixed(2) : m.price;
      li.appendChild(nameEl);
      li.appendChild(priceEl);
      if (energyNames.has(m.name)) {
        energyList.appendChild(li);
      } else {
        marketList.appendChild(li);
      }
    });
  }

  categorySelect.addEventListener('change', render);
  regionInput.addEventListener('input', () => {
    // Debounce for responsiveness
    render();
  });
});
