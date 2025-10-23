document.addEventListener('DOMContentLoaded', () => {

// --- 1. CARGAR DATOS DESDE localStorage ---
let cart = JSON.parse(localStorage.getItem('miTiendaCarrito')) || [];
let selectedShipping = JSON.parse(localStorage.getItem('miTiendaEnvio')) || null;

// --- ELEMENTOS DEL DOM ---
const cartIcon = document.querySelector('.nav-carrito');
const cartCounter = document.querySelector('.cart-counter');
const miniCart = document.getElementById('mini-cart');
const miniCartOverlay = document.getElementById('mini-cart-overlay');
const closeCartBtn = document.getElementById('close-cart-btn');
const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
const miniCartItemsContainer = document.getElementById('mini-cart-items');
const cartTotalPriceEl = document.getElementById('cart-total-price');
const cartShippingCostEl = document.getElementById('cart-shipping-cost'); // Nuevo
const searchInput = document.querySelector('.search-input');
const searchResultsContainer = document.getElementById('live-search-results');
const btnCheckout = document.querySelector('.btn-checkout');

// --- FUNCIONES DEL CARRITO ---
const saveCartToLocalStorage = () => {
    localStorage.setItem('miTiendaCarrito', JSON.stringify(cart));
};

// NUEVA FUNCIÓN PARA GUARDAR ENVÍO
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

// FUNCIÓN DE ACTUALIZAR CARRITO (MODIFICADA)
const updateCartDisplay = () => {
    if (!miniCartItemsContainer || !cartCounter || !cartTotalPriceEl) return; 

    miniCartItemsContainer.innerHTML = '';
    let totalItems = 0;
    let subtotalPrice = 0; // Cambiado a subtotal

    if (cart.length === 0) {
        miniCartItemsContainer.innerHTML = '<p class="cart-empty-msg">Tu carrito está vacío.</p>';
    } else {
        cart.forEach(item => {
            // ... (código para itemHTML sin cambios) ...
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
    
    // --- LÓGICA DE TOTAL CON ENVÍO ---
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
    saveCartToLocalStorage();
};

// --- EVENT LISTENERS DEL CARRITO ---
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
    // ... (código de event listener para quantity-btn y remove-item-btn sin cambios) ...
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

// --- EVENT LISTENER PARA FINALIZAR COMPRA (MODIFICADO) ---
if (btnCheckout) {
    btnCheckout.addEventListener('click', (e) => {
        e.preventDefault(); 
        if (cart.length === 0) {
            alert('Tu carrito está vacío.');
            return;
        }
        btnCheckout.textContent = 'Procesando...';
        btnCheckout.disabled = true;

        // AHORA ENVIAMOS EL CARRITO Y EL ENVÍO
        fetch('/carrito/api/crear-pedido/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                cart: cart,
                shipping: selectedShipping // Enviamos el objeto de envío seleccionado
            })
        })
        .then(response => response.json().then(data => ({ok: response.ok, data})))
        .then(({ok, data}) => {
            if (ok) {
                cart = [];
                selectedShipping = null; // Limpiamos el envío
                saveCartToLocalStorage(); 
                saveShippingToLocalStorage(); // Guardamos el envío limpio
                window.location.href = data.redirect_url;
            } else {
                alert(data.error || 'Hubo un error al crear el pedido.');
                if (data.redirect_url) { window.location.href = data.redirect_url; }
                btnCheckout.textContent = 'Finalizar Compra';
                btnCheckout.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error al finalizar compra:', error);
            alert(`Error: ${error.message}`);
            btnCheckout.textContent = 'Finalizar Compra';
            btnCheckout.disabled = false;
        });
    });
}

// --- LÓGICA PARA LA BÚSQUEDA EN VIVO (sin cambios) ---
if (searchInput && searchResultsContainer) {
    // ... (código de búsqueda predictiva sin cambios) ...
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

// --- LÓGICA DEL CALCULADOR DE ENVÍO (MODIFICADO) ---
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
        
        // Borramos el envío anterior al calcular uno nuevo
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
                        // Extraemos el precio como número
                        const precioNum = parseFloat(metodo.precio.replace('$', '').replace('.', '').replace(',', '.'));
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
                shippingResults.innerHTML = `<p class="shipping-error">Error al calcular. Intenta de nuevo.</p>`;
            });
    });
}

// --- NUEVO EVENT LISTENER PARA SELECCIONAR ENVÍO ---
if (shippingResults) {
    shippingResults.addEventListener('click', (e) => {
        const opcionClickeada = e.target.closest('.shipping-option');
        if (opcionClickeada) {
            // Quitar 'seleccionado' de cualquier otra opción
            shippingResults.querySelectorAll('.shipping-option').forEach(el => el.classList.remove('seleccionado'));
            
            // Añadir 'seleccionado' a la opción clickeada
            opcionClickeada.classList.add('seleccionado');

            // Guardar la selección en la variable global y en localStorage
            selectedShipping = {
                nombre: opcionClickeada.dataset.nombre,
                precio: opcionClickeada.dataset.precio
            };
            saveShippingToLocalStorage();
            
            // Actualizar el mini-carrito para reflejar el nuevo total
            updateCartDisplay();
        }
    });
}

// --- INICIALIZACIÓN FINAL ---
updateCartDisplay();
}); 