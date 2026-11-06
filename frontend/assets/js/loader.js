/**
 * OutbreakWatch Flight Line Page Loader
 * Ministry of Health, The Gambia
 */

function dismissLoader() {
    const loader = document.getElementById('page-loader');
    if (!loader) return;
    loader.classList.add('opacity-0', 'pointer-events-none', 'scale-102');
    setTimeout(() => {
        loader.style.display = 'none';
    }, 600);
}

function runPageLoaderAnimation() {
    const line = document.getElementById('loader-line') || document.getElementById('loader-bar') || document.getElementById('loader-progress-bar');
    const percent = document.getElementById('loader-percent');
    const status = document.getElementById('loader-status');
    if (!line) return;

    let progress = 0;
    const intervalTime = 30; // 50 steps * 30ms = 1500ms
    const timer = setInterval(() => {
        progress += 2;
        if (progress > 100) progress = 100;
        
        line.style.width = `${progress}%`;
        if (percent) percent.textContent = `${Math.round(progress)}%`;

        if (status) {
            if (progress < 30) {
                status.textContent = "Connecting to Port Health Network...";
            } else if (progress < 65) {
                status.textContent = "Verifying Clearance Gateway...";
            } else if (progress < 90) {
                status.textContent = "Synchronizing System Protocols...";
            } else {
                status.textContent = "Clearance Gateway Ready • Welcome";
            }
        }

        if (progress >= 100) {
            clearInterval(timer);
            setTimeout(dismissLoader, 300);
        }
    }, intervalTime);
}

document.addEventListener('DOMContentLoaded', () => {
    runPageLoaderAnimation();
});
