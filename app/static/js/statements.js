/* Financial Statement rendering */
const Statements = {
    currentSubTab: 'income',
    currentFreq: 'annual',
    currentTicker: null,

    init() {
        document.querySelectorAll('.sub-tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.sub-tab-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentSubTab = btn.dataset.subtab;
                if (this.currentTicker) this.load(this.currentTicker);
            });
        });

        document.querySelectorAll('.freq-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.freq-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentFreq = btn.dataset.freq;
                if (this.currentTicker) this.load(this.currentTicker);
            });
        });
    },

    async load(ticker) {
        this.currentTicker = ticker;
        const container = document.getElementById('statement-table-container');
        container.innerHTML = '<div class="empty-state">Loading...</div>';

        const endpoints = {
            income: `/api/statements/${ticker}/income?freq=${this.currentFreq}`,
            cashflow: `/api/statements/${ticker}/cashflow?freq=${this.currentFreq}`,
            balance: `/api/statements/${ticker}/balance-sheet?freq=${this.currentFreq}`,
        };

        try {
            const data = await Utils.fetchJSON(endpoints[this.currentSubTab]);
            this.render(data.data, container);
        } catch (e) {
            container.innerHTML = '<div class="empty-state">No data available for this ticker</div>';
        }
    },

    render(data, container) {
        if (!data || Object.keys(data).length === 0) {
            container.innerHTML = '<div class="empty-state">No data available</div>';
            return;
        }

        const periods = Object.keys(data).sort().reverse();
        const allItems = new Set();
        periods.forEach(p => Object.keys(data[p]).forEach(k => allItems.add(k)));

        // Order items: keep the original order from the first period
        const items = [...allItems];

        let html = '<div style="overflow-x:auto;"><table class="statement-table"><thead><tr>';
        html += '<th>Line Item</th>';
        periods.forEach(p => {
            const label = p.substring(0, 7); // YYYY-MM
            html += `<th>${label}</th>`;
        });
        html += '</tr></thead><tbody>';

        items.forEach(item => {
            html += '<tr>';
            html += `<td>${this.formatLabel(item)}</td>`;
            periods.forEach(p => {
                const val = data[p][item];
                const negClass = val !== null && val < 0 ? ' class="negative"' : '';
                html += `<td${negClass}>${this.formatValue(val)}</td>`;
            });
            html += '</tr>';
        });

        html += '</tbody></table></div>';
        container.innerHTML = html;
    },

    formatLabel(key) {
        // Convert camelCase/PascalCase to spaced
        return key.replace(/([A-Z])/g, ' $1').replace(/^ /, '').trim();
    },

    formatValue(val) {
        if (val === null || val === undefined) return '--';
        const abs = Math.abs(val);
        const sign = val < 0 ? '-' : '';
        if (abs >= 1e9) return sign + '$' + (abs / 1e9).toFixed(2) + 'B';
        if (abs >= 1e6) return sign + '$' + (abs / 1e6).toFixed(2) + 'M';
        if (abs >= 1e3) return sign + '$' + (abs / 1e3).toFixed(2) + 'K';
        return sign + '$' + abs.toFixed(2);
    },
};
