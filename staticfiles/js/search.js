/**
 * =================================
 * MÓDULO: BÚSQUEDA PREDICTIVA
 * =================================
 * Inicializa la búsqueda predictiva en el header.
 */
function initSearch() {
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

        // Ocultar resultados al hacer clic fuera
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-wrapper')) { 
                searchResultsContainer.classList.remove('visible');
            }
        });
    }
}