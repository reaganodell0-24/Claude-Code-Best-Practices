/* Shared utilities */
const Utils = {
    formatNumber(num) {
        if (num == null) return '--';
        if (Math.abs(num) >= 1e12) return (num / 1e12).toFixed(2) + 'T';
        if (Math.abs(num) >= 1e9) return (num / 1e9).toFixed(2) + 'B';
        if (Math.abs(num) >= 1e6) return (num / 1e6).toFixed(2) + 'M';
        if (Math.abs(num) >= 1e3) return (num / 1e3).toFixed(2) + 'K';
        return num.toFixed(2);
    },

    formatCurrency(num) {
        if (num == null) return '--';
        return '$' + Utils.formatNumber(num);
    },

    formatPercent(num) {
        if (num == null) return '--';
        return (num * 100).toFixed(2) + '%';
    },

    formatPriceChange(change, pct) {
        const sign = change >= 0 ? '+' : '';
        return `${sign}${change.toFixed(2)} (${sign}${pct.toFixed(2)}%)`;
    },

    async fetchJSON(url) {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
    },

    debounce(fn, ms) {
        let timer;
        return (...args) => {
            clearTimeout(timer);
            timer = setTimeout(() => fn(...args), ms);
        };
    },

};
