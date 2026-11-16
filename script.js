document.addEventListener("DOMContentLoaded", () => {
    let menuData = null;
    let activeCategory = null;

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
        if (!value) return "";

        if (typeof value === "string") return value;

        if (typeof value === "object") {
            if (value[lang]) return value[lang];
            const fallback = Object.values(value)[0];
            return fallback ?? "";
        }

        return "";
    }

    function renderCategories() {
        categoriesNav.innerHTML = "";

        menuData.categories.forEach(category => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = `cat-btn ${category.id === activeCategory?.id ? "active" : ""}`;
            btn.textContent = getLocalizedValue({ en: category.en, ro: category.ro }, "en") || category.id;

            btn.addEventListener("click", () => {
                activeCategory = category;
                renderCategories();
                renderItems();
            });

            categoriesNav.appendChild(btn);
        });
    }

    function renderItems() {
        menuList.innerHTML = "";

        const filteredItems = menuData.items.filter(item => item.categoryId === activeCategory.id);

        if (filteredItems.length === 0) {
            menuList.innerHTML = `<p style="text-align:center; color:#9ca3af; margin-top:20px;">No items in this category yet.</p>`;
            return;
        }

        filteredItems.forEach(item => {
            const itemEl = document.createElement("div");
            const itemName = getLocalizedValue(item.name, "en");
            const badgeText = getLocalizedValue(item.badge, "en");

            itemEl.className = "menu-item";
            itemEl.innerHTML = `
                <div class="item-info">
                    <div class="item-name">${itemName}</div>
                    ${badgeText ? `<span class="item-tag">${badgeText}</span>` : ""}
                </div>
                <div class="item-price">${Number(item.priceMdl || 0)} MDL</div>
            `;

            itemEl.addEventListener("click", () => openModal(item));
            menuList.appendChild(itemEl);
        });
    }

    function openModal(item) {
        const title = getLocalizedValue(item.name, "en");
        const description = getLocalizedValue(item.description, "en");
        const badgeText = getLocalizedValue(item.badge, "en");

        const allergens = Array.isArray(item.allergens)
            ? item.allergens
            : Array.isArray(item.allergens?.en)
                ? item.allergens.en
                : Array.isArray(item.allergens?.ro)
                    ? item.allergens.ro
                    : [];

        modalImg.src = item.image || "";
        modalImg.alt = title;
        modalTitle.textContent = title;
        modalWeight.textContent = `Weight: ${item.weight || "N/A"}`;
        modalPrice.textContent = `${Number(item.priceMdl || 0)} MDL`;
        modalDesc.textContent = description;

        if (badgeText) {
            modalBadge.textContent = badgeText;
            modalBadge.style.display = "block";
        } else {
            modalBadge.style.display = "none";
        }

        if (allergens.length > 0) {
            modalAllergens.textContent = allergens.join(", ");
        } else {
            modalAllergens.textContent = "None specified";
        }

        modalOverlay.classList.add("active");
    }

    function closeModalHandler() {
        modalOverlay.classList.remove("active");
    }

    fetch("menu.json")
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to load menu.json: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            menuData = data;

            if (!Array.isArray(menuData.categories) || !Array.isArray(menuData.items)) {
                throw new Error("Invalid menu data structure.");
            }

            activeCategory = menuData.categories[0];
            renderCategories();
            renderItems();
        })
        .catch(error => {
            console.error("Error loading menu:", error);
            menuList.innerHTML = `<p style="text-align:center; color:#fca5a5; margin-top:20px;">Unable to load the menu.</p>`;
        });

    closeModal.addEventListener("click", closeModalHandler);
    modalOverlay.addEventListener("click", (e) => {
        if (e.target === modalOverlay) {
            closeModalHandler();
        }
    });
});
