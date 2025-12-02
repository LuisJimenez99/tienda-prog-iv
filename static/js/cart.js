/**
 * =================================
 * MÓDULO: CARRITO DE COMPRAS
 * =================================
 * Inicializa toda la funcionalidad del mini-carrito y el checkout.
 */
function initCart() {
    
    // --- Cargar Carrito desde localStorage ---
    let cart = JSON.parse(localStorage.getItem('miTiendaCarrito')) || [];
    
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
    
    // --- FUNCIÓN CLAVE: ACTUALIZAR VISUALIZACIÓN ---
    const updateCartDisplay = () => {
        if (!miniCartItemsContainer || !cartCounter || !cartTotalPriceEl) return; 

        // 1. LEER ENVÍO FRESCO DESDE MEMORIA
        // Esto asegura que si cambiaste el envío en otra parte, el carrito se entere.
        const shippingData = JSON.parse(localStorage.getItem('miTiendaEnvio')) || null;

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
        
        // 2. CALCULAR TOTAL CON ENVÍO
        let shippingPrice = 0;
        
        // Solo mostramos envío si hay items en el carrito Y hay un envío seleccionado
        if (cart.length > 0 && shippingData && cartShippingCostEl) {
            // Limpieza del precio (por si viene como string "$ 5.000,00")
            let precioLimpio = shippingData.precio;
            if (typeof precioLimpio === 'string') {
                 precioLimpio = precioLimpio.replace('$', '').replace(/\./g, '').replace(',', '.').trim();
            }
            shippingPrice = parseFloat(precioLimpio) || 0;

            cartShippingCostEl.innerHTML = `<span>Envío (${shippingData.nombre}):</span> <strong>$${shippingPrice.toFixed(2)}</strong>`;
            cartShippingCostEl.style.display = 'flex';
        } else if (cartShippingCostEl) {
            // Si no hay envío seleccionado, ocultamos esa línea
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

    // --- NUEVA FUNCIÓN: BORRAR ENVÍO ---
    // Esta función permite quitar el envío seleccionado de la memoria y actualizar el total
    // Úsala en shipping_calculator.js cuando el usuario presione "Calcular" de nuevo.
    const resetCartShipping = () => {
        localStorage.removeItem('miTiendaEnvio'); // Borra la memoria
        updateCartDisplay(); // Refresca el carrito visualmente (quita el costo de envío)
    };

    // --- EXPORTAR FUNCIONES GLOBALES ---
    // Hacemos que estas funciones sean visibles para otros scripts
    window.updateCartDisplay = updateCartDisplay;
    window.resetCartShipping = resetCartShipping;

    const toggleMiniCart = () => {
        if (miniCart && miniCartOverlay) {
            miniCart.classList.toggle('visible');
            miniCartOverlay.classList.toggle('visible');
        }
    };

    const addToCart = (product, quantity) => {
        // Aseguramos que la cantidad sea al menos 1
        const quantityToAdd = parseInt(quantity, 10) || 1; 
        const existingProduct = cart.find(item => item.id === product.id);
        
        if (existingProduct) {
            existingProduct.quantity += quantityToAdd;
        } else {
            cart.push({ ...product, quantity: quantityToAdd });
        }
        updateCartDisplay();
        showCustomAlert(`${product.nombre} (x${quantityToAdd}) añadido al carrito`, 2500, 'info');
        
        // Abrir el carrito automáticamente al agregar (Mejora de UX)
        if (miniCart && !miniCart.classList.contains('visible')) {
            toggleMiniCart();
        }
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

    // --- Event Listeners del Carrito ---
    if (cartIcon) cartIcon.addEventListener('click', toggleMiniCart);
    if (closeCartBtn) closeCartBtn.addEventListener('click', toggleMiniCart);
    if (miniCartOverlay) miniCartOverlay.addEventListener('click', toggleMiniCart);

    addToCartButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const btn = e.target.closest('.add-to-cart-btn');
            const productData = btn.dataset;

            // Buscar input de cantidad (Soporte para Detalle y Lista)
            const container = btn.closest('.producto-detalle-container, .tarjeta-producto');
            let quantity = 1;

            if (container) {
                const quantityInput = container.querySelector('.quantity-input');
                if (quantityInput) {
                    quantity = parseInt(quantityInput.value, 10);
                    // Validación extra: si no es número o es menor a 1, usar 1
                    if (isNaN(quantity) || quantity < 1) quantity = 1;
                }
            }

            const product = {
                id: productData.id, nombre: productData.nombre, 
                precio: productData.precio, imagen: productData.imagen,
            };
            addToCart(product, quantity);
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

            const csrftoken = getCsrfToken(); 
            // IMPORTANTE: Leemos el envío justo antes de enviarlo al backend
            const finalShipping = JSON.parse(localStorage.getItem('miTiendaEnvio')) || null;

            fetch('/carrito/api/crear-pedido/', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ 
                    cart: cart,
                    shipping: finalShipping 
                })
            })
            .then(response => response.json().then(data => ({ok: response.ok, data})))
            .then(({ok, data}) => {
                if (ok) {
                    // Limpieza tras compra exitosa
                    cart = [];
                    localStorage.removeItem('miTiendaCarrito');
                    localStorage.removeItem('miTiendaEnvio');
                    window.location.href = data.redirect_url;
                } else {
                    showCustomAlert(data.error || 'Hubo un error al crear el pedido.');
                    // Si el backend nos redirige (ej: perfil incompleto), vamos ahí
                    if (data.redirect_url) window.location.href = data.redirect_url;
                    
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
    updateCartDisplay(); 
}