/**
 * CircuTrade AI - Main JavaScript
 * Frontend interactions and dynamic features
 */

// ==================== 
// Global State
// ====================
const CircuTradeApp = {
    impactData: {
        co2Saved: 0,
        materialsTrad: 0
    },

    init() {
        this.initImpactCounter();
        this.initPriceCalculator();
        this.initMarketplaceFilters();
        this.initFormValidation();
        this.loadFooterStats();
    },

    // ==================== 
    // Impact Counter Animation
    // ====================
    initImpactCounter() {
        // Support single counter (legacy)
        const singleCounter = document.getElementById('impact-counter');
        if (singleCounter) {
            const targetValue = parseInt(singleCounter.dataset.target) || 0;
            this.animateCounter(singleCounter, 0, targetValue, 2000);
        }

        // Support multiple counters (for landing page)
        const multipleCounters = document.querySelectorAll('.impact-number');
        multipleCounters.forEach(counter => {
            const targetValue = parseInt(counter.dataset.target) || 0;
            this.animateCounter(counter, 0, targetValue, 2000);
        });
    },

    animateCounter(element, start, end, duration) {
        const startTime = performance.now();
        const range = end - start;

        const updateCounter = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Easing function for smooth animation
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const current = Math.floor(start + (range * easeOutQuart));

            element.textContent = this.formatNumber(current);

            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            }
        };

        requestAnimationFrame(updateCounter);
    },

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(2) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(2) + 'K';
        }
        return num.toLocaleString();
    },

    // ==================== 
    // Real-time Price Calculator
    // ====================
    initPriceCalculator() {
        const materialSelect = document.getElementById('id_material');
        const gradeSelect = document.getElementById('id_grade');
        const weightInput = document.getElementById('id_weight');
        const priceDisplay = document.getElementById('calculated-price');

        if (!materialSelect || !gradeSelect || !weightInput || !priceDisplay) return;

        const calculatePrice = async () => {
            const material = materialSelect.value;
            const grade = gradeSelect.value;
            const weight = weightInput.value;

            if (!material || !grade || !weight || weight <= 0) {
                priceDisplay.textContent = '₹0.00';
                return;
            }

            try {
                const response = await fetch('/marketplace/api/calculate-price/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCsrfToken()
                    },
                    body: JSON.stringify({
                        material_id: material,
                        grade: grade,
                        weight: parseFloat(weight)
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    priceDisplay.textContent = `₹${data.price.toFixed(2)}`;

                    // Animate price update
                    priceDisplay.classList.add('count-up');
                    setTimeout(() => priceDisplay.classList.remove('count-up'), 800);
                } else {
                    console.error('Price calculation failed');
                }
            } catch (error) {
                console.error('Error calculating price:', error);
            }
        };

        // Debounce price calculation
        let timeout;
        const debouncedCalculate = () => {
            clearTimeout(timeout);
            timeout = setTimeout(calculatePrice, 300);
        };

        materialSelect.addEventListener('change', debouncedCalculate);
        gradeSelect.addEventListener('change', debouncedCalculate);
        weightInput.addEventListener('input', debouncedCalculate);
    },

    // ==================== 
    // Marketplace Filters
    // ====================
    initMarketplaceFilters() {
        const filterForm = document.getElementById('filter-form');
        if (!filterForm) return;

        const filterInputs = filterForm.querySelectorAll('select, input');

        filterInputs.forEach(input => {
            input.addEventListener('change', () => {
                this.applyFilters(filterForm);
            });
        });
    },

    applyFilters(form) {
        const formData = new FormData(form);
        const params = new URLSearchParams(formData);

        // Update URL without reload
        const newUrl = `${window.location.pathname}?${params.toString()}`;
        window.history.pushState({}, '', newUrl);

        // Fetch filtered results
        this.fetchFilteredListings(params);
    },

    async fetchFilteredListings(params) {
        const listingsContainer = document.getElementById('listings-container');
        if (!listingsContainer) return;

        // Show loading state
        listingsContainer.classList.add('opacity-50');

        try {
            const response = await fetch(`/marketplace/feed/?${params.toString()}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                const html = await response.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newListings = doc.getElementById('listings-container');

                if (newListings) {
                    listingsContainer.innerHTML = newListings.innerHTML;

                    // Animate new cards
                    const cards = listingsContainer.querySelectorAll('.marketplace-card');
                    cards.forEach((card, index) => {
                        card.style.animationDelay = `${index * 0.1}s`;
                        card.classList.add('fade-in-up');
                    });
                }
            }
        } catch (error) {
            console.error('Error filtering listings:', error);
        } finally {
            listingsContainer.classList.remove('opacity-50');
        }
    },

    // ==================== 
    // Form Validation
    // ====================
    initFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');

        forms.forEach(form => {
            form.addEventListener('submit', (event) => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }

                form.classList.add('was-validated');
            });
        });
    },

    // ==================== 
    // Footer Stats Loader
    // ====================
    async loadFooterStats() {
        const co2Element = document.getElementById('footer-co2');
        const materialsElement = document.getElementById('footer-materials');

        if (!co2Element || !materialsElement) return;

        try {
            // In production, this would fetch from an API endpoint
            // For now, calculate from page data or use mock values
            const co2Saved = document.querySelectorAll('[data-co2]').length
                ? Array.from(document.querySelectorAll('[data-co2]'))
                    .reduce((sum, el) => sum + parseFloat(el.dataset.co2 || 0), 0)
                : 15420; // Mock value

            const materialsTraded = document.querySelectorAll('.marketplace-card').length || 243; // Mock value

            this.animateCounter(co2Element, 0, co2Saved, 1500);
            this.animateCounter(materialsElement, 0, materialsTraded, 1500);

            // Format CO2 with unit
            setTimeout(() => {
                co2Element.textContent = this.formatNumber(co2Saved) + ' kg';
            }, 1500);
        } catch (error) {
            console.error('Error loading footer stats:', error);
            co2Element.textContent = 'N/A';
            materialsElement.textContent = 'N/A';
        }
    },

    // ==================== 
    // Utility Functions
    // ====================
    getCsrfToken() {
        const cookie = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    },

    showNotification(message, type = 'success') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
        alertDiv.style.zIndex = '9999';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alertDiv);

        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    },

    // ==================== 
    // Image Preview
    // ====================
    initImagePreview() {
        const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');

        imageInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (!file) return;

                const previewId = input.dataset.preview;
                if (!previewId) return;

                const preview = document.getElementById(previewId);
                if (!preview) return;

                const reader = new FileReader();
                reader.onload = (e) => {
                    preview.src = e.target.result;
                    preview.classList.remove('d-none');
                };
                reader.readAsDataURL(file);
            });
        });
    },

    // ==================== 
    // Blockchain Hash Visualization
    // ====================
    highlightBlockchainHash(hashElement) {
        if (!hashElement) return;

        const hash = hashElement.textContent;
        const highlighted = hash.split('').map((char, index) => {
            const hue = (index * 137.5) % 360; // Golden angle for color distribution
            return `<span style="color: hsl(${hue}, 70%, 50%)">${char}</span>`;
        }).join('');

        hashElement.innerHTML = highlighted;
    }
};

// ==================== 
// Initialize on DOM Ready
// ====================
document.addEventListener('DOMContentLoaded', () => {
    CircuTradeApp.init();

    // Initialize image preview
    CircuTradeApp.initImagePreview();

    // Highlight blockchain hashes
    document.querySelectorAll('.timeline-hash').forEach(hash => {
        CircuTradeApp.highlightBlockchainHash(hash);
    });

    // Add smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
});

// ==================== 
// Export for external use
// ====================
window.CircuTradeApp = CircuTradeApp;
