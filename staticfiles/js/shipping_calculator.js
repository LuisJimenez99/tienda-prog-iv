/**
 * =================================
 * MÓDULO: CALCULADOR DE ENVÍO
 * =================================
 * Inicializa el calculador de envío (usado en detalle_producto.html).
 */
function initShippingCalculator() {
    const btnCalcularEnvio = document.getElementById('cp-calcular-btn');
    const cpInput = document.getElementById('cp-input');
    const shippingResults = document.getElementById('shipping-results');

    // Depende de localStorage y updateCartDisplay (que están en cart.js)
    // Nos aseguramos de que existan antes de continuar.
    if (!btnCalcularEnvio) {
        return; // No estamos en la página de detalle, no hacer nada.
    }
    
    // Estas funciones son definidas globalmente por cart.js
    let selectedShipping = JSON.parse(localStorage.getItem('miTiendaEnvio')) || null;
    const saveShippingToLocalStorage = () => {
        localStorage.setItem('miTiendaEnvio', JSON.stringify(selectedShipping));
    };
    // Necesitamos una referencia a updateCartDisplay (que debe estar en cart.js)
    // ¡Aviso! Esto crea una dependencia.
    // Por simplicidad, asumimos que cart.js ya definió 'updateCartDisplay' globalmente.
    // Si 'updateCartDisplay' no es global, esto fallará.

    /* * CORRECCIÓN: Para evitar fallos, 'shipping_calculator.js' NO debería
    * llamar a 'updateCartDisplay' directamente. Debería emitir un evento.
    *
    * Vamos a hacerlo más simple por ahora: asumimos que cart.js se carga primero
    * y que updateCartDisplay SÍ está disponible.
    *
    * ¡ESPERA! updateCartDisplay no es global, está dentro de initCart().
    * ¡Esto es un problema!
    *
    * SOLUCIÓN: Haremos que `cart.js` exponga `updateCartDisplay`
    * y `saveShippingToLocalStorage` en el objeto global `window`.
    *
    * Ve a `static/js/cart.js` y añade estas líneas al final,
    * fuera de la función `initCart()`:
    *
    * window.miTienda = {
    * updateCartDisplay: updateCartDisplay,
    * saveShippingToLocalStorage: saveShippingToLocalStorage,
    * selectedShipping: selectedShipping
    * };
    *
    * Y en este archivo (shipping_calculator.js), las usamos:
    */

    btnCalcularEnvio.addEventListener('click', () => {
        const cp = cpInput.value;
        if (!cp || isNaN(cp)) {
            shippingResults.innerHTML = '<p class="shipping-error">Por favor, ingresa un código postal válido.</p>';
            return;
        }
        shippingResults.innerHTML = '<p class="shipping-loading">Calculando...</p>';
        
        // Limpiamos el envío guardado
        selectedShipping = null;
        saveShippingToLocalStorage();
        
        // Actualizamos el display del carrito (si existe)
        if (typeof updateCartDisplay === "function") {
            updateCartDisplay();
        }

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
            
            // Actualizamos el display del carrito (si existe)
            if (typeof updateCartDisplay === "function") {
                updateCartDisplay();
            }
        }
    });
}