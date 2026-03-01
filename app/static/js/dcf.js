/* DCF Valuation UI */
const DCF = {
    currentTicker: null,
    assumptions: null,

    async load(ticker) {
        this.currentTicker = ticker;
        const inputsEl = document.getElementById('dcf-inputs');
        inputsEl.innerHTML = '<div class="empty-state">Loading DCF...</div>';

        try {
            const data = await Utils.fetchJSON(`/api/valuation/dcf/${ticker}`);
            this.assumptions = data.assumptions;
            this.renderInputs(data.assumptions);
            this.renderResults(data);
        } catch (e) {
            inputsEl.innerHTML = '<div class="empty-state">Could not load DCF data for this ticker</div>';
            document.getElementById('dcf-fair-value').innerHTML = '';
            document.getElementById('dcf-projections').innerHTML = '';
            document.getElementById('dcf-sensitivity').innerHTML = '';
        }
    },

    renderInputs(assumptions) {
        const fields = [
            { key: 'revenue_growth', label: 'Revenue Growth', min: -0.5, max: 1.0, step: 0.01, fmt: 'pct' },
            { key: 'operating_margin', label: 'Operating Margin', min: -0.5, max: 0.8, step: 0.01, fmt: 'pct' },
            { key: 'tax_rate', label: 'Tax Rate', min: 0, max: 0.5, step: 0.01, fmt: 'pct' },
            { key: 'capex_pct_revenue', label: 'CapEx % of Revenue', min: 0, max: 0.3, step: 0.005, fmt: 'pct' },
            { key: 'da_pct_revenue', label: 'D&A % of Revenue', min: 0, max: 0.2, step: 0.005, fmt: 'pct' },
            { key: 'wacc', label: 'WACC (Discount Rate)', min: 0.04, max: 0.20, step: 0.005, fmt: 'pct' },
            { key: 'terminal_growth', label: 'Terminal Growth Rate', min: 0, max: 0.06, step: 0.005, fmt: 'pct' },
            { key: 'projection_years', label: 'Projection Years', min: 3, max: 10, step: 1, fmt: 'int' },
        ];

        let html = '';
        fields.forEach(f => {
            const val = assumptions[f.key];
            const displayVal = f.fmt === 'pct' ? (val * 100).toFixed(1) + '%' : val;
            html += `
                <div class="dcf-input-group">
                    <label>${f.label}</label>
                    <div class="dcf-input-row">
                        <input type="range" id="dcf-${f.key}"
                            min="${f.min}" max="${f.max}" step="${f.step}" value="${val}"
                            data-key="${f.key}" data-fmt="${f.fmt}">
                        <span class="dcf-value" id="dcf-val-${f.key}">${displayVal}</span>
                    </div>
                </div>
            `;
        });

        html += '<button class="btn-primary" id="dcf-recalc-btn" style="width:100%; margin-top:12px;">Recalculate</button>';

        document.getElementById('dcf-inputs').innerHTML = html;

        // Bind slider events
        fields.forEach(f => {
            const slider = document.getElementById(`dcf-${f.key}`);
            slider.addEventListener('input', () => {
                const v = parseFloat(slider.value);
                const display = f.fmt === 'pct' ? (v * 100).toFixed(1) + '%' : Math.round(v);
                document.getElementById(`dcf-val-${f.key}`).textContent = display;
                this.assumptions[f.key] = v;
            });
        });

        document.getElementById('dcf-recalc-btn').addEventListener('click', () => this.recalculate());
    },

    async recalculate() {
        if (!this.currentTicker || !this.assumptions) return;

        const btn = document.getElementById('dcf-recalc-btn');
        btn.textContent = 'Calculating...';
        btn.disabled = true;

        try {
            const res = await fetch(`/api/valuation/dcf/${this.currentTicker}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.assumptions),
            });
            if (!res.ok) throw new Error('Failed');
            const data = await res.json();
            this.renderResults(data);
        } catch (e) {
            console.error('DCF recalculation failed:', e);
        } finally {
            btn.textContent = 'Recalculate';
            btn.disabled = false;
        }
    },

    renderResults(data) {
        this.renderFairValue(data);
        this.renderProjections(data.projections);
        this.renderSensitivity(data.sensitivity, data.current_price);
    },

    renderFairValue(data) {
        const el = document.getElementById('dcf-fair-value');
        const upside = data.current_price
            ? ((data.fair_value - data.current_price) / data.current_price * 100).toFixed(1)
            : null;
        const upsideClass = upside > 0 ? 'upside' : 'downside';
        const upsideSign = upside > 0 ? '+' : '';

        el.innerHTML = `
            <div class="fv-item">
                <div class="fv-label">Fair Value</div>
                <div class="fv-value">$${data.fair_value.toFixed(2)}</div>
            </div>
            <div class="fv-item">
                <div class="fv-label">Current Price</div>
                <div class="fv-value">${data.current_price ? '$' + data.current_price.toFixed(2) : '--'}</div>
            </div>
            ${upside !== null ? `
            <div class="fv-item">
                <div class="fv-label">Upside/Downside</div>
                <div class="fv-value ${upsideClass}">${upsideSign}${upside}%</div>
            </div>
            ` : ''}
            <div class="fv-item">
                <div class="fv-label">Enterprise Value</div>
                <div class="fv-value">${Utils.formatCurrency(data.enterprise_value)}</div>
            </div>
        `;
    },

    renderProjections(projections) {
        const el = document.getElementById('dcf-projections');
        let html = '<table class="projection-table"><thead><tr>';
        html += '<th>Year</th><th>Revenue</th><th>EBIT</th><th>NOPAT</th><th>FCF</th><th>PV of FCF</th>';
        html += '</tr></thead><tbody>';

        projections.forEach(p => {
            html += `<tr>
                <td>Year ${p.year}</td>
                <td>${Utils.formatCurrency(p.revenue)}</td>
                <td>${Utils.formatCurrency(p.ebit)}</td>
                <td>${Utils.formatCurrency(p.nopat)}</td>
                <td>${Utils.formatCurrency(p.fcf)}</td>
                <td>${Utils.formatCurrency(p.pv_fcf)}</td>
            </tr>`;
        });

        html += '</tbody></table>';
        el.innerHTML = html;
    },

    renderSensitivity(sensitivity, currentPrice) {
        const el = document.getElementById('dcf-sensitivity');
        if (!sensitivity) { el.innerHTML = ''; return; }

        const { wacc_values, terminal_growth_values, matrix } = sensitivity;

        let html = '<table class="sensitivity-table"><thead><tr>';
        html += '<th>WACC \\ TGR</th>';
        terminal_growth_values.forEach(tg => {
            html += `<th>${tg}%</th>`;
        });
        html += '</tr></thead><tbody>';

        matrix.forEach((row, i) => {
            html += `<tr><td class="heat-header">${wacc_values[i]}%</td>`;
            row.forEach(val => {
                if (val === null) {
                    html += '<td class="heat-neutral">N/A</td>';
                } else {
                    const heatClass = this.getHeatClass(val, currentPrice);
                    html += `<td class="${heatClass}">$${val.toFixed(2)}</td>`;
                }
            });
            html += '</tr>';
        });

        html += '</tbody></table>';
        el.innerHTML = html;
    },

    getHeatClass(fairValue, currentPrice) {
        if (!currentPrice) return 'heat-neutral';
        const pctDiff = (fairValue - currentPrice) / currentPrice;
        if (pctDiff > 0.5) return 'heat-strong-green';
        if (pctDiff > 0.25) return 'heat-green';
        if (pctDiff > 0.05) return 'heat-light-green';
        if (pctDiff > -0.05) return 'heat-neutral';
        if (pctDiff > -0.25) return 'heat-light-red';
        if (pctDiff > -0.5) return 'heat-red';
        return 'heat-strong-red';
    },
};
