/**
 * =================================
 * ARCHIVO PRINCIPAL (INICIALIZADOR)
 * =================================
 */

/**
 * Obtiene el token CSRF de la página.
 * (Necesario para las peticiones POST de fetch)
 */
function getCsrfToken() {
    const tokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (tokenInput) {
        return tokenInput.value;
    }
    console.error('¡Token CSRF no encontrado en el DOM!');
    return '';
}

/**
 * Inicializador principal
 * Se ejecuta cuando el DOM está listo.
 */
document.addEventListener('DOMContentLoaded', () => {
    
    // --- Módulos Globales (se ejecutan en todas las páginas) ---
    // (Asumimos que notifications.js, cart.js y search.js se cargan ANTES que main.js)
    
    if (typeof initCart === "function") {
        initCart();
    } else {
        console.error("Módulo de Carrito (cart.js) no se cargó.");
    }
    
    if (typeof initSearch === "function") {
        initSearch();
    } else {
        console.error("Módulo de Búsqueda (search.js) no se cargó.");
    }

    // --- Módulos Específicos (solo se ejecutan si sus funciones existen) ---
    
    if (typeof initShippingCalculator === "function") {
        initShippingCalculator();
    }
    
    if (typeof initCarousel === "function") {
        initCarousel();
    }

    // Nota: showCustomAlert() ya existe globalmente desde notifications.js
});