document.addEventListener("DOMContentLoaded", () => {
            const loader = document.getElementById("preloader");

            /* Hide on normal load */
            window.addEventListener("load", () => {
                loader.classList.add("hidden");
                setTimeout(() => loader.style.display = "none", 300);
            });

            /* Back button fix */
            window.addEventListener("pageshow", (event) => {
                if (event.persisted) {
                    loader.style.display = "none";
                    loader.classList.add("hidden");
                }
            });

            /* Show only on REAL navigation */
            const safeAreas = [
                ".sidebar", 
                ".dropdown-menu", 
                ".dropdown-toggle",
                ".nav-link",
                ".submenu a",
                ".delete-btn",
            ];

            function isInsideSafeArea(el) {
                return safeAreas.some(selector => el.closest(selector));
            }

            /* LINKS */
            document.querySelectorAll("a:not([target='_blank'])").forEach(link => {
                link.addEventListener("click", (e) => {
                    const href = link.getAttribute("href");

                    // Skip JS links, anchors, empty links, or sidebar/dropdown
                    if (!href || href.startsWith("#") || href.startsWith("javascript")) return;

                    if (isInsideSafeArea(link)) return;

                    loader.style.display = "flex";
                    loader.classList.remove("hidden");
                });
            });

            /* FORMS */
            document.querySelectorAll("form").forEach(form => {
                form.addEventListener("submit", () => {
                    loader.style.display = "flex";
                    loader.classList.remove("hidden");
                });
            });

        });