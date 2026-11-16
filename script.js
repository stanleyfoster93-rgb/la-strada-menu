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

    // Загрузка данных из menu.json
    fetch("menu.json")
        .then(response => response.json())
        .then(data => {
            menuData = data;
            activeCategory = data.categories[0];
            renderCategories();
            renderItems();
        })
        .catch(error => console.error("Error loading menu:", error));

    function renderCategories() {
        categoriesNav.innerHTML = "";
        menuData.categories.forEach(category => {
            const btn = document.createElement("button");
            btn.className = `cat-btn ${category === activeCategory ? "active" : ""}`;
            btn.textContent = category;
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
        const filteredItems = menuData.items.filter(item => item.category === activeCategory);

        if (filteredItems.length === 0) {
            menuList.innerHTML = `<p style="text-align:center; color:#9ca3af; margin-top:20px;">No items in this category yet.</p>`;
            return;
        }

        filteredItems.forEach(item => {
            const itemEl = document.createElement("div");
            itemEl.className = "menu-item";
            itemEl.innerHTML = `
                <div class="item-info">
                    <div class="item-name">${item.name}</div>
                    ${item.badge ? `<span class="item-tag">${item.badge}</span>` : ""}
                </div>
                <div class="item-price">${item.priceMdl} MDL</div>
            `;
            itemEl.addEventListener("click", () => openModal(item));
            menuList.appendChild(itemEl);
        });
    }

    function openModal(item) {
        modalImg.src = item.image || "";
        modalTitle.textContent = item.name;
        modalWeight.textContent = `Weight: ${item.weight}`;
        modalPrice.textContent = `${item.priceMdl} MDL`;
        modalDesc.textContent = item.description;
        
        if (item.badge) {
            modalBadge.textContent = item.badge;
            modalBadge.style.display = "block";
        } else {
            modalBadge.style.display = "none";
        }

        if (item.allergens && item.allergens.length > 0) {
            modalAllergens.textContent = item.allergens.join(", ");
        } else {
            modalAllergens.textContent = "None specified";
        }

        modalOverlay.classList.add("active");
    }

    function closeModalHandler() {
        modalOverlay.classList.remove("active");
    }

    closeModal.addEventListener("click", closeModalHandler);
    modalOverlay.addEventListener("click", (e) => {
        if (e.target === modalOverlay) {
            closeModalHandler();
        }
    });
});
