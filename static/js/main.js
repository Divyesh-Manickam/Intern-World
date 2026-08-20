/**
 * InternWorld Main Client Script
 */

document.addEventListener('DOMContentLoaded', function() {
    // 1. Initialize Bootstrap Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 2. Auto-dismiss alerts after 5 seconds
    const autoAlerts = document.querySelectorAll('.alert-dismissible');
    autoAlerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = bootstrap.Alert.getInstance(alert) || new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // 3. AJAX Save / Bookmark Opportunity Toggle
    const saveButtons = document.querySelectorAll('.btn-save-toggle');
    saveButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const oppId = this.dataset.oppId;
            const url = `/students/saved/${oppId}/toggle/`;
            const icon = this.querySelector('i');
            const textSpan = this.querySelector('.save-text');

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.is_saved) {
                    if (icon) {
                        icon.classList.remove('bi-bookmark');
                        icon.classList.add('bi-bookmark-fill', 'text-primary');
                    }
                    if (textSpan) textSpan.textContent = 'Saved';
                    btn.classList.add('btn-saved');
                } else {
                    if (icon) {
                        icon.classList.remove('bi-bookmark-fill', 'text-primary');
                        icon.classList.add('bi-bookmark');
                    }
                    if (textSpan) textSpan.textContent = 'Save';
                    btn.classList.remove('btn-saved');
                }
            })
            .catch(err => console.error("Error saving opportunity:", err));
        });
    });

    // 4. Mark single notification as read via AJAX
    const notifItems = document.querySelectorAll('.notification-item-unread');
    notifItems.forEach(function(item) {
        item.addEventListener('click', function() {
            const notifId = this.dataset.notifId;
            if (notifId) {
                fetch(`/notifications/${notifId}/read/`, {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
            }
        });
    });
});

/**
 * Utility helper to extract CSRF token from cookies
 */
function getCsrfToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 10) === ('csrftoken=')) {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    return cookieValue;
}
