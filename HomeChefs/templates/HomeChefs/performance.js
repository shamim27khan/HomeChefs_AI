// HomeChefs AI Performance Optimizations
// Add this to chef.html before closing </body> tag

// Lazy loading for images
function setupLazyLoading() {
    const lazyImages = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for older browsers
        let scrollTimeout;
        window.addEventListener('scroll', function() {
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }
            scrollTimeout = setTimeout(function() {
                lazyImages.forEach(img => {
                    if (img.getBoundingClientRect().top < window.innerHeight + 200) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                });
            }, 100);
        });
    }
}

// Optimize star rating rendering
function optimizeStarRating() {
    const starDisplay = document.getElementById('chefRatingDisplay');
    const ratingText = document.getElementById('chefRatingText');
    
    if (!starDisplay || !ratingText) return;
    
    // Cache DOM elements
    const starElements = [];
    
    // Use requestAnimationFrame for smooth rendering
    function renderStars() {
        requestAnimationFrame(() => {
            const fragment = document.createDocumentFragment();
            
            // Clear existing stars
            starElements.forEach(el => el.remove());
            starElements.length = 0;
            
            // Add new stars
            for (let i = 0; i < 5; i++) {
                const star = document.createElement('i');
                star.className = 'fas fa-star';
                star.style.cssText = 'color: #ffc107; font-size: 16px; transition: color 0.3s;';
                fragment.appendChild(star);
                starElements.push(star);
            }
            
            starDisplay.appendChild(fragment);
        });
    }
    
    return { renderStars };
}

// Debounce function for performance
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

// Throttle function for scroll events
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Initialize performance optimizations
document.addEventListener('DOMContentLoaded', function() {
    setupLazyLoading();
    optimizeStarRating();
});
