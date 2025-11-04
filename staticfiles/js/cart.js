/**
 * =================================
 * MÓDULO: CARRITO DE COMPRAS
 * =================================
 * Inicializa toda la funcionalidad del mini-carrito y el checkout.
 */
function initCart() {
    
    // --- Cargar Carrito y Envío desde localStorage ---
    let cart = JSON.parse(localStorage.getItem('miTiendaCarrito')) || [];
    let selectedShipping = JSON.parse(localStorage.getItem('miTiendaEnvio')) || null;

    // --- Elementos del DOM (Carrito) ---
    const cartIcon = document.querySelector('.nav-carrito');
    const cartCounter = document.querySelector('.cart-counter');
    const miniCart = document.getElementById('mini-cart');
    const miniCartOverlay = document.getElementById('mini-cart-overlay');
    const closeCartBtn = document.getElementById('close-cart-btn');
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    const miniCartItemsContainer = document.getElementById('mini-cart-items');
    const cartTotalPriceEl = document.getElementById('cart-total-price');
    const cartShippingCostEl = document.getElementById('cart-shipping-cost');
    const btnCheckout = document.querySelector('.btn-checkout');

    // --- Funciones del Carrito ---
    const saveCartToLocalStorage = () => {
        localStorage.setItem('miTiendaCarrito', JSON.stringify(cart));
    };
    
    const saveShippingToLocalStorage = () => {
        localStorage.setItem('miTiendaEnvio', JSON.stringify(selectedShipping));
    };

    const toggleMiniCart = () => {
        if (miniCart && miniCartOverlay) {
            miniCart.classList.toggle('visible');
            miniCartOverlay.classList.toggle('visible');
        }
    };

    const addToCart = (product) => {
        const existingProduct = cart.find(item => item.id === product.id);
        if (existingProduct) {
            existingProduct.quantity++;
        } else {
            cart.push({ ...product, quantity: 1 });
        }
        updateCartDisplay();
        
        // Llamada a la notificación global
        showCustomAlert(`${product.nombre} añadido al carrito`, 2500, 'info');
    };
    
    const updateQuantity = (productId, change) => {
        const product = cart.find(item => item.id === productId);
        if (product) {
            product.quantity += change;
            if (product.quantity <= 0) {
                cart = cart.filter(item => item.id !== productId);
            }
        }
        updateCartDisplay();
    };

    const updateCartDisplay = () => {
        if (!miniCartItemsContainer || !cartCounter || !cartTotalPriceEl) return; 

        miniCartItemsContainer.innerHTML = '';
        let totalItems = 0;
        let subtotalPrice = 0;

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
                subtotalPrice += item.quantity * parseFloat(item.precio);
            });
        }
        
        let shippingPrice = 0;
        if (selectedShipping && cartShippingCostEl) {
            shippingPrice = parseFloat(selectedShipping.precio);
            cartShippingCostEl.innerHTML = `<span>Envío:</span> <strong>$${shippingPrice.toFixed(2)}</strong>`;
            cartShippingCostEl.style.display = 'flex';
        } else if (cartShippingCostEl) {
            cartShippingCostEl.style.display = 'none';
        }

        const totalPrice = subtotalPrice + shippingPrice;
        
        cartCounter.textContent = totalItems;
        cartTotalPriceEl.textContent = `$${totalPrice.toFixed(2)}`;

        if (totalItems > 0) {
            cartCounter.classList.add('has-items');
        } else {
            cartCounter.classList.remove('has-items');
        }
        
        saveCartToLocalStorage();
    };

    // --- Event Listeners del Carrito ---
    if (cartIcon) cartIcon.addEventListener('click', toggleMiniCart);
    if (closeCartBtn) closeCartBtn.addEventListener('click', toggleMiniCart);
    if (miniCartOverlay) miniCartOverlay.addEventListener('click', toggleMiniCart);

    addToCartButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const productData = e.target.closest('.add-to-cart-btn').dataset;
            const product = {
                id: productData.id, nombre: productData.nombre, 
                precio: productData.precio, imagen: productData.imagen,
            };
            addToCart(product);
        });
    });
    
    if (miniCartItemsContainer) {
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
    }

    if (btnCheckout) {
        btnCheckout.addEventListener('click', (e) => {
            e.preventDefault(); 
            if (cart.length === 0) {
                showCustomAlert('Tu carrito está vacío.');
                return;
            }
            btnCheckout.textContent = 'Procesando...';
            btnCheckout.disabled = true;

            // ¡IMPORTANTE! Aquí llamamos a la función global para el token CSRF
            const csrftoken = getCsrfToken(); 

            fetch('/carrito/api/crear-pedido/', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken // Token CSRF añadido
                },
                body: JSON.stringify({ 
                    cart: cart,
                    shipping: selectedShipping
                })
            })
            .then(response => response.json().then(data => ({ok: response.ok, data})))
            .then(({ok, data}) => {
                if (ok) {
                    cart = [];
                    selectedShipping = null;
                    saveCartToLocalStorage(); 
                    saveShippingToLocalStorage();
                    window.location.href = data.redirect_url;
                } else {
                    showCustomAlert(data.error || 'Hubo un error al crear el pedido.');
                    if (data.redirect_url) { window.location.href = data.redirect_url; }
                    btnCheckout.textContent = 'Finalizar Compra';
                    btnCheckout.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error al finalizar compra:', error);
                showCustomAlert(`Error: ${error.message || 'Error de conexión.'}`);
                btnCheckout.textContent = 'Finalizar Compra';
                btnCheckout.disabled = false;
            });
        });
    }

    // --- INICIALIZACIÓN FINAL ---
    updateCartDisplay(); // Muestra el carrito al cargar la página
}