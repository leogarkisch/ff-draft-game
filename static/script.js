// Additional JavaScript functionality for the webapp

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Number input validation
    const guessInput = document.getElementById('guess');
    if (guessInput) {
        guessInput.addEventListener('input', function() {
            const value = parseInt(this.value);
            if (value < 0 || value > 1000) {
                this.setCustomValidity('Number must be between 0 and 1000');
            } else {
                this.setCustomValidity('');
            }
        });
    }
});

// Function to refresh page periodically to check for deadline
function autoRefresh() {
    // Refresh every 5 minutes if on main page
    if (window.location.pathname === '/') {
        setTimeout(function() {
            window.location.reload();
        }, 300000); // 5 minutes
    }
}

autoRefresh();