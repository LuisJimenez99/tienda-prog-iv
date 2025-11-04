/**
 * =================================
 * MÓDULO: NOTIFICACIONES
 * =================================
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
  }
  // No se necesita 'else' para 'error' porque el CSS base ya es rojo

  // 3. Pone el mensaje y la muestra
  alertMessage.textContent = message;
  alertBox.classList.add('visible');

  // 4. Oculta la alerta después de la duración especificada
  setTimeout(() => {
    alertBox.classList.remove('visible');
  }, duration);
}