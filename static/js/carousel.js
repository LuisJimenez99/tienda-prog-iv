/**
 * =================================
 * MÓDULO: CARRUSEL
 * =================================
 * Inicializa el carrusel (usado en inicio.html).
 */
function initCarousel() {
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
                autoSlideInterval = setInterval(nextSlide, 5000); 
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

        // Iniciar al cargar la página
        showSlide(currentIndex); 
        startAutoSlide(); 

        carrusel.addEventListener('mouseenter', stopAutoSlide);
        carrusel.addEventListener('mouseleave', startAutoSlide);
    }
}