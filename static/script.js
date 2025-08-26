// Additional JavaScript functionality for the webapp

// Countdown Timer
function updateCountdown() {
    // Set the deadline: Thursday, August 28th, 2025 at 12:00 PM ET
    const deadline = new Date('2025-08-28T12:00:00-04:00').getTime(); // ET timezone
    const now = new Date().getTime();
    const timeLeft = deadline - now;
    
    const countdownElement = document.getElementById('countdown');
    if (!countdownElement) return;
    
    if (timeLeft > 0) {
        const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
        const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
        
        let countdownText = '';
        if (days > 0) {
            countdownText += `${days}d `;
        }
        countdownText += `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        countdownElement.innerHTML = countdownText;
        countdownElement.className = 'fs-4 fw-bold text-primary';
    } else {
        countdownElement.innerHTML = 'Deadline Reached!';
        countdownElement.className = 'fs-4 fw-bold text-danger';
    }
}

// Update countdown every second
if (document.getElementById('countdown')) {
    updateCountdown(); // Initial call
    setInterval(updateCountdown, 1000);
}

// Existing validation code
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