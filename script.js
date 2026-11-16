document.addEventListener("DOMContentLoaded", () => {
    let menuData = null;
    let activeCategory = null;
    let currentItem = null;
    let lastFocusedElement = null;

    const categoriesNav = document.getElementById("categoriesNav");
    const menuList = document.getElementById("menuList");
    const modalOverlay = document.getElementById("modalOverlay");
    const closeModal = document.getElementById("closeModal");
    const modalImg = document.getElementById("modalImg");
    const modalBadge = document.getElementById("modalBadge");
    const modalTitle = document.getElementById("modalTitle");
    const modalWeight = document.getElementById("modalWeight");
    const modalPrice = document.getElementById("modalPrice");
    const modalDesc = document.getElementById("modalDesc");
    const modalAllergens = document.getElementById("modalAllergens");
    const languageButtons = document.querySelectorAll("[data-lang]");

    const translations = {
        en: {
            languageLabel: "Choose language",
            categories: "Menu categories",
            subtitle: "Tourist Menu · Tap any dish for details",
            footer: "Please call your waiter to place an order.",
            weight: "Weight",
            allergens: "Allergens:",
            noneSpecified: "None specified",
            noItems: "No items in this category yet.",
            loadError: "Unable to load the menu. Please try again later.",
            close: "Close dish details",
            showDetails: "Show details"
        },
        ro: {
            languageLabel: "Alegeți limba",
            categories: "Categorii meniu",
            subtitle: "Meniu turistic · Atingeți un preparat pentru detalii",
            footer: "Vă rugăm să chemați chelnerul pentru a comanda.",
            weight: "Gramaj",
            allergens: "Alergeni:",
            noneSpecified: "Nespecificați",
            noItems: "Nu există preparate în această categorie.",
            loadError: "Meniul nu a putut fi încărcat. Încercați din nou mai târziu.",
            close: "Închide detaliile preparatului",
            showDetails: "Afișează detaliile"
        },
        ru: {
            languageLabel: "Выберите язык",
            categories: "Категории меню",
            subtitle: "Меню для гостей · Нажмите на блюдо, чтобы узнать подробности",
            footer: "Чтобы сделать заказ, пожалуйста, позовите официанта.",
            weight: "Вес",
            allergens: "Аллергены:",
            noneSpecified: "Не указаны",
            noItems: "В этой категории пока нет блюд.",
            loadError: "Не удалось загрузить меню. Попробуйте позже.",
            close: "Закрыть описание блюда",
            showDetails: "Показать описание"
        }
    };

    let language = getSavedLanguage();

    function getSavedLanguage() {
        try {
            const saved = localStorage.getItem("la-strada-language");
            return Object.hasOwn(translations, saved) ? saved : "en";
        } catch {
            return "en";
        }
    }

    function getLocalizedValue(value) {
        if (typeof value === "string") return value;
        if (!value || typeof value !== "object" || Array.isArray(value)) return "";
        return value[language] || value.en || value.ro || value.ru || "";
    }

    function getAllergens(item) {
        if (Array.isArray(item.allergens)) return item.allergens;
        if (Array.isArray(item.allergens?.[language])) return item.allergens[language];
        return item.allergens?.en || item.allergens?.ro || item.allergens?.ru || [];
    }

    function showMessage(message, isError = false) {
        const paragraph = document.createElement("p");
        paragraph.className = isError ? "menu-message menu-message-error" : "menu-message";
        paragraph.textContent = message;
        menuList.replaceChildren(paragraph);
    }

    function updateStaticText() {
        const text = translations[language];
        document.documentElement.lang = language;
        document.getElementById("languageSwitch").setAttribute("aria-label", text.languageLabel);
        categoriesNav.setAttribute("aria-label", text.categories);
        document.getElementById("subtitle").textContent = text.subtitle;
        document.getElementById("footerText").textContent = text.footer;
        document.getElementById("allergensLabel").textContent = text.allergens;
        closeModal.setAttribute("aria-label", text.close);

        languageButtons.forEach(button => {
            button.setAttribute("aria-pressed", String(button.dataset.lang === language));
        });
    }

    function renderCategories() {
        categoriesNav.replaceChildren();

        menuData.categories.forEach(category => {
            const button = document.createElement("button");
            const isActive = category.id === activeCategory.id;
            button.type = "button";
            button.className = `cat-btn${isActive ? " active" : ""}`;
            button.textContent = getLocalizedValue(category) || category.id;
            button.setAttribute("aria-pressed", String(isActive));
            button.addEventListener("click", () => {
                activeCategory = category;
                renderCategories();
                renderItems();
            });
            categoriesNav.appendChild(button);
        });
    }

    function renderItems() {
        menuList.replaceChildren();
        const items = menuData.items.filter(item => item.categoryId === activeCategory.id);

        if (items.length === 0) {
            showMessage(translations[language].noItems);
            return;
        }

        items.forEach(item => {
            const button = document.createElement("button");
            const image = document.createElement("img");
            const info = document.createElement("span");
            const name = document.createElement("span");
            const price = document.createElement("span");
            const title = getLocalizedValue(item.name);
            const badgeText = getLocalizedValue(item.badge);

            button.type = "button";
            button.className = "menu-item";
            button.setAttribute("aria-label", `${title}, ${item.priceMdl} MDL. ${translations[language].showDetails}`);

            image.className = "item-image";
            image.alt = "";
            image.loading = "lazy";
            image.decoding = "async";
            if (typeof item.image === "string" && item.image) {
                image.src = item.image;
                image.addEventListener("error", () => image.classList.add("image-unavailable"), { once: true });
            } else {
                image.classList.add("image-unavailable");
            }

            info.className = "item-info";
            name.className = "item-name";
            name.textContent = title;
            info.appendChild(name);

            if (badgeText) {
                const badge = document.createElement("span");
                badge.className = "item-tag";
                badge.textContent = badgeText;
                info.appendChild(badge);
            }

            price.className = "item-price";
            price.textContent = `${item.priceMdl} MDL`;
            button.append(image, info, price);
            button.addEventListener("click", () => openModal(item, button));
            menuList.appendChild(button);
        });
    }

    function updateModal() {
        if (!currentItem) return;

        const title = getLocalizedValue(currentItem.name);
        const image = typeof currentItem.image === "string" ? currentItem.image : "";
        const text = translations[language];

        modalTitle.textContent = title;
        modalImg.alt = image ? title : "";
        if (image) {
            modalImg.src = image;
        } else {
            modalImg.removeAttribute("src");
        }
        modalWeight.textContent = `${text.weight}: ${currentItem.weight}`;
        modalPrice.textContent = `${currentItem.priceMdl} MDL`;
        modalDesc.textContent = getLocalizedValue(currentItem.description);
        modalBadge.textContent = getLocalizedValue(currentItem.badge);
        modalBadge.hidden = !modalBadge.textContent;
        modalAllergens.textContent = getAllergens(currentItem).join(", ") || text.noneSpecified;
    }

    function openModal(item, trigger) {
        currentItem = item;
        lastFocusedElement = trigger;
        updateModal();
        modalOverlay.inert = false;
        modalOverlay.setAttribute("aria-hidden", "false");
        modalOverlay.classList.add("active");
        closeModal.focus();
    }

    function closeModalHandler() {
        if (!modalOverlay.classList.contains("active")) return;
        modalOverlay.classList.remove("active");
        modalOverlay.inert = true;
        modalOverlay.setAttribute("aria-hidden", "true");
        currentItem = null;
        if (lastFocusedElement?.isConnected) lastFocusedElement.focus();
    }

    function validateMenu(data) {
        if (!data || !Array.isArray(data.categories) || !Array.isArray(data.items)) {
            throw new Error("Menu must contain categories and items arrays.");
        }
        if (data.categories.length === 0) throw new Error("Menu has no categories.");

        const categoryIds = new Set();
        data.categories.forEach(category => {
            if (!category || typeof category.id !== "string" || !category.id.trim() || categoryIds.has(category.id)) {
                throw new Error("Every category must have a unique, non-empty string id.");
            }
            categoryIds.add(category.id);
        });

        const itemIds = new Set();
        data.items.forEach(item => {
            if (!item || (typeof item.id !== "string" && typeof item.id !== "number") || itemIds.has(item.id)) {
                throw new Error("Every menu item must have a unique id.");
            }
            itemIds.add(item.id);
            if (!categoryIds.has(item.categoryId)) throw new Error(`Menu item ${item.id} references an unknown category.`);
            if (!getLocalizedValue(item.name).trim()) throw new Error(`Menu item ${item.id} is missing a name.`);
            if (!Number.isFinite(item.priceMdl) || item.priceMdl < 0) throw new Error(`Menu item ${item.id} has an invalid price.`);
            if (typeof item.weight !== "string" || !item.weight.trim()) throw new Error(`Menu item ${item.id} is missing its weight.`);
        });
    }

    function setLanguage(nextLanguage) {
        if (!Object.hasOwn(translations, nextLanguage)) return;
        language = nextLanguage;
        try {
            localStorage.setItem("la-strada-language", language);
        } catch {
            // Language switching still works when storage is unavailable.
        }
        updateStaticText();
        if (menuData) {
            renderCategories();
            renderItems();
        }
        if (currentItem) updateModal();
    }

    languageButtons.forEach(button => {
        button.addEventListener("click", () => setLanguage(button.dataset.lang));
    });

    updateStaticText();

    fetch("menu.json")
        .then(response => {
            if (!response.ok) throw new Error(`Failed to load menu.json: ${response.status}`);
            return response.json();
        })
        .then(data => {
            validateMenu(data);
            menuData = data;
            activeCategory = menuData.categories[0];
            renderCategories();
            renderItems();
        })
        .catch(error => {
            console.error("Error loading menu:", error);
            showMessage(translations[language].loadError, true);
        });

    closeModal.addEventListener("click", closeModalHandler);
    modalOverlay.addEventListener("click", event => {
        if (event.target === modalOverlay) closeModalHandler();
    });
    document.addEventListener("keydown", event => {
        if (event.key === "Escape") closeModalHandler();
    });
});
