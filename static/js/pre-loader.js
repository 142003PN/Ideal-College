
document.addEventListener("DOMContentLoaded", () => {
    const loader = document.getElementById("global-preloader");

    // Hide preloader once page fully loaded (normal load)
    window.addEventListener("load", () => {
        loader.style.opacity = "0";
        setTimeout(() => { loader.style.display = "none"; }, 300);
    });

    // FIX: Back button (bfcache restore)
    window.addEventListener("pageshow", (event) => {
        if (event.persisted) {
            loader.style.display = "none";
            loader.style.opacity = "0";
        }
    });

    // Show preloader on form submission
    document.querySelectorAll("form").forEach(form => {
        form.addEventListener("submit", () => {
            loader.style.display = "flex";
            loader.style.opacity = "1";
        });
    });

    // Show preloader on navigation
    document.querySelectorAll("a:not([target='_blank'])").forEach(link => {
        link.addEventListener("click", (e) => {
            const href = link.getAttribute("href");
            if (!href || href.startsWith("#") || href.startsWith("javascript:")) return;

            loader.style.display = "flex";
            loader.style.opacity = "1";
        });
    });
});
