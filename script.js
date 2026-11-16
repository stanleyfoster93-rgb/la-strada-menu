document.addEventListener("DOMContentLoaded", () => {
    let menuData = null;
    let activeCategory = null;
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

    function getLocalizedValue(value, lang = "en") {
        if (typeof value === "string") return value;
        if (!value || typeof value !== "object" || Array.isArray(value)) return "";
        return value[lang] || Object.values(value).find(entry => typeof entry === "string") || "";
    }

    function showMessage(message, isError = false) {
        const paragraph = document.createElement("p");
        paragraph.className = isError ? "menu-message menu-message-error" : "menu-message";
        paragraph.textContent = message;
        menuList.replaceChildren(paragraph);
    }

    function renderCategories() {
        categoriesNav.replaceChildren();

        menuData.categories.forEach(category => {
            const button = document.createElement("button");
            button.type = "button";
            button.className = `cat-btn${category.id === activeCategory.id ? " active" : ""}`;
            button.textContent = category.en || category.id;
            button.setAttribute("aria-pressed", String(category.id === activeCategory.id));
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
            showMessage("No items in this category yet.");
            return;
        }

        items.forEach(item => {
            const button = document.createElement("button");
            const info = document.createElement("span");
            const name = document.createElement("span");
            const price = document.createElement("span");
            const title = getLocalizedValue(item.name);
            const badgeText = getLocalizedValue(item.badge);

            button.type = "button";
            button.className = "menu-item";
            button.setAttribute("aria-label", `${title}, ${item.priceMdl} MDL. Show details`);
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
            button.append(info, price);
            button.addEventListener("click", () => openModal(item, button));
            menuList.appendChild(button);
        });
    }

    function getAllergens(item) {
        if (Array.isArray(item.allergens)) return item.allergens;
        if (Array.isArray(item.allergens?.en)) return item.allergens.en;
        if (Array.isArray(item.allergens?.ro)) return item.allergens.ro;
        return [];
    }

    function openModal(item, trigger) {
        lastFocusedElement = trigger;
        const title = getLocalizedValue(item.name);
        const image = typeof item.image === "string" ? item.image : "";

        modalTitle.textContent = title;
        modalImg.alt = image ? title : "";
        if (image) {
            modalImg.src = image;
        } else {
            modalImg.removeAttribute("src");
        }
        modalWeight.textContent = `Weight: ${item.weight}`;
        modalPrice.textContent = `${item.priceMdl} MDL`;
        modalDesc.textContent = getLocalizedValue(item.description);
        modalBadge.textContent = getLocalizedValue(item.badge);
        modalBadge.hidden = !modalBadge.textContent;
        modalAllergens.textContent = getAllergens(item).join(", ") || "None specified";

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
            if (!categoryIds.has(item.categoryId)) {
                throw new Error(`Menu item ${item.id} references an unknown category.`);
            }
            if (!getLocalizedValue(item.name).trim()) {
                throw new Error(`Menu item ${item.id} is missing a name.`);
            }
            if (!Number.isFinite(item.priceMdl) || item.priceMdl < 0) {
                throw new Error(`Menu item ${item.id} has an invalid price.`);
            }
            if (typeof item.weight !== "string" || !item.weight.trim()) {
                throw new Error(`Menu item ${item.id} is missing its weight.`);
            }
        });
    }

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
            showMessage("Unable to load the menu. Please try again later.", true);
        });

    closeModal.addEventListener("click", closeModalHandler);
    modalOverlay.addEventListener("click", event => {
        if (event.target === modalOverlay) closeModalHandler();
    });
    document.addEventListener("keydown", event => {
        if (event.key === "Escape") closeModalHandler();
    });
});
