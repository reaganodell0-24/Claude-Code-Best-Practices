/* Main application controller */
const App = {
    currentTicker: null,
    currentTab: 'financials',

    init() {
        this.bindSearch();
        this.bindTabs();
        Statements.init();
        Portfolio.init();
    },

    bindSearch() {
        const input = document.getElementById('ticker-search');
        const results = document.getElementById('search-results');

        const doSearch = Utils.debounce(async (query) => {
            if (query.length < 1) {
                results.classList.remove('active');
                return;
            }
            try {
                const resp = await Utils.fetchJSON(`/api/market/search?q=${encodeURIComponent(query)}`);
                const data = resp.results || resp;
                if (!data || data.length === 0) {
                    results.classList.remove('active');
                    return;
                }
                results.innerHTML = data.map(r => `
                    <div class="search-result-item" data-symbol="${r.symbol}">
                        <span class="search-result-symbol">${r.symbol}</span>
                        <span class="search-result-name">${r.name}</span>
                    </div>
                `).join('');
                results.classList.add('active');

                results.querySelectorAll('.search-result-item').forEach(item => {
                    item.addEventListener('click', () => {
                        const symbol = item.dataset.symbol;
                        input.value = symbol;
                        results.classList.remove('active');
                        this.selectTicker(symbol);
                    });
                });
            } catch (e) {
                results.classList.remove('active');
            }
        }, 300);

        input.addEventListener('input', () => doSearch(input.value.trim()));

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const val = input.value.trim().toUpperCase();
                if (val) {
                    results.classList.remove('active');
                    this.selectTicker(val);
                }
            }
        });

        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-container')) {
                results.classList.remove('active');
            }
        });
    },

    bindTabs() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tab = btn.dataset.tab;
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
                document.querySelector(`[data-panel="${tab}"]`).classList.add('active');
                this.currentTab = tab;

                if (tab === 'portfolio') Portfolio.load();
                if (tab === 'financials' && this.currentTicker) Statements.load(this.currentTicker);
                if (tab === 'dcf' && this.currentTicker) DCF.load(this.currentTicker);
            });
        });
    },

    async selectTicker(ticker) {
        this.currentTicker = ticker;

        // Update header
        document.getElementById('ticker-name').textContent = ticker;
        document.getElementById('current-price').textContent = '';
        document.getElementById('price-change').textContent = '';

        // Fetch quote for header
        try {
            const quote = await Utils.fetchJSON(`/api/market/quote/${ticker}`);
            document.getElementById('ticker-name').textContent = `${quote.ticker} — ${quote.name}`;
            document.getElementById('current-price').textContent = `$${quote.price.toFixed(2)}`;
            const changeEl = document.getElementById('price-change');
            changeEl.textContent = Utils.formatPriceChange(quote.change, quote.change_percent);
            changeEl.className = 'price-change ' + (quote.change >= 0 ? 'price-positive' : 'price-negative');
        } catch (e) {
            // Quote fetch failed, continue anyway
        }

        // Load current tab data
        if (this.currentTab === 'financials') Statements.load(ticker);
        if (this.currentTab === 'dcf') DCF.load(ticker);
    },
};

document.addEventListener('DOMContentLoaded', () => App.init());
