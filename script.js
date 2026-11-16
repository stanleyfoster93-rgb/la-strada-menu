document.addEventListener("DOMContentLoaded", () => {
    const LANGUAGES = ["en", "ro", "ru"];
    const TEXT = {
        en: {
            language: "Language", subtitle: "Tourist Menu · Tap any dish for details",
            footer: "Please call your waiter to place an order.", portion: "Portion",
            allergens: "Allergens:", unspecified: "Not specified", noItems: "No items in this category yet.",
            loadError: "Unable to load the menu. Please try again later.", close: "Close dish details",
            details: "View details", currency: "lei"
        },
        ro: {
            language: "Limba", subtitle: "Meniu · Atingeți un preparat pentru detalii",
            footer: "Vă rugăm să chemați chelnerul pentru a comanda.", portion: "Cantitate",
            allergens: "Alergeni:", unspecified: "Nespecificați", noItems: "Nu există poziții în această categorie.",
            loadError: "Meniul nu a putut fi încărcat. Încercați din nou mai târziu.", close: "Închide detaliile preparatului",
            details: "Vezi detaliile", currency: "lei"
        },
        ru: {
            language: "Язык", subtitle: "Меню · Нажмите на блюдо, чтобы узнать подробности",
            footer: "Чтобы сделать заказ, пожалуйста, позовите официанта.", portion: "Порция",
            allergens: "Аллергены:", unspecified: "Не указаны", noItems: "В этой категории пока нет блюд.",
            loadError: "Не удалось загрузить меню. Попробуйте позже.", close: "Закрыть описание блюда",
            details: "Подробнее", currency: "лей"
        }
    };

    const categoriesNav = document.getElementById("categoriesNav");
    const menuList = document.getElementById("menuList");
    const languageSelect = document.getElementById("languageSelect");
    const languageLabel = document.getElementById("languageLabel");
    const subtitle = document.getElementById("subtitle");
    const footerText = document.getElementById("footerText");
    const modalOverlay = document.getElementById("modalOverlay");
    const modalCard = document.getElementById("modalCard");
    const closeModal = document.getElementById("closeModal");
    const modalImageWrap = document.getElementById("modalImageWrap");
    const modalImg = document.getElementById("modalImg");
    const modalBadge = document.getElementById("modalBadge");
    const modalTitle = document.getElementById("modalTitle");
    const modalWeight = document.getElementById("modalWeight");
    const modalPrice = document.getElementById("modalPrice");
    const modalDesc = document.getElementById("modalDesc");
    const allergensLabel = document.getElementById("allergensLabel");
    const modalAllergens = document.getElementById("modalAllergens");
    const allergensBox = document.getElementById("allergensBox");

    let menuData = null;
    let activeCategoryId = null;
    let currentItem = null;
    let lastFocusedElement = null;
    let language = getSavedLanguage();

    languageSelect.value = language;

    function getSavedLanguage() {
        try {
            const saved = localStorage.getItem("la-strada-language");
            return LANGUAGES.includes(saved) ? saved : "en";
        } catch {
            return "en";
        }
    }

    // Accept localized objects, plain strings, and legacy menu rows.
    function localized(value, fallback = "") {
        if (typeof value === "string") return value;
        if (!value || typeof value !== "object" || Array.isArray(value)) return fallback;
        return value[language] || value.ro || value.en || value.ru || fallback;
    }

    function normalizeItem(entry, categoryId, index) {
        if (Array.isArray(entry)) {
            const [name = "", portion = "", price = "", description = ""] = entry;
            return {
                id: `${categoryId}-${index + 1}`,
                name,
                portion,
                price,
                description,
                allergens: [],
                image: "",
                badge: ""
            };
        }
        return {
            ...entry,
            id: entry.id ?? `${categoryId}-${index + 1}`,
            portion: entry.portion ?? entry.weight ?? "",
            price: entry.price ?? entry.priceMdl ?? entry.priceLabel ?? "",
            description: entry.description ?? "",
            allergens: entry.allergens ?? [],
            image: entry.image ?? "",
            badge: entry.badge ?? ""
        };
    }

    function priceText(item) {
        const value = localized(item.price, "");
        return value ? `${value} ${TEXT[language].currency}` : "";
    }

    function allergenText(value) {
        if (Array.isArray(value)) return value.map(part => localized(part, String(part))).join(", ");
        if (value && typeof value === "object") {
            const translated = value[language] ?? value.ro ?? value.en ?? value.ru;
            return Array.isArray(translated) ? translated.join(", ") : (translated || "");
        }
        return typeof value === "string" ? value : "";
    }

    function showMessage(message, isError = false) {
        const paragraph = document.createElement("p");
        paragraph.className = isError ? "state-message state-message-error" : "state-message";
        paragraph.textContent = message;
        menuList.replaceChildren(paragraph);
    }

    function updateStaticText() {
        const text = TEXT[language];
        document.documentElement.lang = language;
        languageLabel.textContent = text.language;
        subtitle.textContent = text.subtitle;
        footerText.textContent = text.footer;
        categoriesNav.setAttribute("aria-label", language === "ru" ? "Категории меню" : language === "ro" ? "Categorii meniu" : "Menu categories");
        closeModal.setAttribute("aria-label", text.close);
        allergensLabel.textContent = text.allergens;
    }

    function renderCategories() {
        categoriesNav.replaceChildren();
        menuData.categories.forEach(category => {
            const button = document.createElement("button");
            const isActive = category.id === activeCategoryId;
            button.type = "button";
            button.className = `cat-btn${isActive ? " active" : ""}`;
            button.textContent = localized(category, category.id);
            button.setAttribute("aria-pressed", String(isActive));
            button.addEventListener("click", () => {
                activeCategoryId = category.id;
                renderCategories();
                renderItems();
            });
            categoriesNav.appendChild(button);
        });
    }

    function renderItems() {
        const category = menuData.categories.find(item => item.id === activeCategoryId);
        if (!category || !Array.isArray(category.items) || category.items.length === 0) {
            showMessage(TEXT[language].noItems);
            return;
        }

        menuList.replaceChildren();
        category.items.forEach((entry, index) => {
            const item = normalizeItem(entry, category.id, index);
            const card = document.createElement("button");
            const bullet = document.createElement("span");
            const info = document.createElement("span");
            const name = document.createElement("span");
            const meta = document.createElement("span");
            const portion = document.createElement("span");
            const price = document.createElement("span");

            card.type = "button";
            card.className = "menu-item";
            card.setAttribute("aria-label", `${localized(item.name)}. ${priceText(item)}. ${TEXT[language].details}`);
            bullet.className = "item-bullet";
            bullet.setAttribute("aria-hidden", "true");
            info.className = "item-info";
            name.className = "item-name";
            name.textContent = localized(item.name, "Menu item");
            info.appendChild(name);

            const description = localized(item.description, "");
            if (description) {
                const detail = document.createElement("span");
                detail.className = "item-description";
                detail.textContent = description;
                info.appendChild(detail);
            }

            const badge = localized(item.badge, "");
            if (badge) {
                const badgeEl = document.createElement("span");
                badgeEl.className = "item-badge";
                badgeEl.textContent = badge;
                info.appendChild(badgeEl);
            }

            meta.className = "item-meta";
            portion.className = "item-weight";
            portion.textContent = localized(item.portion, "");
            price.className = "item-price";
            price.textContent = priceText(item);
            if (portion.textContent) meta.appendChild(portion);
            if (price.textContent) meta.appendChild(price);

            card.append(bullet, info, meta);
            card.addEventListener("click", () => openModal(item, card));
            menuList.appendChild(card);
        });
    }

    function updateModal() {
        if (!currentItem) return;
        const name = localized(currentItem.name, "Menu item");
        const image = typeof currentItem.image === "string" ? currentItem.image : "";
        modalTitle.textContent = name;
        modalWeight.textContent = currentItem.portion ? `${TEXT[language].portion}: ${localized(currentItem.portion)}` : "";
        modalPrice.textContent = priceText(currentItem);
        modalDesc.textContent = localized(currentItem.description, "");

        modalImageWrap.hidden = !image;
        if (image) {
            modalImg.src = image;
            modalImg.alt = name;
        } else {
            modalImg.removeAttribute("src");
            modalImg.alt = "";
        }

        const badge = localized(currentItem.badge, "");
        modalBadge.textContent = badge;
        modalBadge.hidden = !badge;

        const allergens = allergenText(currentItem.allergens);
        modalAllergens.textContent = allergens || TEXT[language].unspecified;
        allergensBox.hidden = !allergens;
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
        if (!data || !Array.isArray(data.categories) || !data.categories.length) {
            throw new Error("Menu must contain at least one category.");
        }
        const ids = new Set();
        data.categories.forEach(category => {
            if (!category || typeof category.id !== "string" || ids.has(category.id) || !Array.isArray(category.items)) {
                throw new Error("Each category must have a unique id and an items array.");
            }
            ids.add(category.id);
            category.items.forEach((entry, index) => {
                if (Array.isArray(entry)) {
                    if (typeof entry[0] !== "string" || entry[2] == null) throw new Error(`Invalid row in ${category.id} at ${index + 1}.`);
                } else if (!entry || typeof entry !== "object" || !entry.name || entry.price == null && entry.priceMdl == null && entry.priceLabel == null) {
                    throw new Error(`Invalid item in ${category.id} at ${index + 1}.`);
                }
            });
        });
    }

    languageSelect.addEventListener("change", () => {
        if (!LANGUAGES.includes(languageSelect.value)) return;
        language = languageSelect.value;
        try { localStorage.setItem("la-strada-language", language); } catch { /* Optional preference. */ }
        updateStaticText();
        if (menuData) {
            renderCategories();
            renderItems();
        }
        if (currentItem) updateModal();
    });

    updateStaticText();
    modalOverlay.inert = true;
    closeModal.addEventListener("click", closeModalHandler);
    modalOverlay.addEventListener("click", event => {
        if (event.target === modalOverlay) closeModalHandler();
    });
    document.addEventListener("keydown", event => {
        if (event.key === "Escape") closeModalHandler();
    });

    fetch("menu.json")
        .then(response => {
            if (!response.ok) throw new Error(`Unable to load menu.json (${response.status}).`);
            return response.json();
        })
        .then(data => {
            validateMenu(data);
            menuData = data;
            activeCategoryId = data.categories[0].id;
            renderCategories();
            renderItems();
        })
        .catch(error => {
            console.error("Menu load error:", error);
            showMessage(TEXT[language].loadError, true);
        });
});
