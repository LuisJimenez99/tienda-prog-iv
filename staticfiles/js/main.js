document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. CARGAR CARRITO DESDE localStorage ---
    let cart = JSON.parse(localStorage.getItem('miTiendaCarrito')) || [];

    // --- ELEMENTOS DEL DOM ---
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
    const btnCheckout = document.querySelector('.btn-checkout'); // Botón en el mini-carrito

    // --- FUNCIONES DEL CARRITO ---
    const saveCartToLocalStorage = () => {
        localStorage.setItem('miTiendaCarrito', JSON.stringify(cart));
    };

    const toggleMiniCart = () => {
        if (miniCart && miniCartOverlay) { // Verificar si existen los elementos
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

    const updateCartDisplay = () => {
        // Verificar si los elementos del carrito existen antes de usarlos
        if (!miniCartItemsContainer || !cartCounter || !cartTotalPriceEl) return; 

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

    // --- EVENT LISTENER PARA FINALIZAR COMPRA (PRODUCTOS) ---
    if (btnCheckout) {
        btnCheckout.addEventListener('click', (e) => {
            e.preventDefault(); 
            if (cart.length === 0) {
                alert('Tu carrito está vacío.');
                return;
            }
            btnCheckout.textContent = 'Procesando...';
            btnCheckout.disabled = true;

            fetch('/carrito/api/crear-pedido/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cart: cart })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(errData => { throw new Error(errData.error || `Error ${response.status}`); });
                }
                return response.json();
            })
            .then(data => {
                if (data.success && data.redirect_url) {
                    cart = [];
                    saveCartToLocalStorage(); 
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

    // --- LÓGICA PARA LA BÚSQUEDA EN VIVO ---
    if (searchInput && searchResultsContainer) { // Verificar si existen ambos elementos
        searchInput.addEventListener('input', () => {
            const query = searchInput.value;
            if (query.length > 2) {
                fetch(`/productos/api/live-search/?q=${query}`)
                    .then(response => response.json())
                    .then(data => {
                        searchResultsContainer.innerHTML = ''; 
                        if (data.productos && data.productos.length > 0) { // Verificar si hay productos
                            data.productos.forEach(producto => {
                                const item = document.createElement('a');
                                item.href = producto.url;
                                item.className = 'search-result-item';
                                item.innerHTML = `
                                    <img src="${producto.imagen_url || ''}" alt="${producto.nombre}"> 
                                    <span>${producto.nombre}</span>
                                `; // Añadir fallback para imagen_url
                                searchResultsContainer.appendChild(item);
                            });
                            searchResultsContainer.classList.add('visible');
                        } else {
                            searchResultsContainer.classList.remove('visible');
                        }
                    })
                    .catch(error => {
                        // --- CORRECCIÓN AQUÍ: Manejo de error específico para la búsqueda ---
                        console.error('Error al obtener sugerencias:', error);
                        searchResultsContainer.innerHTML = ''; // Limpiar en caso de error
                        searchResultsContainer.classList.remove('visible');
                    });
            } else {
                searchResultsContainer.classList.remove('visible');
            }
        });

        // Ocultar resultados si se hace clic fuera del buscador
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-wrapper')) { 
                searchResultsContainer.classList.remove('visible');
            }
        });
    }

    // --- INICIALIZACIÓN FINAL ---
    updateCartDisplay(); // Muestra el carrito al cargar la página

}); // Fin del DOMContentLoaded

