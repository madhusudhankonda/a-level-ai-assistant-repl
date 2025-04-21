/**
 * Camera Capture & Image Upload Functionality
 * Provides image capture and upload features for the AI tutor app
 */

document.addEventListener('DOMContentLoaded', function() {
    // Global modal reference
    window.aiConsentModal = new bootstrap.Modal(document.getElementById('aiConsentModal'));

    // Global variable to store captured image
    let capturedImageData;

    // Get all DOM elements
    const elements = {
        // Main tabs
        captureTab: document.getElementById('capture-tab'),
        feedbackTab: document.getElementById('feedback-tab'),
        
        // Analysis mode
        analysisMode: document.getElementById('analysis-mode'),
        
        // Camera elements
        video: document.getElementById('video'),
        canvas: document.getElementById('canvas'),
        captureBtn: document.getElementById('capture-btn'),
        retakeBtn: document.getElementById('retake-btn'),
        retakeBtnText: document.getElementById('retake-btn-text'),
        analyzeBtn: document.getElementById('analyze-btn'),
        analyzeBtnText: document.getElementById('analyze-btn-text'),
        cameraContainer: document.getElementById('camera-container'),
        captureResult: document.getElementById('capture-result'),
        instructionText: document.getElementById('instruction-text'),
        captureTitle: document.getElementById('capture-title'),
        resultLabel: document.getElementById('result-label'),
        
        // Subject selection
        subjectSelect: document.getElementById('subject'),
        
        // File upload
        fileInput: document.getElementById('file-input'),
        
        // API status
        apiStatusAlert: document.getElementById('api-status-alert'),
        apiStatusMessage: document.getElementById('api-status-message'),
        
        // Feedback elements
        feedbackLoading: document.getElementById('feedback-loading'),
        feedbackResult: document.getElementById('feedback-result'),
        feedbackPlaceholder: document.getElementById('feedback-placeholder'),
        feedbackError: document.getElementById('feedback-error'),
        feedbackContent: document.getElementById('feedback-content'),
        explanationContent: document.getElementById('explanation-content'),
        tipsContent: document.getElementById('tips-content'),
        feedbackSubject: document.getElementById('feedback-subject'),
        feedbackScore: document.getElementById('feedback-score'),
        errorMessage: document.getElementById('error-message'),
        startOverBtn: document.getElementById('start-over-btn'),
        
        // Feedback image
        feedbackImageCanvas: document.getElementById('feedback-image-canvas'),
        feedbackImageContainer: document.getElementById('feedback-image-container'),
        toggleImageBtn: document.getElementById('toggle-image-btn'),
        toggleImageText: document.getElementById('toggle-image-text')
    };
    
    // Camera stream
    let stream;
    
    // Functions
    
    // Update UI based on selected mode
    function updateModeUI() {
        const mode = elements.analysisMode.value;
        
        if (mode === 'explanation-only') {
            // Question-only mode
            elements.instructionText.textContent = 'Upload or take a clear photo of just the question to get an explanation.';
            elements.captureTitle.textContent = 'Capture or Upload Question';
            elements.resultLabel.textContent = 'Question Image:';
            elements.analyzeBtnText.textContent = 'Get AI Explanation';
            // Hide score badge
            if (elements.feedbackScore) {
                elements.feedbackScore.style.display = 'none';
            }
        } else {
            // Answer feedback mode
            elements.instructionText.textContent = 'Upload or take a photo that shows both the question and your answer on the same page.';
            elements.captureTitle.textContent = 'Capture or Upload Your Work';
            elements.resultLabel.textContent = 'Captured Image:';
            elements.analyzeBtnText.textContent = 'Get AI Feedback & Marking';
            // Show score badge
            if (elements.feedbackScore) {
                elements.feedbackScore.style.display = 'inline-block';
            }
        }
    }
    
    // Process the selected file
    function processFile(file) {
        console.log("Processing file:", file.name);
        
        // Validate file type
        if (!file.type.match('image.*')) {
            alert('Please select an image file (JPG, PNG, or GIF).');
            return;
        }
        
        // Validate file size (10MB max)
        if (file.size > 10 * 1024 * 1024) {
            alert('File size exceeds 10MB limit. Please select a smaller file.');
            return;
        }
        
        // Create a FileReader to read the image
        const reader = new FileReader();
        
        // Set up the FileReader onload event
        reader.onload = function(e) {
            console.log("File loaded, processing image...");
            
            // Create an image element to get dimensions
            const img = new Image();
            
            img.onload = function() {
                console.log("Image loaded, dimensions:", img.width, "x", img.height);
                
                // Get the canvas context
                const context = elements.canvas.getContext('2d');
                
                // Scale down if necessary
                const maxWidth = 600;
                const maxHeight = 450;
                let width = img.width;
                let height = img.height;
                
                if (width > maxWidth || height > maxHeight) {
                    const ratio = Math.min(maxWidth / width, maxHeight / height);
                    width = Math.floor(width * ratio);
                    height = Math.floor(height * ratio);
                }
                
                // Set canvas dimensions
                elements.canvas.width = width;
                elements.canvas.height = height;
                
                // Draw the image on the canvas
                context.drawImage(img, 0, 0, width, height);
                
                // Save the image data with reduced quality
                capturedImageData = elements.canvas.toDataURL('image/jpeg', 0.6);
                
                // Log size for debugging
                console.log('Processed image size:', Math.round(capturedImageData.length / 1024), 'KB');
                
                // Show the result and hide the upload interface
                elements.captureResult.style.display = 'block';
                document.getElementById('upload-container').style.display = 'none';
                elements.cameraContainer.style.display = 'none';
                
                // Update the retake button text for uploads
                elements.retakeBtnText.textContent = 'Upload Different Image';
            };
            
            // Set the image source
            img.src = e.target.result;
            
            // Also store the full data URL for sending to server
            capturedImageData = e.target.result;
        };
        
        // Read the file as a data URL
        reader.readAsDataURL(file);
    }
    
    // Start camera
    async function startCamera() {
        try {
            // Try to access the camera
            stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: 'environment', // Use back camera if available
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            });
            
            // Show the video stream
            elements.video.srcObject = stream;
            
            // Show camera UI
            elements.cameraContainer.style.display = 'block';
            elements.captureBtn.disabled = false;
        } catch (err) {
            console.error('Error accessing camera:', err);
            elements.cameraContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Unable to access camera: ${err.message}
                </div>
                <p class="mt-3">Make sure your browser has permission to access the camera and try again.</p>
            `;
            elements.captureBtn.disabled = true;
        }
    }
    
    // Stop camera stream
    function stopCameraStream() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    }
    
    // Function to check OpenAI API availability
    function checkOpenAIStatus() {
        // Show the API status alert
        elements.apiStatusAlert.style.display = 'block';
        elements.apiStatusAlert.className = 'alert alert-warning mb-4';
        elements.apiStatusMessage.textContent = 'Checking OpenAI API connection...';
        
        // Make a request with a timeout
        fetch('/api/test-openai')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // API is available
                    elements.apiStatusAlert.className = 'alert alert-success mb-4';
                    elements.apiStatusMessage.textContent = 'OpenAI API connection successful. You can analyze images.';
                    
                    // Hide after 3 seconds
                    setTimeout(() => {
                        elements.apiStatusAlert.style.display = 'none';
                    }, 3000);
                    
                    // Enable analyze button
                    elements.analyzeBtn.disabled = false;
                } else {
                    // API error
                    showAPIError('OpenAI API connection failed. Image analysis will not work.', data.message);
                }
            })
            .catch(error => {
                showAPIError('OpenAI API connection failed. Image analysis will not work.', error.message);
            });
    }
    
    // Show API error
    function showAPIError(message, details) {
        elements.apiStatusAlert.className = 'alert alert-danger mb-4';
        elements.apiStatusMessage.textContent = message;
        
        // Add retry button
        const retryButton = document.createElement('button');
        retryButton.className = 'btn btn-sm btn-outline-danger mt-2';
        retryButton.innerHTML = '<i class="fas fa-sync-alt me-1"></i> Retry Connection';
        retryButton.onclick = function() {
            if (elements.apiStatusAlert.querySelector('button')) {
                elements.apiStatusAlert.querySelector('button').remove();
            }
            if (elements.apiStatusAlert.querySelector('div.mt-3')) {
                elements.apiStatusAlert.querySelector('div.mt-3').remove();
            }
            checkOpenAIStatus();
        };
        
        // Add error details if available
        if (details) {
            const detailsDiv = document.createElement('div');
            detailsDiv.className = 'mt-3 small';
            detailsDiv.innerHTML = `<strong>Details:</strong> ${details}`;
            
            // Insert elements
            elements.apiStatusAlert.appendChild(detailsDiv);
        }
        
        elements.apiStatusAlert.appendChild(retryButton);
        
        // Disable analyze button
        elements.analyzeBtn.disabled = true;
    }
    
    // Proceed with analysis after consent - make it available globally
    window.proceedWithAnalysis = function() {
        // Disable the analyze button during processing
        elements.analyzeBtn.disabled = true;
        elements.analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Processing...';
        
        // Stop camera
        stopCameraStream();
        
        // Enable and show feedback step
        elements.feedbackTab.disabled = false;
        elements.feedbackTab.click();
        
        // Show loading
        elements.feedbackLoading.style.display = 'block';
        elements.feedbackResult.style.display = 'none';
        elements.feedbackPlaceholder.style.display = 'none';
        elements.feedbackError.style.display = 'none';
        
        // Get subject and mode
        const subject = elements.subjectSelect.value;
        const mode = elements.analysisMode.value;
        
        if (mode === 'explanation-only') {
            // Question-only analysis
            console.log(`Sending analysis request (explanation mode) for subject: ${subject}`);
            fetch('/api/analyze-captured-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    image_data: capturedImageData,
                    subject: subject,
                    mode: 'question-only'
                })
            })
            .then(response => {
                if (!response.ok) {
                    // Check if it's an authentication error
                    if (response.status === 401 || response.url.includes('login')) {
                        window.location.href = '/auth/login?next=' + encodeURIComponent(window.location.pathname);
                        throw new Error('Authentication required. Please log in.');
                    }
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => handleExplanationResponse(data))
            .catch(error => {
                console.error('Error in analyze-captured-image:', error);
                handleAnalysisError(error);
            });
        } else {
            // Answer analysis
            console.log(`Sending analysis request (answer mode) for subject: ${subject}`);
            fetch('/api/analyze-answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question_image: capturedImageData, // Same image for both
                    answer_image: capturedImageData,
                    subject: subject
                })
            })
            .then(response => {
                if (!response.ok) {
                    // Check if it's an authentication error
                    if (response.status === 401 || response.url.includes('login')) {
                        window.location.href = '/auth/login?next=' + encodeURIComponent(window.location.pathname);
                        throw new Error('Authentication required. Please log in.');
                    }
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => handleFeedbackResponse(data))
            .catch(error => {
                console.error('Error in analyze-answer:', error);
                handleAnalysisError(error);
            });
        }
    }
    
    // Display captured image in feedback
    function displayCapturedImageInFeedback() {
        if (capturedImageData && elements.feedbackImageCanvas) {
            const img = new Image();
            img.onload = function() {
                // Get canvas context
                const context = elements.feedbackImageCanvas.getContext('2d');
                
                // Set dimensions
                elements.feedbackImageCanvas.width = img.width;
                elements.feedbackImageCanvas.height = img.height;
                
                // Draw the image
                context.drawImage(img, 0, 0, img.width, img.height);
            };
            
            // Set source
            img.src = capturedImageData;
        }
    }
    
    // Handle explanation-only response
    function handleExplanationResponse(data) {
        // Hide loading
        elements.feedbackLoading.style.display = 'none';
        
        // Reset analyze button
        elements.analyzeBtn.disabled = false;
        elements.analyzeBtn.innerHTML = '<i class="fas fa-lightbulb me-1"></i> <span id="analyze-btn-text">Get Explanation</span>';
        
        if (data.success) {
            // Show explanation
            elements.feedbackResult.style.display = 'block';
            elements.explanationContent.innerHTML = data.explanation;
            elements.feedbackContent.innerHTML = '<div class="alert alert-info">Explanation-only mode: see the full explanation tab for details.</div>';
            elements.tipsContent.innerHTML = '<div class="alert alert-success">Review the full explanation to understand this question thoroughly.</div>';
            
            elements.feedbackSubject.textContent = data.subject;
            elements.feedbackScore.style.display = 'none';
            
            // Update timestamp
            const now = new Date();
            elements.feedbackTimestamp.textContent = `Generated on ${now.toLocaleDateString()} at ${now.toLocaleTimeString()}`;
            
            // Display image
            displayCapturedImageInFeedback();
            
            // Try to typeset any math with MathJax if available
            if (window.MathJax) {
                try {
                    window.MathJax.typeset();
                } catch (err) {
                    console.error('MathJax typesetting failed:', err);
                }
            }
        } else {
            // Show error
            elements.feedbackError.style.display = 'block';
            elements.errorMessage.textContent = data.message || 'An error occurred';
        }
    }
    
    // Handle answer feedback response
    function handleFeedbackResponse(data) {
        // Hide loading
        elements.feedbackLoading.style.display = 'none';
        
        // Reset analyze button
        elements.analyzeBtn.disabled = false;
        elements.analyzeBtn.innerHTML = '<i class="fas fa-lightbulb me-1"></i> <span id="analyze-btn-text">Get Feedback</span>';
        
        if (data.success) {
            // Show feedback
            elements.feedbackResult.style.display = 'block';
            
            // Update feedback content
            elements.feedbackContent.innerHTML = data.feedback || 'No feedback available';
            elements.explanationContent.innerHTML = data.explanation || 'No explanation available';
            elements.tipsContent.innerHTML = data.tips || 'No tips available';
            
            // Update metadata
            elements.feedbackSubject.textContent = data.subject || 'Unknown';
            elements.feedbackScore.textContent = data.score || 'N/A';
            elements.feedbackScore.style.display = 'inline-block';
            
            // Update timestamp
            const now = new Date();
            elements.feedbackTimestamp.textContent = `Generated on ${now.toLocaleDateString()} at ${now.toLocaleTimeString()}`;
            
            // Display image
            displayCapturedImageInFeedback();
            
            // Try to typeset any math with MathJax if available
            if (window.MathJax) {
                try {
                    window.MathJax.typeset();
                } catch (err) {
                    console.error('MathJax typesetting failed:', err);
                }
            }
        } else {
            // Show error
            elements.feedbackError.style.display = 'block';
            elements.errorMessage.textContent = data.message || 'An error occurred';
        }
    }
    
    // Handle analysis errors
    function handleAnalysisError(error) {
        // Hide loading
        elements.feedbackLoading.style.display = 'none';
        
        // Reset analyze button
        elements.analyzeBtn.disabled = false;
        elements.analyzeBtn.innerHTML = '<i class="fas fa-lightbulb me-1"></i> <span id="analyze-btn-text">Analyze with AI</span>';
        
        console.error('API Error:', error);
        
        // Show error
        elements.feedbackError.style.display = 'block';
        
        // Simple error message
        let errorMsg = 'Error processing your request. Please try again.';
        
        // Determine if it's a consent error
        if (error.message && (error.message.includes('403') || 
                              error.message.includes('consent') || 
                              error.message.includes('permission'))) {
            errorMsg = 'Permission error: You may need to provide AI consent or purchase more credits.';
            
            // Don't show consent modal here to avoid double-showing it
            console.log("Consent error in analysis - not showing modal to avoid duplicate");
        } else if (error.message && error.message.includes('Failed to fetch')) {
            errorMsg = 'Connection error: Please check your internet connection and try again.';
        }
        
        elements.errorMessage.innerHTML = errorMsg;
        
        // Add retry button
        const retryButton = document.createElement('button');
        retryButton.className = 'btn btn-outline-primary mt-3';
        retryButton.innerHTML = '<i class="fas fa-redo me-1"></i> Try Again';
        retryButton.onclick = function() {
            // Remove button
            if (elements.errorMessage.nextElementSibling) {
                elements.errorMessage.parentNode.removeChild(elements.errorMessage.nextElementSibling);
            }
            
            // Hide error and go back to capture step
            elements.feedbackError.style.display = 'none';
            elements.captureTab.click();
            
            // Start camera again
            startCamera();
        };
        
        if (!elements.errorMessage.nextElementSibling || !elements.errorMessage.nextElementSibling.classList.contains('btn')) {
            elements.errorMessage.parentNode.appendChild(retryButton);
        }
    }
    
    // Event listeners
    
    // Start camera when tab is shown
    document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(button => {
        button.addEventListener('shown.bs.tab', event => {
            if (event.target.id === 'camera-tab' && elements.cameraContainer.style.display !== 'none') {
                startCamera();
            } else if (event.target.id !== 'camera-tab') {
                stopCameraStream();
            }
        });
    });
    
    // Mode change
    if (elements.analysisMode) {
        elements.analysisMode.addEventListener('change', updateModeUI);
    }
    
    // File input change
    if (elements.fileInput) {
        elements.fileInput.addEventListener('change', function() {
            console.log('File input change detected');
            if (this.files.length > 0) {
                console.log('Processing file:', this.files[0].name);
                processFile(this.files[0]);
            }
        });
    }
    
    // Capture button
    if (elements.captureBtn) {
        elements.captureBtn.addEventListener('click', function() {
            // Get canvas context
            const context = elements.canvas.getContext('2d');
            
            // Calculate dimensions
            const maxWidth = 600;
            const maxHeight = 450;
            let width = elements.video.videoWidth;
            let height = elements.video.videoHeight;
            
            // Scale down if necessary
            if (width > maxWidth || height > maxHeight) {
                const ratio = Math.min(maxWidth / width, maxHeight / height);
                width = Math.floor(width * ratio);
                height = Math.floor(height * ratio);
            }
            
            elements.canvas.width = width;
            elements.canvas.height = height;
            
            // Draw video frame on canvas
            context.drawImage(elements.video, 0, 0, width, height);
            
            // Save image data
            capturedImageData = elements.canvas.toDataURL('image/jpeg', 0.6);
            
            // Log size
            console.log('Captured image size:', Math.round(capturedImageData.length / 1024), 'KB');
            
            // Show captured image
            elements.cameraContainer.style.display = 'none';
            elements.captureResult.style.display = 'block';
        });
    }
    
    // Retake button
    if (elements.retakeBtn) {
        elements.retakeBtn.addEventListener('click', function() {
            // Check active tab
            const cameraTabActive = document.querySelector('#camera-tab').classList.contains('active');
            const uploadTabActive = document.querySelector('#upload-tab').classList.contains('active');
            
            // Hide result
            elements.captureResult.style.display = 'none';
            
            if (cameraTabActive) {
                // Show camera again
                elements.cameraContainer.style.display = 'block';
                elements.retakeBtnText.textContent = 'Try Again';
            } else if (uploadTabActive) {
                // Show upload interface
                document.getElementById('upload-container').style.display = 'block';
                elements.retakeBtnText.textContent = 'Upload Different Image';
            }
        });
    }
    
    // Analyze button
    if (elements.analyzeBtn) {
        elements.analyzeBtn.addEventListener('click', function() {
            console.log("Analyze button clicked");
            
            // Check authentication with server-side logic
            
            // Check consent
            fetch('/api/check-ai-consent')
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("Consent check data:", data);
                    
                    if (data.success && data.consent_given) {
                        // User has consent
                        console.log("User has valid AI consent. Proceeding with analysis.");
                        window.proceedWithAnalysis(); // Call the function on the window object
                    } else {
                        // User needs consent
                        console.log("User needs to provide AI consent. Showing consent modal.");
                        console.log("Consent reason:", data.reason || "Unknown");
                        
                        // Show consent modal
                        if (window.aiConsentModal) {
                            window.aiConsentModal.show();
                        } else {
                            console.error("Consent modal not initialized!");
                            setTimeout(() => {
                                window.aiConsentModal = new bootstrap.Modal(document.getElementById('aiConsentModal'));
                                window.aiConsentModal.show();
                            }, 500);
                        }
                    }
                })
                .catch(error => {
                    console.error("Error checking AI consent:", error);
                    
                    // Show error toast
                    const toastBody = document.getElementById('toast-body');
                    const toastTitle = document.getElementById('toast-title');
                    const toast = new bootstrap.Toast(document.getElementById('toast'));
                    
                    toastTitle.textContent = "Consent Check Error";
                    toastBody.textContent = "There was an error checking your AI consent status. Please try again.";
                    toast.show();
                    
                    // Log error but don't show consent modal again to avoid double modal issue
                    console.log("Consent check error - will not show modal to avoid duplicate display");
                });
        });
    }
    
    // Start over button
    if (elements.startOverBtn) {
        elements.startOverBtn.addEventListener('click', function() {
            // Clear previous capture
            capturedImageData = null;
            
            // Reset UI
            elements.feedbackResult.style.display = 'none';
            elements.feedbackPlaceholder.style.display = 'block';
            
            // Reset upload display
            document.getElementById('upload-container').style.display = 'block';
            
            // Reset analyze button
            elements.analyzeBtn.disabled = false;
            elements.analyzeBtn.innerHTML = '<i class="fas fa-lightbulb me-1"></i> <span id="analyze-btn-text">Analyze with AI</span>';
            
            // Reset capture result
            elements.captureResult.style.display = 'none';
            
            // Go back to capture step
            elements.captureTab.click();
            
            // Go to camera tab
            document.getElementById('camera-tab').click();
            
            // Reset retake button
            elements.retakeBtnText.textContent = 'Try Again';
            
            // Start camera
            startCamera();
        });
    }
    
    // Toggle image expand/collapse
    if (elements.toggleImageBtn) {
        elements.toggleImageBtn.addEventListener('click', function() {
            if (elements.feedbackImageContainer.style.maxHeight === '150px') {
                // Expand
                elements.feedbackImageContainer.style.maxHeight = '100%';
                elements.toggleImageText.textContent = 'Collapse Image';
                this.querySelector('i').classList.remove('fa-expand-alt');
                this.querySelector('i').classList.add('fa-compress-alt');
            } else {
                // Collapse
                elements.feedbackImageContainer.style.maxHeight = '150px';
                elements.toggleImageText.textContent = 'Expand Image';
                this.querySelector('i').classList.remove('fa-compress-alt');
                this.querySelector('i').classList.add('fa-expand-alt');
            }
        });
    }
    
    // Initial setup
    updateModeUI();
    checkOpenAIStatus();
    
    // Clean up on page unload
    window.addEventListener('beforeunload', function() {
        stopCameraStream();
    });
});