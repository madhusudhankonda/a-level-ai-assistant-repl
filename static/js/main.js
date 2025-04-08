/**
 * Show a loading indicator
 * @param {string} elementId - ID of the element to update
 */
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="d-flex justify-content-center my-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
            <p class="text-center text-muted">Please wait...</p>
        `;
    }
}

/**
 * Hide a loading indicator
 * @param {string} elementId - ID of the element to update
 */
function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '';
    }
}

/**
 * Show a toast notification
 * @param {string} message - The message to show
 * @param {string} type - The type of toast (success, danger, warning, info)
 */
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastTitle = document.getElementById('toast-title');
    const toastBody = document.getElementById('toast-body');
    
    // Set the title based on type
    let title = 'Notification';
    switch (type) {
        case 'success':
            title = 'Success';
            break;
        case 'danger':
            title = 'Error';
            break;
        case 'warning':
            title = 'Warning';
            break;
        case 'info':
            title = 'Information';
            break;
    }
    
    // Update the toast content
    toastTitle.textContent = title;
    toastBody.textContent = message;
    
    // Add the appropriate background color class
    toast.className = 'toast';
    toast.classList.add(`bg-${type === 'danger' ? 'danger' : (type === 'warning' ? 'warning' : 'light')}`);
    
    if (type === 'danger' || type === 'warning') {
        toast.classList.add('text-white');
    } else {
        toast.classList.remove('text-white');
    }
    
    // Create and show the toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

/**
 * Format explanation text for display
 * @param {string} text - The explanation text to format
 * @returns {string} Formatted HTML
 */
function formatExplanation(text) {
    if (!text) return '';
    
    // Replace line breaks with paragraphs
    let formatted = text.replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>');
    formatted = '<p>' + formatted + '</p>';
    
    // Trigger MathJax rendering after a small delay to ensure DOM is updated
    setTimeout(function() {
        if (typeof MathJax !== 'undefined' && MathJax.typesetPromise) {
            console.log('Triggering MathJax typesetting from main.js');
            MathJax.typesetPromise()
                .then(() => console.log('MathJax typesetting complete'))
                .catch(err => console.error('MathJax typesetting failed:', err));
        } else {
            console.warn('MathJax not available for typesetting');
        }
    }, 500);
    
    return formatted;
}
