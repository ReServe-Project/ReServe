// product_details/static/product_details/js/product_details.js

const productDetails = (function() {
    // Private variables
    let config = {};
    
    // CSRF token setup for AJAX
    function getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }

    // AJAX form submission
    function submitFormAjax(form, url, successCallback) {
        const formData = new FormData(form);
        
        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCSRFToken()
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (successCallback) successCallback(data);
                showNotification(data.message, 'success');
            } else {
                showNotification(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('An error occurred. Please try again.', 'error');
        });
    }

    // Notification system
    function showNotification(message, type) {
        // Remove existing notifications
        const existingAlert = document.querySelector('.ajax-notification');
        if (existingAlert) {
            existingAlert.remove();
        }
        
        const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
        const notification = document.createElement('div');
        notification.className = `alert ${alertClass} alert-dismissible fade show ajax-notification`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Add to top of content
        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(notification, container.firstChild);
        }
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    // Update reviews section
    function updateReviewsSection(data) {
        const reviewsContainer = document.querySelector('.card.shadow-sm.p-4');
        if (reviewsContainer && data.reviews_html) {
            reviewsContainer.innerHTML = data.reviews_html;
            reinitializeReviewEvents();
        }
    }

    // Reinitialize event listeners after AJAX updates
    function reinitializeReviewEvents() {
        // Star rating interaction
        initializeStarRatings();
        
        // Delete review buttons
        document.querySelectorAll('.delete-review-btn').forEach(button => {
            button.addEventListener('click', function() {
                const reviewId = this.getAttribute('data-review-id');
                deleteReviewAjax(reviewId);
            });
        });
        
        // Modal forms
        initializeModalForms();
    }

    // Initialize star ratings
    function initializeStarRatings() {
        // For new review modal
        const starLabels = document.querySelectorAll('#reviewModal .star-label');
        starLabels.forEach((label, index) => {
            label.addEventListener('click', function() {
                const starValue = index + 1;
                
                starLabels.forEach((star, starIndex) => {
                    if (starIndex < starValue) {
                        star.classList.remove('text-muted');
                        star.classList.add('text-warning');
                    } else {
                        star.classList.remove('text-warning');
                        star.classList.add('text-muted');
                    }
                });
                
                const radioInput = document.getElementById(`star${starValue}`);
                if (radioInput) radioInput.checked = true;
            });
        });
        
        // For edit review modal
        const editStarLabels = document.querySelectorAll('#editReviewModal .star-label');
        editStarLabels.forEach((label, index) => {
            label.addEventListener('click', function() {
                const starValue = index + 1;
                
                editStarLabels.forEach((star, starIndex) => {
                    if (starIndex < starValue) {
                        star.classList.remove('text-muted');
                        star.classList.add('text-warning');
                    } else {
                        star.classList.remove('text-warning');
                        star.classList.add('text-muted');
                    }
                });
                
                const radioInput = document.getElementById(`editStar${starValue}`);
                if (radioInput) radioInput.checked = true;
            });
        });
        
        // Initialize edit modal with current rating if available
        if (config.currentRating && config.currentRating > 0) {
            editStarLabels.forEach((star, index) => {
                if (index < config.currentRating) {
                    star.classList.remove('text-muted');
                    star.classList.add('text-warning');
                }
            });
        }
    }

    // Initialize modal forms
    function initializeModalForms() {
        // Add review form
        const addReviewForm = document.querySelector('#reviewModal form');
        if (addReviewForm) {
            addReviewForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const url = this.getAttribute('action');
                
                submitFormAjax(this, url, function(data) {
                    updateReviewsSection(data);
                    const modal = bootstrap.Modal.getInstance(document.getElementById('reviewModal'));
                    if (modal) modal.hide();
                    // Reset form
                    addReviewForm.reset();
                    // Reset stars
                    document.querySelectorAll('#reviewModal .star-label').forEach(star => {
                        star.classList.remove('text-warning');
                        star.classList.add('text-muted');
                    });
                });
            });
        }
        
        // Edit review form
        const editReviewForm = document.querySelector('#editReviewModal form');
        if (editReviewForm) {
            editReviewForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const url = this.getAttribute('action');
                
                submitFormAjax(this, url, function(data) {
                    updateReviewsSection(data);
                    const modal = bootstrap.Modal.getInstance(document.getElementById('editReviewModal'));
                    if (modal) modal.hide();
                });
            });
        }
    }

    // Delete review via AJAX
    function deleteReviewAjax(reviewId) {
        if (!confirm('Are you sure you want to delete your review?')) {
            return;
        }
        
        fetch(`/product_details/review/${reviewId}/delete/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateReviewsSection(data);
                showNotification(data.message, 'success');
            } else {
                showNotification(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('An error occurred. Please try again.', 'error');
        });
    }

    // Book class via AJAX
    function bookClassAjax(classId) {
        fetch(`/product_details/class/${classId}/book/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                // Redirect to checkout
                setTimeout(() => {
                    window.location.href = '/checkout/';
                }, 1000);
            } else {
                showNotification(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('An error occurred. Please try again.', 'error');
        });
    }

    // Initialize everything
    function init(userConfig) {
        config = { ...userConfig };
        
        // Initialize review events
        reinitializeReviewEvents();
        
        // AJAX booking
        const bookForm = document.querySelector('form[action*="book_class"]');
        if (bookForm) {
            bookForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const action = this.getAttribute('action');
                const classId = action.split('/').filter(Boolean).pop();
                bookClassAjax(classId);
            });
        }
        
        // Modal reset handlers
        const reviewModal = document.getElementById('reviewModal');
        const editReviewModal = document.getElementById('editReviewModal');
        
        if (reviewModal) {
            reviewModal.addEventListener('hidden.bs.modal', function () {
                document.querySelectorAll('#reviewModal .star-label').forEach(star => {
                    star.classList.remove('text-warning');
                    star.classList.add('text-muted');
                });
                const form = document.querySelector('#reviewModal form');
                if (form) form.reset();
            });
        }
        
        if (editReviewModal) {
            editReviewModal.addEventListener('hidden.bs.modal', function () {
                // Don't reset edit modal as it should keep current values
            });
        }
        
        console.log('Product Details module initialized');
    }

    // Public API
    return {
        init: init,
        updateReviewsSection: updateReviewsSection,
        showNotification: showNotification
    };
})();

// Make it available globally
window.productDetails = productDetails;

// Auto-initialize if DOM is already loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        window.productDetails.init({});
    });
} else {
    window.productDetails.init({});
}