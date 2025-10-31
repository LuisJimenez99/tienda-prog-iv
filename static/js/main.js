document.addEventListener('DOMContentLoaded', () => {
    
    /**
     * =================================
     * FUNCIÓN DE ALERTA PERSONALIZADA
     * =================================
     * Muestra una notificación "toast" personalizada en la pantalla.
     * @param {string} message El mensaje que se mostrará.
     * @param {number} duration Duración en milisegundos (default: 3000ms).
     */
/* REEMPLAZA CON ESTA VERSIÓN: */

/**
 * Muestra una notificación "toast" personalizada en la pantalla.
 * @param {string} message El mensaje que se mostrará.
 * @param {number} duration Duración en milisegundos (default: 3000ms).
 * @param {string} type Tipo de alerta: 'error' (default), 'success', o 'info'.
 */
function showCustomAlert(message, duration = 3000, type = 'error') {
  const alertBox = document.getElementById('custom-alert');
  const alertMessage = document.getElementById('custom-alert-message');
  
  if (!alertBox || !alertMessage) {
    console.error("No se encontró el HTML de la alerta personalizada.");
    alert(message); // Fallback al alert viejo
    return;
  }

  // 1. Limpiamos clases de color antiguas
  alertBox.classList.remove('success', 'info', 'error'); 

  // 2. Añadimos la clase de color correcta
  if (type === 'success') {
    alertBox.classList.add('success');
  } else if (type === 'info') {
    alertBox.classList.add('info');
  } else {
    // Si no es 'success' o 'info', será 'error' (el default)
    // No hace falta añadir 'error' porque el CSS base ya es rojo
  }

  // 3. Pone el mensaje y la muestra
  alertMessage.textContent = message;
  alertBox.classList.add('visible');

  // 4. Oculta la alerta después de la duración especificada
  setTimeout(() => {
    alertBox.classList.remove('visible');
  }, duration);
}

    /* =================================
        1. LÓGICA DEL CARRITO DE COMPRAS
        ================================= */
    
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

    /* REEMPLAZA CON ESTA VERSIÓN: */
const addToCart = (product) => {
    const existingProduct = cart.find(item => item.id === product.id);
    if (existingProduct) {
        existingProduct.quantity++;
    } else {
        cart.push({ ...product, quantity: 1 });
    }
    updateCartDisplay();
    
    // --- ¡LÍNEA AÑADIDA! ---
    // (Usamos 2500ms y el tipo 'info' para que use el color de tu marca)
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
                // --- ¡CAMBIO AQUÍ! ---
                showCustomAlert('Tu carrito está vacío.');
                // --- FIN DEL CAMBIO ---
                return;
            }
            btnCheckout.textContent = 'Procesando...';
            btnCheckout.disabled = true;

            fetch('/carrito/api/crear-pedido/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
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
                    // --- ¡CAMBIO AQUÍ! ---
                    showCustomAlert(data.error || 'Hubo un error al crear el pedido.');
                    // --- FIN DEL CAMBIO ---
                    if (data.redirect_url) { window.location.href = data.redirect_url; }
                    btnCheckout.textContent = 'Finalizar Compra';
                    btnCheckout.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error al finalizar compra:', error);
                // --- ¡CAMBIO AQUÍ! ---
                showCustomAlert(`Error: ${error.message || 'Error de conexión.'}`);
                // --- FIN DEL CAMBIO ---
                btnCheckout.textContent = 'Finalizar Compra';
                btnCheckout.disabled = false;
            });
        });
    }

    /* =================================
        2. LÓGICA DE BÚSQUEDA PREDICTIVA
        ================================= */
    const searchInput = document.querySelector('.search-input');
    const searchResultsContainer = document.getElementById('live-search-results');

    if (searchInput && searchResultsContainer) {
        searchInput.addEventListener('input', () => {
            const query = searchInput.value;
            if (query.length > 2) {
                fetch(`/productos/api/live-search/?q=${query}`)
                    .then(response => response.json())
                    .then(data => {
                        searchResultsContainer.innerHTML = ''; 
                        if (data.productos && data.productos.length > 0) {
                            data.productos.forEach(producto => {
                                const item = document.createElement('a');
                                item.href = producto.url;
                                item.className = 'search-result-item';
                                item.innerHTML = `
                                    <img src="${producto.imagen_url || ''}" alt="${producto.nombre}"> 
                                    <span>${producto.nombre}</span>
                                `;
                                searchResultsContainer.appendChild(item);
                            });
                            searchResultsContainer.classList.add('visible');
                        } else {
                            searchResultsContainer.classList.remove('visible');
                        }
                    })
                    .catch(error => {
                        console.error('Error al obtener sugerencias:', error);
                        searchResultsContainer.innerHTML = '';
                        searchResultsContainer.classList.remove('visible');
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

    /* =================================
        3. LÓGICA DEL CALCULADOR DE ENVÍO
        ================================= */
    const btnCalcularEnvio = document.getElementById('cp-calcular-btn');
    const cpInput = document.getElementById('cp-input');
    const shippingResults = document.getElementById('shipping-results');

    if (btnCalcularEnvio) {
        btnCalcularEnvio.addEventListener('click', () => {
            const cp = cpInput.value;
            if (!cp || isNaN(cp)) {
                shippingResults.innerHTML = '<p class="shipping-error">Por favor, ingresa un código postal válido.</p>';
                return;
            }
            shippingResults.innerHTML = '<p class="shipping-loading">Calculando...</p>';
            
            selectedShipping = null;
            saveShippingToLocalStorage();
            updateCartDisplay();

            fetch(`/envios/api/calcular-envio/?cp=${cp}`)
                .then(response => response.json().then(data => ({ok: response.ok, data})))
                .then(({ok, data}) => {
                    shippingResults.innerHTML = '';
                    if (ok && data.metodos && data.metodos.length > 0) {
                        let html = '<ul>';
                        data.metodos.forEach(metodo => {
                            const precioNum = parseFloat(metodo.precio.replace('$', '').replace(/\./g, '').replace(',', '.'));
                            html += `
                                <li class="shipping-option" data-nombre="${metodo.nombre}" data-precio="${precioNum}">
                                    <span class="shipping-name">${metodo.nombre} (${metodo.descripcion})</span>
                                    <span class="shipping-price">${metodo.precio}</span>
                                </li>
                            `;
                        });
                        html += '</ul>';
                        shippingResults.innerHTML = html;
                    } else {
                         shippingResults.innerHTML = `<p class="shipping-error">${data.error || 'No hay envíos para este CP.'}</p>`;
                    }
                })
                .catch(error => {
                    console.error('Error al calcular envío:', error);
                    shippingResults.innerHTML = `<p class="shipping-error">${error.message}</p>`;
                });
        });
    }

    if (shippingResults) {
        shippingResults.addEventListener('click', (e) => {
            const opcionClickeada = e.target.closest('.shipping-option');
            if (opcionClickeada) {
                shippingResults.querySelectorAll('.shipping-option').forEach(el => el.classList.remove('seleccionado'));
                opcionClickeada.classList.add('seleccionado');
                selectedShipping = {
                    nombre: opcionClickeada.dataset.nombre,
                    precio: opcionClickeada.dataset.precio
                };
                saveShippingToLocalStorage();
                updateCartDisplay();
            }
        });
    }
    
    /* =================================
        4. LÓGICA DEL CARRUSEL (CORREGIDA)
        ================================= */
    const carrusel = document.getElementById('mi-carrusel');
    
    if (carrusel) {
        const items = carrusel.querySelectorAll('.carrusel-item');
        const dots = carrusel.querySelectorAll('.indicator-dot');
        const prevBtn = carrusel.querySelector('.carrusel-control.prev');
        const nextBtn = carrusel.querySelector('.carrusel-control.next');
        let currentIndex = 0;
        let autoSlideInterval;

        function showSlide(index) {
            if (items.length === 0) return; // No hacer nada si no hay items
            
            if (index >= items.length) {
                currentIndex = 0;
            } else if (index < 0) {
                currentIndex = items.length - 1;
            } else {
                currentIndex = index;
            }

            items.forEach(item => item.classList.remove('active'));
            dots.forEach(dot => dot.classList.remove('active'));

            if (items[currentIndex]) {
                items[currentIndex].classList.add('active');
            }
            if (dots[currentIndex]) {
                dots[currentIndex].classList.add('active');
            }
        }

        function nextSlide() {
            showSlide(currentIndex + 1);
        }

        function prevSlide() {
            showSlide(currentIndex - 1);
        }

        function startAutoSlide() {
            stopAutoSlide(); 
            if (items.length > 1) {
                autoSlideInterval = setInterval(nextSlide, 5000); // Cambia cada 5 segundos
            }
        }

        function stopAutoSlide() {
            clearInterval(autoSlideInterval);
        }

        if (prevBtn && nextBtn) {
            prevBtn.addEventListener('click', () => {
                stopAutoSlide();
                prevSlide();
                startAutoSlide(); 
            });
    
            nextBtn.addEventListener('click', () => {
                stopAutoSlide();
                nextSlide();
                startAutoSlide(); 
            });
        }

        dots.forEach(dot => {
            dot.addEventListener('click', (e) => {
                stopAutoSlide();
                const slideTo = parseInt(e.target.dataset.slideTo);
                showSlide(slideTo);
                startAutoSlide(); 
            });
        });

        showSlide(currentIndex); 
        startAutoSlide(); 

        carrusel.addEventListener('mouseenter', stopAutoSlide);
        carrusel.addEventListener('mouseleave', startAutoSlide);
    }
    
    // --- INICIALIZACIÓN FINAL ---
    updateCartDisplay(); // Muestra el carrito al cargar la página

}); // Fin del DOMContentLoaded