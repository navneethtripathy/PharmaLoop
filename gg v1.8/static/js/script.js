/**
 * PharmaLoop - Main JavaScript File
 * Handles homepage animations, stats loading, and smooth scrolling
 */

// Counter animation for homepage stats
function animateCounter(id, end, duration = 2000) {
  const element = document.getElementById(id);
  if (!element) return;
  
  const start = 0;
  const increment = end / (duration / 16);
  let current = start;
  
  const timer = setInterval(() => {
    current += increment;
    if (current >= end) {
      element.textContent = Math.floor(end);
      clearInterval(timer);
    } else {
      element.textContent = Math.floor(current);
    }
  }, 16);
}

// Load stats on homepage
function loadHomepageStats() {
  if (document.getElementById('medCount')) {
    fetch('/api/stats')
      .then(response => {
        if (!response.ok) {
          throw new Error('Stats API failed');
        }
        return response.json();
      })
      .then(stats => {
        console.log('✅ Stats loaded:', stats);
        animateCounter('medCount', stats.medicines_saved || 1250);
        animateCounter('peopleCount', stats.people_helped || 340);
        animateCounter('wasteCount', stats.waste_reduced || 890);
      })
      .catch(error => {
        console.warn('⚠️ Using default stats:', error);
        // Use default values if API fails
        animateCounter('medCount', 1250);
        animateCounter('peopleCount', 340);
        animateCounter('wasteCount', 890);
      });
  }
}

// Smooth scrolling for anchor links
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      
      // Ignore empty hash links
      if (href === '#' || href === '#!') {
        e.preventDefault();
        return;
      }
      
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
        
        // Update URL without jumping
        if (window.history && window.history.pushState) {
          window.history.pushState(null, null, href);
        }
      }
    });
  });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', function() {
    loadHomepageStats();
    initSmoothScroll();
  });
} else {
  // DOM already loaded
  loadHomepageStats();
  initSmoothScroll();
}

// Also handle page show event (for back/forward navigation)
window.addEventListener('pageshow', function(event) {
  // Reload stats if page is shown from cache
  if (event.persisted) {
    loadHomepageStats();
  }
});

// Modal utilities (for all pages)
window.showModal = function(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
  }
};

window.closeModal = function(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.style.display = 'none';
    document.body.style.overflow = 'auto'; // Restore scrolling
  }
};

// Close modal when clicking outside
window.addEventListener('click', function(event) {
  if (event.target.classList.contains('modal')) {
    event.target.style.display = 'none';
    document.body.style.overflow = 'auto';
  }
});

// Close modal with Escape key
window.addEventListener('keydown', function(event) {
  if (event.key === 'Escape') {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
      if (modal.style.display === 'block') {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
      }
    });
  }
});

// Utility: Format number with commas
window.formatNumber = function(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
};

// Utility: Format currency (Indian Rupees)
window.formatCurrency = function(amount) {
  return '₹' + amount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
};

// Utility: Calculate days until expiry
window.daysUntilExpiry = function(expiryDate) {
  const today = new Date();
  const expiry = new Date(expiryDate);
  const diffTime = expiry - today;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays;
};

// Utility: Get status badge class
window.getStatusColor = function(status) {
  const colors = {
    'SAFE': 'green',
    'REDISTRIBUTE': 'yellow',
    'CRITICAL': 'red',
    'PENDING': 'gray',
    'COMPLETED': 'blue'
  };
  return colors[status.toUpperCase()] || 'gray';
};

// Navbar scroll effect (optional enhancement)
let lastScrollTop = 0;
window.addEventListener('scroll', function() {
  const navbar = document.querySelector('.navbar');
  if (!navbar) return;
  
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
  
  if (scrollTop > 100) {
    navbar.classList.add('navbar-scrolled');
  } else {
    navbar.classList.remove('navbar-scrolled');
  }
  
  lastScrollTop = scrollTop;
}, false);

// Loading state helper
window.setLoading = function(buttonElement, isLoading, loadingText = 'Loading...') {
  if (!buttonElement) return;
  
  if (isLoading) {
    buttonElement.dataset.originalText = buttonElement.textContent;
    buttonElement.textContent = loadingText;
    buttonElement.disabled = true;
  } else {
    buttonElement.textContent = buttonElement.dataset.originalText || buttonElement.textContent;
    buttonElement.disabled = false;
  }
};

// Toast notification helper
window.showToast = function(message, type = 'info', duration = 3000) {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  
  // Add styles if not already in CSS
  toast.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    padding: 15px 20px;
    background: ${type === 'success' ? '#2ecc71' : type === 'error' ? '#e74c3c' : '#3498db'};
    color: white;
    border-radius: 8px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.2);
    z-index: 10000;
    animation: slideIn 0.3s ease-out;
  `;
  
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.style.animation = 'slideOut 0.3s ease-in';
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 300);
  }, duration);
};

// Add CSS animations for toast
if (!document.getElementById('toast-animations')) {
  const style = document.createElement('style');
  style.id = 'toast-animations';
  style.textContent = `
    @keyframes slideIn {
      from {
        transform: translateX(400px);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
    
    @keyframes slideOut {
      from {
        transform: translateX(0);
        opacity: 1;
      }
      to {
        transform: translateX(400px);
        opacity: 0;
      }
    }
    
    .navbar-scrolled {
      box-shadow: 0 5px 20px rgba(0,0,0,0.15) !important;
    }
  `;
  document.head.appendChild(style);
}

// Console branding (fun easter egg)
console.log('%c🏥 PharmaLoop', 'color: #2ecc71; font-size: 24px; font-weight: bold;');
console.log('%cReducing medicine waste with AI 🤖', 'color: #3498db; font-size: 14px;');
console.log('%cBuilt for Healthcare Sustainability 💚', 'color: #27ae60; font-size: 12px;');

// Debug mode checker
window.DEBUG = window.location.hostname === 'localhost';

if (window.DEBUG) {
  console.log('%c🔧 Debug Mode Enabled', 'color: #f39c12; font-weight: bold;');
}
