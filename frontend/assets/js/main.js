/**
 * OutbreakWatch Shared UI Utilities
 */
function showNotification(message, type = 'info') {
    const existing = document.getElementById('toast-container');
    const container = existing || (() => {
        const div = document.createElement('div');
        div.id = 'toast-container';
        div.className = 'fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm';
        document.body.appendChild(div);
        return div;
    })();

    const toast = document.createElement('div');
    const bgColors = {
        success: 'bg-emerald-600 text-white',
        error: 'bg-rose-600 text-white',
        warning: 'bg-amber-600 text-white',
        info: 'bg-slate-800 text-white'
    };

    toast.className = `${bgColors[type] || bgColors.info} px-4 py-3 rounded-lg shadow-lg text-sm flex items-center justify-between transition-all transform duration-300 translate-y-2 opacity-0`;
    toast.innerHTML = `
        <span>${message}</span>
        <button class="ml-3 font-bold text-lg leading-none hover:opacity-80" onclick="this.parentElement.remove()">&times;</button>
    `;

    container.appendChild(toast);
    requestAnimationFrame(() => {
        toast.classList.remove('translate-y-2', 'opacity-0');
    });

    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function getSeverityBadge(severity) {
    const map = {
        critical: 'bg-rose-100 text-rose-800 border-rose-200',
        high: 'bg-amber-100 text-amber-800 border-amber-200',
        medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
        low: 'bg-emerald-100 text-emerald-800 border-emerald-200'
    };
    const cls = map[severity?.toLowerCase()] || 'bg-slate-100 text-slate-800 border-slate-200';
    return `<span class="px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider border ${cls}">${severity || 'Unknown'}</span>`;
}

function getPriorityBadge(priority) {
    const map = {
        emergency: 'bg-red-500 text-white',
        urgent: 'bg-orange-500 text-white',
        routine: 'bg-blue-500 text-white'
    };
    const cls = map[priority?.toLowerCase()] || 'bg-slate-500 text-white';
    return `<span class="px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wide ${cls}">${priority || 'routine'}</span>`;
}

