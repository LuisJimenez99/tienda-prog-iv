/**
 * =================================
 * ARCHIVO PRINCIPAL (INICIALIZADOR)
 * =================================
 */

/**
 * Obtiene el token CSRF de la página.
 * (Necesario para las peticiones POST de fetch en Django)
 */
function getCsrfToken() {
    const tokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (tokenInput) {
        return tokenInput.value;
    }
    return '';
}

/**
 * Función para manejar el botón de Favoritos (AJAX)
 * Se llama desde el HTML: onclick="toggleFavorito(this)"
 */
function toggleFavorito(btn) {
    // 1. Obtener ID del dataset (HTML5 data-id)
    const productoId = btn.dataset.id;
    const csrftoken = getCsrfToken();

    // Evitar navegación o comportamientos extraños
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    // Efecto visual inmediato al presionar (Feedback UX: el botón se encoge un poco)
    btn.style.transform = "scale(0.8)";
    setTimeout(() => btn.style.transform = "scale(1)", 200);

    // Llamada al Backend
    fetch(`/productos/api/favorito/${productoId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        },
    })
    .then(response => {
        if (response.status === 401) {
            // Si no está logueado, redirigir al login
            window.location.href = '/accounts/login/';
            return;
        }
        if (!response.ok) {
            throw new Error('Error en la petición');
        }
        return response.json();
    })
    .then(data => {
        if (data) {
            // 2. Actualizar el estado visual del botón de la tarjeta (Rojo/Gris)
            if (data.es_favorito) {
                btn.classList.add('activo');
            } else {
                btn.classList.remove('activo');
            }

            // 3. ACTUALIZAR EL HEADER (CONTADOR Y ANIMACIÓN)
            const favCounter = document.getElementById('fav-counter');
            const favIcon = document.getElementById('header-fav-icon');

            if (favCounter) {
                // Actualizar el número con el total que nos envía el backend
                favCounter.textContent = data.total_user_favorites;

                // Mostrar u ocultar el globito rojo según la cantidad
                if (data.total_user_favorites > 0) {
                    favCounter.classList.add('has-items');
                } else {
                    favCounter.classList.remove('has-items');
                }

                // 4. Animación de "Latido" en el Header
                if (favIcon) {
                    favIcon.classList.add('fa-beat'); // Clase que definimos en CSS global
                    setTimeout(() => {
                        favIcon.classList.remove('fa-beat');
                    }, 1000); // Quitar la clase después de 1 segundo
                }
            }
        }
    })
    .catch(error => console.error('Error al actualizar favorito:', error));
}

/**
 * Inicializador principal
 * Se ejecuta cuando el DOM está listo.
 */
document.addEventListener('DOMContentLoaded', () => {

    // --- Módulos Globales (se ejecutan en todas las páginas) ---
    // Verificamos si las funciones existen antes de llamarlas para robustez

    if (typeof initCart === "function") {
        initCart();
    }

    if (typeof initSearch === "function") {
        initSearch();
    }

    // --- Módulos Específicos ---

    if (typeof initShippingCalculator === "function") {
        initShippingCalculator();
    }

    if (typeof initCarousel === "function") {
        initCarousel();
    }

    // Nota: showCustomAlert() ya existe globalmente desde notifications.js
});