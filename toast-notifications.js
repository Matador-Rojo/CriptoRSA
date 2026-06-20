const toastIcons = {
  success: '✓',
  warning: '!',
  error: '×',
  info: 'i'
};

function getToastType(title) {
  const normalized = title.toLowerCase();
  if (normalized.includes('error')) return 'error';
  if (normalized.includes('atención') || normalized.includes('atencion')) return 'warning';
  if (normalized.includes('éxito') || normalized.includes('exito') || normalized.includes('copiado')) return 'success';
  return 'info';
}

function getToastContainer() {
  let container = document.getElementById('toastContainer');

  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    container.setAttribute('aria-live', 'polite');
    container.setAttribute('aria-atomic', 'false');
    document.body.appendChild(container);
  }

  return container;
}

function removeToast(toast) {
  if (!toast || toast.classList.contains('removing')) return;
  toast.classList.add('removing');
  setTimeout(() => toast.remove(), 260);
}

showMessage = function showMessage(title, body) {
  const container = getToastContainer();
  const type = getToastType(title);
  const duration = type === 'error' ? 7500 : 4600;

  const toast = document.createElement('section');
  toast.className = `toast ${type}`;
  toast.style.setProperty('--toast-duration', `${duration}ms`);
  toast.setAttribute('role', type === 'error' ? 'alert' : 'status');

  const icon = document.createElement('div');
  icon.className = 'toast-icon';
  icon.textContent = toastIcons[type];

  const content = document.createElement('div');
  content.className = 'toast-content';

  const toastTitle = document.createElement('p');
  toastTitle.className = 'toast-title';
  toastTitle.textContent = title;

  const message = document.createElement('p');
  message.className = 'toast-message';
  message.textContent = body;

  const close = document.createElement('button');
  close.className = 'toast-close';
  close.type = 'button';
  close.setAttribute('aria-label', 'Cerrar notificación');
  close.textContent = '×';

  const progress = document.createElement('div');
  progress.className = 'toast-progress';

  content.appendChild(toastTitle);
  content.appendChild(message);
  toast.appendChild(icon);
  toast.appendChild(content);
  toast.appendChild(close);
  toast.appendChild(progress);
  container.appendChild(toast);

  close.addEventListener('click', () => removeToast(toast));
  const timeout = setTimeout(() => removeToast(toast), duration);

  toast.addEventListener('mouseenter', () => {
    clearTimeout(timeout);
    progress.style.animationPlayState = 'paused';
  });

  toast.addEventListener('mouseleave', () => {
    progress.style.animationPlayState = 'running';
    setTimeout(() => removeToast(toast), 1800);
  }, { once: true });
};

window.showMessage = showMessage;
