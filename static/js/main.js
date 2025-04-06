// Main JavaScript for the A-Level AI Assistant App

// Show loading spinner
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="d-flex justify-content-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
        `;
    }
}

// Hide loading spinner
function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '';
    }
}

// Show a toast notification
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container');
    
    if (!toastContainer) {
        // Create toast container if it doesn't exist
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }
    
    const toastId = 'toast-' + Date.now();
    const toastHTML = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header ${type === 'error' ? 'bg-danger text-white' : 'bg-success text-white'}">
                <strong class="me-auto">${type === 'error' ? 'Error' : 'Success'}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    document.getElementById('toast-container').innerHTML += toastHTML;
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Remove toast after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function () {
        toastElement.remove();
    });
}

// Process Paper - Admin Function
function processPaper(paperId) {
    // Show the processing modal
    const processingModal = new bootstrap.Modal(document.getElementById('processingModal'));
    processingModal.show();
    
    // Reset log area
    document.getElementById('processingLogs').innerHTML = 
        '<div class="alert alert-info">Processing started...</div>';
    
    // Step 1: Clip questions
    clipQuestions(paperId);
}

// Clip Questions from Paper - Admin Function
function clipQuestions(paperId) {
    showLoading('clipStatus');
    document.getElementById('processingLogs').innerHTML += 
        '<div class="alert alert-info">Clipping questions from paper...</div>';
    
    fetch(`/admin/process/${paperId}/clip`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        hideLoading('clipStatus');
        
        if (data.success) {
            document.getElementById('processingLogs').innerHTML += 
                `<div class="alert alert-success">${data.message}</div>`;
                
            // Move to step 2: Generate answers
            generateAnswers(paperId);
        } else {
            document.getElementById('processingLogs').innerHTML += 
                `<div class="alert alert-danger">Error: ${data.message}</div>`;
        }
    })
    .catch(error => {
        hideLoading('clipStatus');
        document.getElementById('processingLogs').innerHTML += 
            `<div class="alert alert-danger">Error: ${error.message}</div>`;
    });
}

// Generate Answers for Questions - Admin Function
function generateAnswers(paperId) {
    showLoading('answerStatus');
    document.getElementById('processingLogs').innerHTML += 
        '<div class="alert alert-info">Generating answers for questions using AI...</div>';
    
    fetch(`/admin/process/${paperId}/generate_answers`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        hideLoading('answerStatus');
        
        if (data.success) {
            document.getElementById('processingLogs').innerHTML += 
                `<div class="alert alert-success">${data.message}</div>`;
            
            // Final success message
            document.getElementById('processingLogs').innerHTML += 
                `<div class="alert alert-success">Paper processing complete! You can now close this window.</div>`;
                
            // Update UI to reflect processed state
            document.getElementById('paperStatus').innerHTML = 
                '<span class="badge bg-success">Processed</span>';
            
            // Refresh logs
            refreshLogs(paperId);
        } else {
            document.getElementById('processingLogs').innerHTML += 
                `<div class="alert alert-danger">Error: ${data.message}</div>`;
        }
    })
    .catch(error => {
        hideLoading('answerStatus');
        document.getElementById('processingLogs').innerHTML += 
            `<div class="alert alert-danger">Error: ${error.message}</div>`;
    });
}

// Refresh Processing Logs - Admin Function
function refreshLogs(paperId) {
    fetch(`/admin/view_logs/${paperId}`)
    .then(response => response.json())
    .then(logs => {
        const logsElement = document.getElementById('logsList');
        if (logsElement) {
            logsElement.innerHTML = '';
            
            logs.forEach(log => {
                const statusClass = log.status === 'Success' ? 'text-success' : 'text-danger';
                
                logsElement.innerHTML += `
                    <div class="log-entry mb-2 p-2 border-bottom">
                        <div><strong>${log.action}</strong> <span class="${statusClass}">${log.status}</span></div>
                        <div>${log.message}</div>
                        <div class="text-muted small">${log.timestamp}</div>
                    </div>
                `;
            });
        }
    })
    .catch(error => {
        console.error('Error fetching logs:', error);
    });
}

// View Question Answer - User Function
function viewAnswer(questionId) {
    showLoading(`answer-${questionId}`);
    
    fetch(`/user/api/answer/${questionId}`)
    .then(response => response.json())
    .then(data => {
        hideLoading(`answer-${questionId}`);
        
        if (data.success) {
            // Format and display the answer
            const formattedAnswer = formatAnswer(data.answer);
            document.getElementById(`answer-${questionId}`).innerHTML = formattedAnswer;
        } else {
            document.getElementById(`answer-${questionId}`).innerHTML = 
                `<div class="alert alert-danger">${data.message}</div>`;
        }
    })
    .catch(error => {
        hideLoading(`answer-${questionId}`);
        document.getElementById(`answer-${questionId}`).innerHTML = 
            `<div class="alert alert-danger">Error retrieving answer: ${error.message}</div>`;
    });
}

// Get Answer Explanation - User Function
function explainAnswer(questionId) {
    showLoading(`explanation-${questionId}`);
    
    fetch(`/user/api/explain/${questionId}`)
    .then(response => response.json())
    .then(data => {
        hideLoading(`explanation-${questionId}`);
        
        if (data.success) {
            // Format and display the explanation
            const formattedExplanation = formatAnswer(data.explanation);
            document.getElementById(`explanation-${questionId}`).innerHTML = formattedExplanation;
        } else {
            document.getElementById(`explanation-${questionId}`).innerHTML = 
                `<div class="alert alert-danger">${data.message}</div>`;
        }
    })
    .catch(error => {
        hideLoading(`explanation-${questionId}`);
        document.getElementById(`explanation-${questionId}`).innerHTML = 
            `<div class="alert alert-danger">Error retrieving explanation: ${error.message}</div>`;
    });
}

// Format text with line breaks and potential LaTeX
function formatAnswer(text) {
    // Replace line breaks with HTML breaks
    let formatted = text.replace(/\n/g, '<br>');
    
    // Potentially implement LaTeX rendering here if desired
    
    return `<div class="answer-content">${formatted}</div>`;
}

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Set up toast container
    if (!document.getElementById('toast-container')) {
        const toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
});
