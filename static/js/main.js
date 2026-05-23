/* JobPortal – main.js */

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert.alert-dismissible').forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert.close();
    }, 5000);
  });

  // Activate tooltips
  document.querySelectorAll('[title]').forEach(el => {
    new bootstrap.Tooltip(el, { trigger: 'hover' });
  });

  // Character counter for textareas
  document.querySelectorAll('textarea[maxlength]').forEach(ta => {
    const counter = document.createElement('div');
    counter.className = 'text-muted small text-end mt-1';
    const update = () => counter.textContent = `${ta.value.length} / ${ta.maxLength}`;
    ta.addEventListener('input', update);
    ta.after(counter);
    update();
  });

  // File input preview filename
  document.querySelectorAll('input[type="file"]').forEach(input => {
    input.addEventListener('change', () => {
      const file = input.files[0];
      if (file) {
        let preview = input.nextElementSibling;
        if (!preview || !preview.classList.contains('file-preview')) {
          preview = document.createElement('div');
          preview.className = 'file-preview text-success small mt-1';
          input.after(preview);
        }
        preview.innerHTML = `<i class="bi bi-check-circle me-1"></i>${file.name} (${(file.size/1024).toFixed(1)} KB)`;
      }
    });
  });

  // Confirm dialogs (data-confirm attribute)
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', e => {
      if (!confirm(el.dataset.confirm)) e.preventDefault();
    });
  });
});

// CSRF helper for fetch requests
function getCSRF() {
  return document.cookie.match(/csrftoken=([\w-]+)/)?.[1] || '';
}

// Generic AJAX post helper
async function ajaxPost(url, data = {}) {
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRF(),
    },
    body: JSON.stringify(data),
  });
  return res.json();
}
