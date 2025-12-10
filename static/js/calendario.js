/**
 * LÓGICA DEL CALENDARIO DE TURNOS
 * - Selección visual de hora.
 * - Confirmación en dos pasos.
 * - Notificaciones personalizadas.
 */

document.addEventListener('DOMContentLoaded', function() {
    
    const calendarEl = document.getElementById('inline-calendar');
    const listaHorariosEl = document.getElementById('lista-horarios');
    const tituloFechaEl = document.getElementById('fecha-seleccionada-titulo');
    const loadingEl = document.getElementById('estado-loading');
    
    const formReserva = document.getElementById('form-reserva');
    const inputFecha = document.getElementById('input-fecha');
    const inputHora = document.getElementById('input-hora');

    if (!calendarEl || !listaHorariosEl) return;

    // 1. INICIALIZAR FLATPICKR
    const fp = flatpickr(calendarEl, {
        inline: true,
        locale: "es",
        minDate: "today",
        dateFormat: "Y-m-d",
        disable: [ function(date) { return false; } ],
        onChange: function(selectedDates, dateStr, instance) {
            if (selectedDates.length > 0) {
                cargarHorarios(dateStr, selectedDates[0]);
            }
        }
    });

    // 2. FUNCIÓN AJAX
    function cargarHorarios(fechaStr, fechaObj) {
        listaHorariosEl.innerHTML = ''; 
        loadingEl.style.display = 'inline-block';
        
        const opcionesFecha = { weekday: 'long', day: 'numeric', month: 'long' };
        const fechaTexto = fechaObj.toLocaleDateString('es-ES', opcionesFecha);
        tituloFechaEl.textContent = fechaTexto.charAt(0).toUpperCase() + fechaTexto.slice(1);

        fetch(`/turnos/api/horarios/?fecha=${fechaStr}`)
            .then(response => {
                if (!response.ok) throw new Error('Error en la red');
                return response.json();
            })
            .then(data => {
                loadingEl.style.display = 'none';
                if (data.horarios && data.horarios.length > 0) {
                    renderizarInterfazSeleccion(data.horarios, fechaStr);
                } else {
                    listaHorariosEl.innerHTML = `
                        <div class="empty-state-horarios">
                            <i class="far fa-clock" style="font-size: 2rem; opacity: 0.3; margin-bottom: 10px;"></i>
                            <p>No hay horarios disponibles.</p>
                        </div>`;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                loadingEl.style.display = 'none';
                listaHorariosEl.innerHTML = '<p class="error-msg">Error al cargar horarios.</p>';
            });
    }

    // 3. RENDERIZAR LA INTERFAZ DE SELECCIÓN
    function renderizarInterfazSeleccion(horarios, fechaStr) {
        listaHorariosEl.innerHTML = '';

        // A. Contenedor de la grilla de botones
        const gridDiv = document.createElement('div');
        gridDiv.className = 'grid-horarios-inner';
        listaHorariosEl.appendChild(gridDiv);

        // B. Contenedor del botón de confirmación (Oculto al inicio)
        const confirmArea = document.createElement('div');
        confirmArea.className = 'confirm-action-area';
        confirmArea.style.display = 'none'; // Se muestra al seleccionar una hora
        listaHorariosEl.appendChild(confirmArea);

        horarios.forEach(hora => {
            const btn = document.createElement('button');
            btn.className = 'btn-hora';
            btn.textContent = hora;
            btn.type = 'button';
            
            // Lógica de Selección
            btn.addEventListener('click', () => {
                // 1. Quitar selección previa
                const previos = gridDiv.querySelectorAll('.selected');
                previos.forEach(b => b.classList.remove('selected'));

                // 2. Marcar actual
                btn.classList.add('selected');

                // 3. Mostrar botón de confirmar
                mostrarBotonConfirmar(confirmArea, fechaStr, hora);
            });
            
            gridDiv.appendChild(btn);
        });
    }

    // 4. MOSTRAR BOTÓN DE CONFIRMACIÓN
    function mostrarBotonConfirmar(container, fecha, hora) {
        container.style.display = 'block';
        container.innerHTML = ''; // Limpiar previo

        const btnConfirmar = document.createElement('button');
        btnConfirmar.className = 'btn-confirmar-seleccion';
        btnConfirmar.innerHTML = `Confirmar Turno: <strong>${hora} hs</strong> <i class="fas fa-arrow-right"></i>`;
        
        btnConfirmar.addEventListener('click', () => {
            procesarReserva(fecha, hora);
        });
        
        container.appendChild(btnConfirmar);
    }

    // 5. PROCESAR Y REDIRIGIR (Con notificación bonita)
    function procesarReserva(fecha, hora) {
        // Llenar datos ocultos
        inputFecha.value = fecha;
        inputHora.value = hora;

        // Mostrar notificación flotante (usando tu función global)
        if (typeof showCustomAlert === "function") {
            showCustomAlert(`Reservando turno para las ${hora}...`, 3000, 'info');
        }

        // Pequeño delay para que el usuario lea la notificación antes de irse
        setTimeout(() => {
            formReserva.submit();
        }, 1000);
    }
});