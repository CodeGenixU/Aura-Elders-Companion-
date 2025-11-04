export function showStatus(message, tone = 'info') {
    const el = document.getElementById('appStatus');
    if (!el) return;
    const base = 'w-full px-3 py-2';
    const byTone = tone === 'error'
        ? 'bg-red-50 text-red-800 border-b border-red-200'
        : tone === 'warn'
        ? 'bg-amber-50 text-amber-900 border-b border-amber-200'
        : 'bg-emerald-50 text-emerald-900 border-b border-emerald-200';
    el.className = `${byTone} ${base}`;
    el.textContent = message;
    el.style.display = 'block';
}

