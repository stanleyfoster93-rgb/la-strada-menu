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
            languageLabel: "Choose language", categories: "Menu categories",
            subtitle: "Tourist Menu · Tap any dish for details",
            footer: "Please call your waiter to place an order.",
            weight: "Portion", allergens: "Allergens:", noneSpecified: "Not specified",
            noItems: "No items in this category yet.", loadError: "Unable to load the menu.",
            close: "Close dish details", showDetails: "Show details", lei: "lei"
        },
        ro: {
            languageLabel: "Alegeți limba", categories: "Categorii meniu",
            subtitle: "Meniu · Atingeți un preparat pentru detalii",
            footer: "Vă rugăm să chemați chelnerul pentru a comanda.",
            weight: "Cantitate", allergens: "Alergeni:", noneSpecified: "Nespecificați",
            noItems: "Nu există poziții în această categorie.", loadError: "Meniul nu a putut fi încărcat.",
            close: "Închide detaliile preparatului", showDetails: "Afișează detaliile", lei: "lei"
        },
        ru: {
            languageLabel: "Выберите язык", categories: "Категории меню",
            subtitle: "Меню · Нажмите на позицию, чтобы узнать подробности",
            footer: "Чтобы сделать заказ, пожалуйста, позовите официанта.",
            weight: "Порция", allergens: "Аллергены:", noneSpecified: "Не указаны",
            noItems: "В этой категории пока нет позиций.", loadError: "Не удалось загрузить меню.",
            close: "Закрыть описание позиции", showDetails: "Показать описание", lei: "лей"
        }
    };

    let language = getSavedLanguage();
    const currency = "lei";

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
        return value[language] || value.ro || value.en || value.ru || "";
    }

    function displayPrice(item) {
        const rawPrice = item.priceLabel ?? (item.priceMdl == null ? "" : `${item.priceMdl}`);
        return rawPrice ? `${rawPrice} ${translations[language].lei}` : "";
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
        languageButtons.forEach(button => button.setAttribute("aria-pressed", String(button.dataset.lang === language)));
    }

    function renderCategories() {
        categoriesNav.replaceChildren();
        menuData.categories.forEach(category => {
            const button = document.createElement("button");
            const active = category.id === activeCategory.id;
            button.type = "button";
            button.className = `cat-btn${active ? " active" : ""}`;
            button.textContent = getLocalizedValue(category) || category.id;
            button.setAttribute("aria-pressed", String(active));
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
        activeCategory.items.forEach((entry, index) => {
            const [name, portion = "", price = "", description = ""] = entry;
            const item = { id: `${activeCategory.id}-${index + 1}`, name, portion, priceLabel: price, description, allergens: [] };
            const button = document.createElement("button");
            const image = document.createElement("span");
            const info = document.createElement("span");
            const title = document.createElement("span");
            const meta = document.createElement("span");

            button.type = "button";
            button.className = "menu-item menu-item-text-only";
            button.setAttribute("aria-label", `${name}, ${displayPrice(item)}. ${translations[language].showDetails}`);
            image.className = "item-image item-image-placeholder";
            image.setAttribute("aria-hidden", "true");
            info.className = "item-info";
            title.className = "item-name";
            title.textContent = name;
            info.appendChild(title);
            if (description) {
                const detail = document.createElement("span");
                detail.className = "item-description";
                detail.textContent = description;
                info.appendChild(detail);
            }
            meta.className = "item-price";
            meta.textContent = [portion, displayPrice(item)].filter(Boolean).join(" · ");
            button.append(image, info, meta);
            button.addEventListener("click", () => openModal(item, button));
            menuList.appendChild(button);
        });

        if (activeCategory.items.length === 0) showMessage(translations[language].noItems);
    }

    function updateModal() {
        if (!currentItem) return;
        const title = getLocalizedValue(currentItem.name);
        const image = typeof currentItem.image === "string" ? currentItem.image : "";
        modalTitle.textContent = title;
        modalImg.alt = image ? title : "";
        if (image) modalImg.src = image;
        else modalImg.removeAttribute("src");
        modalWeight.textContent = currentItem.portion ? `${translations[language].weight}: ${currentItem.portion}` : "";
        modalPrice.textContent = displayPrice(currentItem);
        modalDesc.textContent = getLocalizedValue(currentItem.description);
        modalBadge.hidden = true;
        modalAllergens.textContent = translations[language].noneSpecified;
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
        if (!data || !Array.isArray(data.categories) || data.categories.length === 0) {
            throw new Error("Menu must contain a non-empty categories array.");
        }
        const ids = new Set();
        data.categories.forEach(category => {
            if (!category || typeof category.id !== "string" || !category.id.trim() || ids.has(category.id) || !Array.isArray(category.items)) {
                throw new Error("Each category needs a unique id and an items array.");
            }
            ids.add(category.id);
            category.items.forEach((entry, index) => {
                if (!Array.isArray(entry) || typeof entry[0] !== "string" || !entry[0].trim() || typeof entry[2] !== "string") {
                    throw new Error(`Invalid menu item in category ${category.id} at position ${index + 1}.`);
                }
            });
        });
    }

    function setLanguage(nextLanguage) {
        if (!Object.hasOwn(translations, nextLanguage)) return;
        language = nextLanguage;
        try { localStorage.setItem("la-strada-language", language); } catch { /* Optional persistence. */ }
        updateStaticText();
        if (menuData) { renderCategories(); renderItems(); }
        if (currentItem) updateModal();
    }

    languageButtons.forEach(button => button.addEventListener("click", () => setLanguage(button.dataset.lang)));
    updateStaticText();

    fetch("menu.json")
        .then(response => {
            if (!response.ok) throw new Error(`Failed to load menu.json: ${response.status}`);
            return response.json();
        })
        .then(data => {
            validateMenu(data);
            menuData = data;
            activeCategory = data.categories[0];
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
