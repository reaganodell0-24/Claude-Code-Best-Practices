/* Portfolio UI */
const Portfolio = {
    init() {
        document.getElementById('add-holding-btn').addEventListener('click', () => this.addHolding());

        // Enter key support for form inputs
        ['add-ticker', 'add-shares', 'add-cost'].forEach(id => {
            document.getElementById(id).addEventListener('keydown', (e) => {
                if (e.key === 'Enter') this.addHolding();
            });
        });
    },

    async load() {
        try {
            const summary = await Utils.fetchJSON('/api/portfolio/summary');
            this.renderSummary(summary);
            this.renderHoldings(summary.holdings);
        } catch (e) {
            console.error('Failed to load portfolio:', e);
        }
    },

    renderSummary(summary) {
        const container = document.getElementById('portfolio-summary');
        const gainClass = summary.total_gain >= 0 ? 'price-positive' : 'price-negative';

        container.innerHTML = `
            <div class="summary-card">
                <div class="summary-label">Total Value</div>
                <div class="summary-value">${Utils.formatCurrency(summary.total_value)}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Total Cost</div>
                <div class="summary-value">${Utils.formatCurrency(summary.total_cost)}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Total P&L</div>
                <div class="summary-value ${gainClass}">${Utils.formatCurrency(summary.total_gain)}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Return</div>
                <div class="summary-value ${gainClass}">${summary.total_gain_pct.toFixed(2)}%</div>
            </div>
        `;
    },

    renderHoldings(holdings) {
        const tbody = document.getElementById('holdings-body');
        if (holdings.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:var(--text-secondary); padding:24px;">No holdings yet. Add one above.</td></tr>';
            return;
        }

        tbody.innerHTML = holdings.map(h => {
            const plClass = h.gain_loss >= 0 ? 'price-positive' : 'price-negative';
            const sign = h.gain_loss >= 0 ? '+' : '';
            return `
                <tr>
                    <td style="font-weight:600;">${h.ticker}</td>
                    <td>${h.shares}</td>
                    <td>$${h.avg_cost.toFixed(2)}</td>
                    <td>$${h.current_price.toFixed(2)}</td>
                    <td>$${h.market_value.toFixed(2)}</td>
                    <td class="${plClass}">${sign}$${h.gain_loss.toFixed(2)}</td>
                    <td class="${plClass}">${sign}${h.gain_loss_pct.toFixed(2)}%</td>
                    <td><button class="btn-danger" onclick="Portfolio.deleteHolding(${h.id})">Delete</button></td>
                </tr>
            `;
        }).join('');
    },

    async addHolding() {
        const ticker = document.getElementById('add-ticker').value.trim().toUpperCase();
        const shares = parseFloat(document.getElementById('add-shares').value);
        const avgCost = parseFloat(document.getElementById('add-cost').value);

        if (!ticker || isNaN(shares) || isNaN(avgCost)) return;

        try {
            await fetch('/api/portfolio/holdings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ticker, shares, avg_cost: avgCost }),
            });
            document.getElementById('add-ticker').value = '';
            document.getElementById('add-shares').value = '';
            document.getElementById('add-cost').value = '';
            await this.load();
        } catch (e) {
            console.error('Failed to add holding:', e);
        }
    },

    async deleteHolding(id) {
        try {
            await fetch(`/api/portfolio/holdings/${id}`, { method: 'DELETE' });
            await this.load();
        } catch (e) {
            console.error('Failed to delete holding:', e);
        }
    },
};
