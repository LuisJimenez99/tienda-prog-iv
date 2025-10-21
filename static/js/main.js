document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. CARGAR CARRITO DESDE localStorage ---
    // Intentamos cargar el carrito desde localStorage.
    // JSON.parse convierte el texto guardado de nuevo en un array de JavaScript.
    // Si no hay nada guardado (||), empezamos con un carrito vacío [].
    let cart = JSON.parse(localStorage.getItem('miTiendaCarrito')) || [];

    // --- ELEMENTOS DEL DOM (sin cambios) ---
    const cartIcon = document.querySelector('.nav-carrito');
    const cartCounter = document.querySelector('.cart-counter');
    const miniCart = document.getElementById('mini-cart');
    const miniCartOverlay = document.getElementById('mini-cart-overlay');
    const closeCartBtn = document.getElementById('close-cart-btn');
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    const miniCartItemsContainer = document.getElementById('mini-cart-items');
    const cartTotalPriceEl = document.getElementById('cart-total-price');
    const searchInput = document.querySelector('.search-input');
    const searchResultsContainer = document.getElementById('live-search-results');


    // --- FUNCIONES ---

    // --- 2. FUNCIÓN PARA GUARDAR EL CARRITO ---
    // Esta función convierte nuestro array 'cart' en texto con JSON.stringify
    // y lo guarda en localStorage bajo la clave 'miTiendaCarrito'.
    const saveCartToLocalStorage = () => {
        localStorage.setItem('miTiendaCarrito', JSON.stringify(cart));
    };

    const toggleMiniCart = () => {
        miniCart.classList.toggle('visible');
        miniCartOverlay.classList.toggle('visible');
    };

    const addToCart = (product) => {
        const existingProduct = cart.find(item => item.id === product.id);
        if (existingProduct) {
            existingProduct.quantity++;
        } else {
            cart.push({ ...product, quantity: 1 });
        }
        updateCartDisplay(); // Esta función ahora también guardará el carrito
    };
    
    const updateQuantity = (productId, change) => {
        const product = cart.find(item => item.id === productId);
        if (product) {
            product.quantity += change;
            if (product.quantity <= 0) {
                cart = cart.filter(item => item.id !== productId);
            }
        }
        updateCartDisplay(); // Esta función ahora también guardará el carrito
    };

    const updateCartDisplay = () => {
        miniCartItemsContainer.innerHTML = '';
        let totalItems = 0;
        let totalPrice = 0;

        if (cart.length === 0) {
            miniCartItemsContainer.innerHTML = '<p class="cart-empty-msg">Tu carrito está vacío.</p>';
        } else {
            cart.forEach(item => {
                const itemHTML = `
                    <div class="mini-cart-item">
                        <img src="${item.imagen}" alt="${item.nombre}" class="cart-item-img">
                        <div class="cart-item-details">
                            <p class="cart-item-name">${item.nombre}</p>
                            <p class="cart-item-price">$${parseFloat(item.precio).toFixed(2)}</p>
                            <div class="cart-item-quantity">
                                <button class="quantity-btn" data-id="${item.id}" data-change="-1">-</button>
                                <span>${item.quantity}</span>
                                <button class="quantity-btn" data-id="${item.id}" data-change="1">+</button>
                            </div>
                        </div>
                        <button class="remove-item-btn" data-id="${item.id}">&times;</button>
                    </div>
                `;
                miniCartItemsContainer.innerHTML += itemHTML;
                totalItems += item.quantity;
                totalPrice += item.quantity * parseFloat(item.precio);
            });
        }
        
        cartCounter.textContent = totalItems;
        cartTotalPriceEl.textContent = `$${totalPrice.toFixed(2)}`;
        
        // --- 3. GUARDAMOS EN CADA ACTUALIZACIÓN ---
        // Cada vez que la vista del carrito se actualiza, guardamos el estado actual.
        saveCartToLocalStorage();
    };

    // --- EVENT LISTENERS (sin cambios) ---
    cartIcon.addEventListener('click', toggleMiniCart);
    closeCartBtn.addEventListener('click', toggleMiniCart);
    miniCartOverlay.addEventListener('click', toggleMiniCart);

    addToCartButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const productData = e.target.closest('.add-to-cart-btn').dataset;
            const product = {
                id: productData.id,
                nombre: productData.nombre,
                precio: productData.precio,
                imagen: productData.imagen,
            };
            addToCart(product);
        });
    });
    
    miniCartItemsContainer.addEventListener('click', (e) => {
        const target = e.target;
        if (target.classList.contains('quantity-btn')) {
            const productId = target.dataset.id;
            const change = parseInt(target.dataset.change, 10);
            updateQuantity(productId, change);
        }
        if (target.classList.contains('remove-item-btn')) {
            const productId = target.dataset.id;
            const product = cart.find(item => item.id === productId);
            if (product) updateQuantity(productId, -product.quantity);
        }
    });

    // --- 4. INICIALIZACIÓN ---
    // Al cargar la página, llamamos a esta función una vez para que
    // muestre el contenido del carrito que acabamos de cargar de localStorage.
    updateCartDisplay();


if (searchInput) {
    searchInput.addEventListener('input', () => {
        const query = searchInput.value;

        if (query.length > 2) {
            fetch(`/productos/api/live-search/?q=${query}`)
                .then(response => response.json())
                .then(data => {
                    searchResultsContainer.innerHTML = '';
                    if (data.productos.length > 0) {
                        data.productos.forEach(producto => {
                            const item = document.createElement('a');
                            item.href = producto.url;
                            item.className = 'search-result-item';
                            item.innerHTML = `
                                <img src="${producto.imagen_url}" alt="${producto.nombre}">
                                <span>${producto.nombre}</span>
                            `;
                            searchResultsContainer.appendChild(item);
                        });
                        searchResultsContainer.classList.add('visible');
                    } else {
                        searchResultsContainer.classList.remove('visible');
                    }
                });
        } else {
            searchResultsContainer.classList.remove('visible');
        }
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-wrapper')) {
            searchResultsContainer.classList.remove('visible');
        }
    });
}
});

