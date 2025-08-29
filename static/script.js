// Additional JavaScript functionality for the webapp

// Countdown Timer
function updateCountdown() {
    const countdownElement = document.getElementById('countdown');
    if (!countdownElement) return;
    
    // Get deadline from data attribute
    const deadlineISO = countdownElement.getAttribute('data-deadline');
    if (!deadlineISO) {
        countdownElement.innerHTML = 'No deadline set';
        countdownElement.className = 'fs-5 text-muted';
        return;
    }
    
    const deadline = new Date(deadlineISO).getTime();
    const now = new Date().getTime();
    const timeLeft = deadline - now;
    
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
    
    // Draft position hover tooltips with snake draft logic
    const draftButtons = document.querySelectorAll('.draft-position-btn');
    if (draftButtons.length > 0) {
        // Get total number of teams from all available positions
        const allPositions = document.querySelectorAll('.draft-position');
        const totalTeams = allPositions.length;
        
        draftButtons.forEach(button => {
            const position = parseInt(button.getAttribute('data-position'));
            
            // Calculate all 13 round picks for this position using snake logic
            const allPicks = [];
            for (let round = 1; round <= 13; round++) {
                let pickInRound;
                if (round % 2 === 1) {
                    // Odd rounds: normal order (1, 2, 3, ...)
                    pickInRound = position;
                } else {
                    // Even rounds: reverse order (12, 11, 10, ...)
                    pickInRound = totalTeams - position + 1;
                }
                
                // Calculate overall pick number
                const overallPick = (round - 1) * totalTeams + pickInRound;
                allPicks.push(`<tr><td>${round}</td><td>${overallPick}</td></tr>`);
            }
            
            // Create tooltip content
            const tooltipContent = `
                <div class="draft-tooltip">
                    <h6>Draft Position ${position}</h6>
                    <table class="pick-table">
                        <thead>
                            <tr><th>Round</th><th>Pick</th></tr>
                        </thead>
                        <tbody>
                            ${allPicks.join('')}
                        </tbody>
                    </table>
                </div>
            `;
            
            // Add hover events
            button.addEventListener('mouseenter', function(e) {
                showTooltip(e.target, tooltipContent);
            });
            
            button.addEventListener('mouseleave', function() {
                hideTooltip();
            });
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

// Tooltip functions for draft position hover
function showTooltip(element, content) {
    // Remove existing tooltip
    hideTooltip();
    
    const tooltip = document.createElement('div');
    tooltip.id = 'draft-tooltip';
    tooltip.innerHTML = content;
    tooltip.style.cssText = `
        position: absolute;
        background: #333;
        color: white;
        padding: 10px;
        border-radius: 5px;
        font-size: 12px;
        line-height: 1.4;
        z-index: 1000;
        max-width: 200px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        pointer-events: none;
    `;
    
    document.body.appendChild(tooltip);
    
    // Position tooltip
    const rect = element.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    
    let left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
    let top = rect.top - tooltipRect.height - 10;
    
    // Adjust if tooltip goes off screen
    if (left < 5) left = 5;
    if (left + tooltipRect.width > window.innerWidth - 5) {
        left = window.innerWidth - tooltipRect.width - 5;
    }
    if (top < 5) {
        top = rect.bottom + 10;
    }
    
    tooltip.style.left = left + 'px';
    tooltip.style.top = top + 'px';
}

function hideTooltip() {
    const existing = document.getElementById('draft-tooltip');
    if (existing) {
        existing.remove();
    }
}

// Theme Toggle Functionality
class ThemeToggle {
    constructor() {
        this.toggle = document.getElementById('themeToggle');
        this.label = document.querySelector('.theme-label');
        this.storageKey = 'fantasy-football-theme';
        
        this.init();
    }
    
    init() {
        // Set initial theme based on stored preference or system preference
        this.setInitialTheme();
        
        // Add change event listener
        if (this.toggle) {
            this.toggle.addEventListener('change', () => this.handleToggle());
        }
    }
    
    setInitialTheme() {
        const savedTheme = localStorage.getItem(this.storageKey);
        
        if (savedTheme === 'dark') {
            this.applyTheme('dark');
            this.toggle.checked = true;
        } else if (savedTheme === 'light') {
            this.applyTheme('light');
            this.toggle.checked = false;
        } else {
            // Use system preference (auto mode)
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            this.applyTheme(prefersDark ? 'dark' : 'light');
            this.toggle.checked = prefersDark;
        }
    }
    
    getCurrentTheme() {
        const htmlElement = document.documentElement;
        return htmlElement.getAttribute('data-theme') || 'auto';
    }
    
    applyTheme(theme) {
        const htmlElement = document.documentElement;
        
        if (theme === 'dark') {
            htmlElement.setAttribute('data-theme', 'dark');
            this.updateLabel('Dark Mode');
        } else {
            htmlElement.setAttribute('data-theme', 'light');
            this.updateLabel('Light Mode');
        }
        
        // Save preference
        localStorage.setItem(this.storageKey, theme);
    }
    
    updateLabel(text) {
        if (this.label) {
            this.label.textContent = text;
        }
    }
    
    handleToggle() {
        if (this.toggle.checked) {
            this.applyTheme('dark');
        } else {
            this.applyTheme('light');
        }
    }
}

// Initialize theme toggle when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new ThemeToggle();
});