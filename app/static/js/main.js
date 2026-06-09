document.addEventListener('DOMContentLoaded', function () {
  initTheme();
  initTooltips();
  initAutoCloseAlerts();
  initScrollAnimations();
  initConfetti();
});

function initTheme() {
  const saved = localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeIcon(saved);

  const btn = document.getElementById('theme-toggle');
  if (btn) {
    btn.addEventListener('click', function () {
      const current = document.documentElement.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      updateThemeIcon(next);
    });
  }
}

function updateThemeIcon(theme) {
  const btn = document.getElementById('theme-toggle');
  if (!btn) return;
  const icon = btn.querySelector('i');
  if (icon) {
    icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
  }
  const label = btn.querySelector('.theme-label');
  if (label) {
    label.textContent = theme === 'dark' ? 'Claro' : 'Oscuro';
  }
}

function initTooltips() {
  if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
      new bootstrap.Tooltip(el);
    });
  }
}

function initAutoCloseAlerts() {
  document.querySelectorAll('.alert').forEach(function (alert) {
    setTimeout(function () {
      if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
        new bootstrap.Alert(alert).close();
      } else {
        alert.style.display = 'none';
      }
    }, 5000);
  });
}

function initScrollAnimations() {
  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-fade-up');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.animate-on-scroll').forEach(function (el) {
    observer.observe(el);
  });
}

function initConfetti() {
  const triggers = document.querySelectorAll('[data-confetti]');
  triggers.forEach(function (el) {
    el.addEventListener('click', function (e) {
      if (el.tagName === 'A') {
        e.preventDefault();
        fireConfetti();
        var href = el.getAttribute('href');
        if (href) {
          setTimeout(function () { window.location.href = href; }, 800);
        }
      } else if (el.type === 'submit') {
        fireConfetti();
      } else {
        e.preventDefault();
        fireConfetti();
      }
    });
  });
}

function fireConfetti() {
  var container = document.querySelector('.confetti-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'confetti-container';
    document.body.appendChild(container);
  }

  var colors = ['#FFD700', '#D32F2F', '#0A1F44', '#FFFFFF', '#FF9800', '#4CAF50', '#E91E63'];
  var shapes = ['circle', 'square', 'triangle'];

  for (var i = 0; i < 80; i++) {
    var piece = document.createElement('div');
    piece.className = 'confetti-piece';
    var color = colors[Math.floor(Math.random() * colors.length)];
    var shape = shapes[Math.floor(Math.random() * shapes.length)];
    var size = Math.random() * 8 + 4;
    var left = Math.random() * 100;
    var delay = Math.random() * 2;
    var duration = Math.random() * 2 + 2;

    piece.style.left = left + '%';
    piece.style.width = size + 'px';
    piece.style.height = size + 'px';
    piece.style.background = color;
    piece.style.animationDuration = duration + 's';
    piece.style.animationDelay = delay + 's';

    if (shape === 'circle') piece.style.borderRadius = '50%';
    if (shape === 'triangle') {
      piece.style.width = '0';
      piece.style.height = '0';
      piece.style.background = 'transparent';
      piece.style.borderLeft = size / 2 + 'px solid transparent';
      piece.style.borderRight = size / 2 + 'px solid transparent';
      piece.style.borderBottom = size + 'px solid ' + color;
    }

    container.appendChild(piece);
  }

  setTimeout(function () {
    container.innerHTML = '';
  }, 5000);
}

function showToast(message, type) {
  type = type || 'info';
  var container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  var toast = document.createElement('div');
  toast.className = 'custom-toast ' + type;

  var iconMap = { success: 'check-circle', error: 'exclamation-circle', info: 'info-circle' };
  var icon = iconMap[type] || 'info-circle';

  toast.innerHTML =
    '<div class="d-flex align-items-center gap-2">' +
    '<i class="fas fa-' + icon + '"></i>' +
    '<span>' + message + '</span>' +
    '</div>' +
    '<button type="button" class="btn-close btn-close-white" onclick="this.parentElement.remove()"></button>';

  container.appendChild(toast);

  setTimeout(function () {
    toast.style.animation = 'toastOut 0.3s forwards';
    setTimeout(function () { toast.remove(); }, 300);
  }, 4000);
}

async function apiRequest(url, options) {
  options = options || {};
  try {
    var response = await fetch(url, options);
    var data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Error inesperado');
    return data;
  } catch (error) {
    showToast(error.message, 'error');
    throw error;
  }
}

function togglePassword(fieldId) {
  var field = document.getElementById(fieldId);
  if (field) {
    field.type = field.type === 'password' ? 'text' : 'password';
  }
}

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/service-worker.js').then(function () {
    // console.log('SW registered');
  }).catch(function () {
    // console.log('SW failed');
  });
}
