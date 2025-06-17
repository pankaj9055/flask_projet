// Main JavaScript for Oxin Platform
(function() {
    'use strict';

    // DOM Content Loaded
    document.addEventListener('DOMContentLoaded', function() {
        initializeApp();
    });

    // Initialize Application
    function initializeApp() {
        initScrollAnimations();
        initParticleEffects();
        initNavbarEffects();
        initFormValidation();
        initTooltips();
        initCounters();
        initModalEffects();
        
        // Page-specific initializations
        if (document.querySelector('.countdown-timer')) {
            initCountdownTimer();
        }
        
        if (document.querySelector('.mining-section')) {
            initMiningEffects();
        }
        
        if (document.querySelector('.wallet-section')) {
            initWalletEffects();
        }
        
        if (document.querySelector('.admin-dashboard')) {
            initAdminEffects();
        }
    }

    // Scroll Animations
    function initScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        // Observe elements for animation
        const animatedElements = document.querySelectorAll(
            '.feature-item, .feature-card, .stat-card, .action-card, .profile-card, .sidebar-card'
        );
        
        animatedElements.forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            observer.observe(el);
        });

        // Add animate-in styles
        const style = document.createElement('style');
        style.textContent = `
            .animate-in {
                opacity: 1 !important;
                transform: translateY(0) !important;
            }
        `;
        document.head.appendChild(style);
    }

    // Particle Effects - Optimized for performance
    function initParticleEffects() {
        const hero = document.querySelector('.hero-section');
        if (!hero) return;

        // Reduced particle count for better performance
        for (let i = 0; i < 8; i++) {
            setTimeout(() => createFloatingParticle(hero), i * 200);
        }
    }

    function createFloatingParticle(container) {
        const particle = document.createElement('div');
        particle.className = 'floating-particle';
        particle.style.cssText = `
            position: absolute;
            width: 4px;
            height: 4px;
            background: var(--neon-purple);
            border-radius: 50%;
            pointer-events: none;
            opacity: 0.6;
            animation: floatParticle ${Math.random() * 10 + 5}s linear infinite;
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
            animation-delay: ${Math.random() * 5}s;
        `;
        
        container.appendChild(particle);

        // Remove and recreate after animation
        setTimeout(() => {
            if (particle.parentNode) {
                particle.parentNode.removeChild(particle);
                createFloatingParticle(container);
            }
        }, (Math.random() * 10 + 5) * 1000);
    }

    // Navbar Effects
    function initNavbarEffects() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;

        let lastScrollY = window.scrollY;

        window.addEventListener('scroll', () => {
            const currentScrollY = window.scrollY;
            
            if (currentScrollY > 100) {
                navbar.style.background = 'rgba(10, 10, 35, 0.95)';
                navbar.style.backdropFilter = 'blur(20px)';
            } else {
                navbar.style.background = 'rgba(10, 10, 35, 0.9)';
                navbar.style.backdropFilter = 'blur(10px)';
            }
            
            lastScrollY = currentScrollY;
        });
    }

    // Form Validation
    function initFormValidation() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input[required], select[required]');
            
            inputs.forEach(input => {
                input.addEventListener('blur', validateInput);
                input.addEventListener('input', debounce(clearValidation, 300));
            });
            
            form.addEventListener('submit', function(e) {
                let isValid = true;
                
                inputs.forEach(input => {
                    if (!validateInput.call(input)) {
                        isValid = false;
                    }
                });
                
                if (!isValid) {
                    e.preventDefault();
                    showNotification('Please fix the errors in the form', 'error');
                }
            });
        });
    }

    function validateInput() {
        const input = this;
        const value = input.value.trim();
        let isValid = true;
        let message = '';

        // Remove existing error styling
        input.classList.remove('error');
        const existingError = input.parentNode.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }

        // Required validation
        if (input.hasAttribute('required') && !value) {
            isValid = false;
            message = 'This field is required';
        }

        // Email validation
        if (input.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                message = 'Please enter a valid email address';
            }
        }

        // Password validation
        if (input.type === 'password' && value) {
            if (value.length < 6) {
                isValid = false;
                message = 'Password must be at least 6 characters long';
            }
        }

        // Number validation
        if (input.type === 'number' && value) {
            const min = parseFloat(input.getAttribute('min'));
            const max = parseFloat(input.getAttribute('max'));
            const numValue = parseFloat(value);
            
            if (!isNaN(min) && numValue < min) {
                isValid = false;
                message = `Value must be at least ${min}`;
            }
            
            if (!isNaN(max) && numValue > max) {
                isValid = false;
                message = `Value must be at most ${max}`;
            }
        }

        if (!isValid) {
            input.classList.add('error');
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = message;
            errorDiv.style.cssText = `
                color: var(--neon-pink);
                font-size: 0.8rem;
                margin-top: 0.25rem;
            `;
            input.parentNode.appendChild(errorDiv);
        }

        return isValid;
    }

    function clearValidation() {
        if (this && this.classList) {
            this.classList.remove('error');
            const errorMessage = this.parentNode ? this.parentNode.querySelector('.error-message') : null;
            if (errorMessage) {
                errorMessage.remove();
            }
        }
    }

    // Tooltips
    function initTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', showTooltip);
            element.addEventListener('mouseleave', hideTooltip);
        });
    }

    function showTooltip(e) {
        const element = e.target;
        const text = element.getAttribute('data-tooltip');
        
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = text;
        tooltip.style.cssText = `
            position: absolute;
            background: rgba(42, 42, 74, 0.95);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-size: 0.8rem;
            z-index: 9999;
            pointer-events: none;
            border: 1px solid var(--neon-purple);
            backdrop-filter: blur(10px);
        `;
        
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
        
        element._tooltip = tooltip;
    }

    function hideTooltip(e) {
        const element = e.target;
        if (element._tooltip) {
            document.body.removeChild(element._tooltip);
            delete element._tooltip;
        }
    }

    // Counters
    function initCounters() {
        const counters = document.querySelectorAll('.counter');
        
        const counterObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    counterObserver.unobserve(entry.target);
                }
            });
        });
        
        counters.forEach(counter => {
            counterObserver.observe(counter);
        });
    }

    function animateCounter(element) {
        const target = parseInt(element.textContent);
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;
        
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                element.textContent = target;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current);
            }
        }, 16);
    }

    // Modal Effects
    function initModalEffects() {
        const modals = document.querySelectorAll('.modal');
        
        modals.forEach(modal => {
            modal.addEventListener('show.bs.modal', function() {
                document.body.style.overflow = 'hidden';
                this.style.backdropFilter = 'blur(10px)';
            });
            
            modal.addEventListener('hide.bs.modal', function() {
                document.body.style.overflow = '';
            });
        });
    }

    // Countdown Timer - Optimized
    function initCountdownTimer() {
        const countdownElements = {
            days: document.getElementById('days'),
            hours: document.getElementById('hours'),
            minutes: document.getElementById('minutes'),
            seconds: document.getElementById('seconds')
        };

        // Safe check for elements existence
        const validElements = Object.values(countdownElements).filter(el => el !== null);
        if (validElements.length === 0) {
            return;
        }

        function updateCountdown() {
            const targetDate = new Date('2026-01-01T00:00:00Z').getTime();
            const now = new Date().getTime();
            const distance = targetDate - now;
            
            if (distance < 0) {
                Object.values(countdownElements).forEach(el => el.textContent = '00');
                return;
            }
            
            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);
            
            countdownElements.days.textContent = days.toString().padStart(2, '0');
            countdownElements.hours.textContent = hours.toString().padStart(2, '0');
            countdownElements.minutes.textContent = minutes.toString().padStart(2, '0');
            countdownElements.seconds.textContent = seconds.toString().padStart(2, '0');
            
            // Add pulse effect to seconds
            countdownElements.seconds.style.animation = 'pulse 1s ease-in-out';
            setTimeout(() => {
                countdownElements.seconds.style.animation = '';
            }, 1000);
        }
        
        updateCountdown();
        setInterval(updateCountdown, 1000);
    }

    // Mining Effects
    function initMiningEffects() {
        const miningCircle = document.querySelector('.mining-circle');
        const progressRing = document.querySelector('.progress-ring-circle');
        
        if (miningCircle) {
            // Add pulsing effect to mining circle
            setInterval(() => {
                miningCircle.style.boxShadow = '0 0 30px var(--neon-purple)';
                setTimeout(() => {
                    miningCircle.style.boxShadow = '0 0 10px var(--neon-purple)';
                }, 500);
            }, 2000);
        }
        
        if (progressRing) {
            // Initialize progress ring
            const radius = progressRing.r.baseVal.value;
            const circumference = radius * 2 * Math.PI;
            
            progressRing.style.strokeDasharray = `${circumference} ${circumference}`;
            progressRing.style.strokeDashoffset = circumference;
        }
    }

    // Wallet Effects
    function initWalletEffects() {
        const balanceCard = document.querySelector('.balance-card');
        
        if (balanceCard) {
            // Add hover glow effect
            balanceCard.addEventListener('mouseenter', function() {
                this.style.boxShadow = '0 0 40px rgba(139, 92, 246, 0.6)';
            });
            
            balanceCard.addEventListener('mouseleave', function() {
                this.style.boxShadow = '0 0 20px rgba(139, 92, 246, 0.3)';
            });
        }
        
        // Animate balance numbers
        const balanceAmount = document.querySelector('.balance-amount');
        if (balanceAmount) {
            const originalValue = balanceAmount.textContent;
            balanceAmount.addEventListener('click', function() {
                this.style.animation = 'glow 1s ease-in-out';
                setTimeout(() => {
                    this.style.animation = '';
                }, 1000);
            });
        }
    }

    // Admin Effects
    function initAdminEffects() {
        const menuItems = document.querySelectorAll('.menu-item');
        
        menuItems.forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Remove active class from all items
                menuItems.forEach(mi => mi.classList.remove('active'));
                
                // Add active class to clicked item
                this.classList.add('active');
                
                // Show corresponding section
                const target = this.getAttribute('href');
                if (target && target.startsWith('#')) {
                    showAdminSection(target.substring(1));
                }
            });
        });
        
        // Initialize charts if Chart.js is available
        if (typeof Chart !== 'undefined') {
            initAdminCharts();
        }
    }

    function showAdminSection(sectionId) {
        // Hide all sections
        document.querySelectorAll('.admin-section').forEach(section => {
            section.classList.add('d-none');
        });
        
        // Show target section
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.remove('d-none');
            
            // Add fade-in animation
            targetSection.style.opacity = '0';
            targetSection.style.transform = 'translateY(20px)';
            setTimeout(() => {
                targetSection.style.transition = 'all 0.3s ease';
                targetSection.style.opacity = '1';
                targetSection.style.transform = 'translateY(0)';
            }, 10);
        }
    }

    function initAdminCharts() {
        // This would initialize charts if needed
        // For now, just placeholder for future chart implementations
    }

    // Utility Functions
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 9999;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            max-width: 400px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        `;
        
        // Set background based on type
        switch (type) {
            case 'success':
                notification.style.background = 'rgba(16, 185, 129, 0.9)';
                break;
            case 'error':
                notification.style.background = 'rgba(236, 72, 153, 0.9)';
                break;
            case 'warning':
                notification.style.background = 'rgba(251, 191, 36, 0.9)';
                break;
            default:
                notification.style.background = 'rgba(59, 130, 246, 0.9)';
        }
        
        document.body.appendChild(notification);
        
        // Slide in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);
        
        // Auto remove
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }

    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    function throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // Copy to clipboard utility
    function copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                showNotification('Copied to clipboard!', 'success');
            }).catch(() => {
                fallbackCopyTextToClipboard(text);
            });
        } else {
            fallbackCopyTextToClipboard(text);
        }
    }

    function fallbackCopyTextToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.top = '0';
        textArea.style.left = '0';
        textArea.style.position = 'fixed';
        
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            const successful = document.execCommand('copy');
            if (successful) {
                showNotification('Copied to clipboard!', 'success');
            } else {
                showNotification('Failed to copy', 'error');
            }
        } catch (err) {
            showNotification('Failed to copy', 'error');
        }
        
        document.body.removeChild(textArea);
    }

    // Expose utilities to global scope
    window.OxinUtils = {
        showNotification,
        copyToClipboard,
        debounce,
        throttle
    };

    // Performance monitoring
    if ('performance' in window) {
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
            }, 0);
        });
    }

    // Error handling
    window.addEventListener('error', function(e) {
        console.error('JavaScript error:', e.error);
        // Could send to error tracking service here
    });

    // Service Worker registration (if available)
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            // Service worker would be registered here if implemented
        });
    }

})();

// Additional utility functions for specific components
document.addEventListener('DOMContentLoaded', function() {
    
    // Copy button functionality for referral codes
    document.addEventListener('click', function(e) {
        if (e.target.closest('.copy-btn') || e.target.closest('[onclick*="copy"]')) {
            e.preventDefault();
            const input = e.target.closest('.input-group, .code-input, .referral-input')?.querySelector('input');
            if (input) {
                window.OxinUtils.copyToClipboard(input.value);
            }
        }
    });
    
    // Auto-hide alerts
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (!alert.querySelector('.btn-close')) {
            setTimeout(() => {
                alert.style.opacity = '0';
                alert.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.parentNode.removeChild(alert);
                    }
                }, 300);
            }, 5000);
        }
    });
    
    // Smooth scrolling for anchor links
    document.addEventListener('click', function(e) {
        const link = e.target.closest('a[href^="#"]');
        if (link) {
            e.preventDefault();
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
    
    // Form auto-save (for longer forms)
    const forms = document.querySelectorAll('form[data-autosave]');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('input', window.OxinUtils.debounce(() => {
                localStorage.setItem(`form_${form.id}_${input.name}`, input.value);
            }, 500));
            
            // Restore saved values
            const saved = localStorage.getItem(`form_${form.id}_${input.name}`);
            if (saved && !input.value) {
                input.value = saved;
            }
        });
        
        // Clear saved data on successful submission
        form.addEventListener('submit', function() {
            inputs.forEach(input => {
                localStorage.removeItem(`form_${form.id}_${input.name}`);
            });
        });
    });
    
});
