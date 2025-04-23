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
        feedbackTimestamp: document.getElementById('feedback-timestamp'),
        errorMessage: document.getElementById('error-message'),
        startOverBtn: document.getElementById('start-over-btn'),
        newUploadBtn: document.getElementById('new-upload-btn'),
        
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
            
            // Start playing the video - critical step to view camera feed
            elements.video.onloadedmetadata = function() {
                // Wait for metadata to be loaded before playing
                elements.video.play()
                    .then(() => {
                        console.log("Camera stream started successfully");
                    })
                    .catch(playError => {
                        console.error("Error playing video:", playError);
                        // Show a specific error for autoplay issues
                        if (playError.name === "NotAllowedError") {
                            elements.cameraContainer.innerHTML = 
                                '<div class="alert alert-warning">' +
                                '<i class="fas fa-exclamation-triangle me-2"></i>' +
                                'Autoplay prevented. Please click the video area to enable the camera.' +
                                '</div>' +
                                '<div class="text-center mt-2 mb-3">' +
                                '<button class="btn btn-primary" id="enable-camera-btn">' +
                                '<i class="fas fa-video me-1"></i> Enable Camera</button>' +
                                '</div>';
                                
                            // Add event listener to the enable button
                            document.getElementById('enable-camera-btn').addEventListener('click', function() {
                                elements.video.play()
                                    .then(() => {
                                        // Restore UI after successful play
                                        elements.cameraContainer.style.display = 'block';
                                        elements.captureBtn.disabled = false;
                                    })
                                    .catch(err => {
                                        console.error("Still cannot play video:", err);
                                    });
                            });
                        }
                    });
            };
            
            // Show camera UI
            elements.cameraContainer.style.display = 'block';
            elements.captureBtn.disabled = false;
        } catch (err) {
            console.error('Error accessing camera:', err);
            elements.cameraContainer.innerHTML = 
                '<div class="alert alert-danger">' +
                '<i class="fas fa-exclamation-circle me-2"></i>' +
                'Unable to access camera: ' + err.message +
                '</div>' +
                '<p class="mt-3">Make sure your browser has permission to access the camera and try again.</p>';
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
                    throw new Error('HTTP error! Status: ' + response.status);
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
            detailsDiv.innerHTML = '<strong>Details:</strong> ' + details;
            
            // Insert elements
            elements.apiStatusAlert.appendChild(detailsDiv);
        }
        
        elements.apiStatusAlert.appendChild(retryButton);
        
        // Disable analyze button
        elements.analyzeBtn.disabled = true;
    }
    
    // Proceed with analysis after consent - make it available globally
    window.proceedWithAnalysis = function() {
        console.log("proceedWithAnalysis called");
        
        // Stop camera if running
        stopCameraStream();
        
        // Get subject and mode - with fallbacks in case elements are undefined
        let subject = 'Mathematics';
        let mode = 'question-only';
        
        try {
            if (elements.subjectSelect) {
                subject = elements.subjectSelect.value;
            }
            if (elements.analysisMode) {
                mode = elements.analysisMode.value;
            }
            console.log('Using subject: ' + subject + ', mode: ' + mode);
        } catch (error) {
            console.error("Error getting subject or mode:", error);
        }
        
        // Validate image data
        if (!capturedImageData) {
            handleAnalysisError(new Error('No image data available. Please capture or upload an image first.'));
            return;
        }
        
        console.log('Image data length: ' + capturedImageData.length + ' characters');
        
        // This check is already done in the analyze button handler, but double-check to be safe
        if (elements.feedbackLoading.style.display !== 'block') {
            // Enable and show feedback step
            elements.feedbackTab.disabled = false;
            elements.feedbackTab.click();
            
            // Show loading
            elements.feedbackLoading.style.display = 'block';
            elements.feedbackResult.style.display = 'none';
            elements.feedbackPlaceholder.style.display = 'none';
            elements.feedbackError.style.display = 'none';
        }
        
        // Start processing timer for debugging
        const startTime = new Date();
        console.log('Starting analysis at ' + startTime.toISOString());
        
        if (mode === 'explanation-only') {
            // Question-only analysis
            console.log('Sending analysis request (explanation mode) for subject: ' + subject);
            
            // Send the actual analysis request with a timeout for safety
            const timeoutPromise = new Promise((_, reject) => {
                setTimeout(() => reject(new Error('Request timed out after 60 seconds')), 60000);
            });
            
            console.log('Preparing to send image analysis request...');
            
            // Create the request payload with exact size logging
            const payload = {
                image_data: capturedImageData,
                subject: subject,
                mode: 'question-only'
            };
            
            // Log payload size for debugging
            const payloadSize = JSON.stringify(payload).length;
            console.log('Request payload size: ' + Math.round(payloadSize / 1024) + ' KB');
            
            // Check if payload is extremely large
            if (payloadSize > 5 * 1024 * 1024) { // 5MB
                console.error('Payload too large:', Math.round(payloadSize / 1024 / 1024), 'MB');
                handleAnalysisError(new Error('The image is too large to process. Please try with a smaller image or lower resolution.'));
                return;
            }
            
            console.log('Sending analysis request to server...');
            const fetchPromise = fetch('/api/analyze-captured-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            // Use Promise.race to implement timeout
            Promise.race([fetchPromise, timeoutPromise])
                .then(response => {
                    const processingTime = (new Date() - startTime) / 1000;
                    console.log('Received server response after ' + processingTime + ' seconds');
                    
                    if (!response || !response.ok) {
                        // Check if it's an authentication error
                        if (response && (response.status === 401 || response.url.includes('login'))) {
                            window.location.href = '/auth/login?next=' + encodeURIComponent(window.location.pathname);
                            throw new Error('Authentication required. Please log in.');
                        }
                        throw new Error('HTTP error! Status: ' + (response ? response.status : 'No response'));
                    }
                    return response.json();
                })
                .then(data => {
                    const totalTime = (new Date() - startTime) / 1000;
                    console.log('Analysis completed in ' + totalTime + ' seconds');
                    handleExplanationResponse(data);
                })
                .catch(error => {
                    console.error('Error in analyze-captured-image:', error);
                    
                    // Add more context to timeout errors
                    if (error.message && error.message.includes('timed out')) {
                        error = new Error('The analysis request timed out. This usually happens when the AI is taking too long to process the image. Try with a clearer image or a simpler question.');
                    }
                    
                    handleAnalysisError(error);
                });
        } else {
            // Answer feedback mode
            console.log('Sending feedback request for subject: ' + subject);
            
            // Use Promise race for timeout
            const timeoutPromise = new Promise((_, reject) => {
                setTimeout(() => reject(new Error('Request timed out after 90 seconds')), 90000);
            });
            
            const fetchPromise = fetch('/api/analyze-answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question_image: capturedImageData,
                    answer_image: capturedImageData, // Using same image, but the AI will analyze both parts
                    subject: subject,
                    mode: 'answer-feedback',
                    combined_image: true
                })
            });
            
            // Use Promise.race to implement timeout
            Promise.race([fetchPromise, timeoutPromise])
                .then(response => {
                    const processingTime = (new Date() - startTime) / 1000;
                    console.log('Received server response after ' + processingTime + ' seconds');
                    
                    if (!response || !response.ok) {
                        // Check if it's an authentication error
                        if (response && (response.status === 401 || response.url.includes('login'))) {
                            window.location.href = '/auth/login?next=' + encodeURIComponent(window.location.pathname);
                            throw new Error('Authentication required. Please log in.');
                        }
                        throw new Error('HTTP error! Status: ' + (response ? response.status : 'No response'));
                    }
                    return response.json();
                })
                .then(data => {
                    const totalTime = (new Date() - startTime) / 1000;
                    console.log('Analysis completed in ' + totalTime + ' seconds');
                    handleFeedbackResponse(data);
                })
                .catch(error => {
                    console.error('Error in analyze-answer:', error);
                    
                    // Add more context to timeout errors
                    if (error.message.includes('timed out')) {
                        error = new Error('The analysis request timed out. This usually happens when the AI is taking too long to process the image. Try with a clearer image or a simpler question.');
                    }
                    
                    handleAnalysisError(error);
                });
        }
    }
    
    // Display captured image in feedback
    function displayCapturedImageInFeedback() {
        console.log("Displaying captured image in feedback");
        
        if (!capturedImageData) {
            console.error("No image data to display");
            return;
        }
        
        if (!elements.feedbackImageCanvas) {
            console.error("Feedback image canvas element not found");
            return;
        }
        
        // Ensure the image container is visible
        if (elements.feedbackImageContainer) {
            elements.feedbackImageContainer.style.display = 'block';
            // Reset any previous max-height settings that might be restricting display
            elements.feedbackImageContainer.style.maxHeight = 'none';
        }
        
        // Try direct image display first
        try {
            // Create a new image element
            const img = new Image();
            
            // Set up error handling
            img.onerror = function(err) {
                console.error("Error loading image:", err);
                
                // Fallback - try to show a visual error indicator
                try {
                    const context = elements.feedbackImageCanvas.getContext('2d');
                    elements.feedbackImageCanvas.width = 400;
                    elements.feedbackImageCanvas.height = 100;
                    context.fillStyle = "#f8d7da";
                    context.fillRect(0, 0, 400, 100);
                    context.font = "14px Arial";
                    context.fillStyle = "#842029";
                    context.fillText("Unable to display image", 20, 50);
                    context.fillText("Check browser console for details", 20, 75);
                } catch (canvasErr) {
                    console.error("Canvas error:", canvasErr);
                }
            };
            
            // Set up successful load handler
            img.onload = function() {
                console.log("Image loaded successfully, dimensions:", img.width, "x", img.height);
                
                try {
                    // Get canvas context
                    const context = elements.feedbackImageCanvas.getContext('2d');
                    
                    // Set dimensions - limit to reasonable size if huge
                    const maxWidth = 800;  // Reduced for better display
                    const maxHeight = 600; // Reduced for better display
                    
                    let drawWidth = img.width;
                    let drawHeight = img.height;
                    
                    // Scale down if necessary, preserving aspect ratio
                    if (drawWidth > maxWidth || drawHeight > maxHeight) {
                        const scale = Math.min(maxWidth / drawWidth, maxHeight / drawHeight);
                        drawWidth = Math.floor(drawWidth * scale);
                        drawHeight = Math.floor(drawHeight * scale);
                    }
                    
                    // Log the final dimensions for debugging
                    console.log("Final image dimensions:", drawWidth, "x", drawHeight);
                    
                    // Set canvas dimensions
                    elements.feedbackImageCanvas.width = drawWidth;
                    elements.feedbackImageCanvas.height = drawHeight;
                    
                    // Clear the canvas first
                    context.clearRect(0, 0, drawWidth, drawHeight);
                    
                    // Draw the image
                    context.drawImage(img, 0, 0, drawWidth, drawHeight);
                    console.log("Image drawn successfully");
                    
                    // Update toggle image button text if available
                    if (elements.toggleImageText) {
                        elements.toggleImageText.textContent = "Expand Image";
                    }
                    
                    // Add click handler to toggle image size
                    if (elements.toggleImageBtn) {
                        // Remove any previous handlers to avoid duplicates
                        elements.toggleImageBtn.onclick = function() {
                            const container = elements.feedbackImageContainer;
                            const isExpanded = container.style.maxHeight === 'none';
                            
                            if (isExpanded) {
                                // Collapse the image
                                container.style.maxHeight = '150px';
                                elements.toggleImageText.textContent = "Expand Image";
                            } else {
                                // Expand the image
                                container.style.maxHeight = 'none';
                                elements.toggleImageText.textContent = "Collapse Image";
                            }
                        };
                    }
                    
                } catch (drawErr) {
                    console.error("Error drawing image:", drawErr);
                }
            };
            
            // Set source - this triggers the loading
            // Add cache buster to prevent browser caching issues
            const cacheBuster = '?cache=' + new Date().getTime();
            console.log("Setting image source, data length:", capturedImageData.length);
            
            // Check if it's a data URI and use directly, otherwise add cache buster
            if (capturedImageData.startsWith('data:')) {
                img.src = capturedImageData;
            } else {
                img.src = capturedImageData + cacheBuster;
            }
            
            // Set a timeout in case the image loading hangs
            setTimeout(function() {
                if (!img.complete) {
                    console.error("Image loading timed out");
                    img.onerror(new Error("Loading timed out"));
                }
            }, 5000);
            
        } catch (err) {
            console.error("Exception in displayCapturedImageInFeedback:", err);
            
            // Try alternative display method if the default fails
            try {
                // Display an error message in the canvas
                const context = elements.feedbackImageCanvas.getContext('2d');
                elements.feedbackImageCanvas.width = 400;
                elements.feedbackImageCanvas.height = 120;
                context.fillStyle = "#fff3cd";
                context.fillRect(0, 0, 400, 120);
                context.font = "14px Arial";
                context.fillStyle = "#856404";
                context.fillText("Image display error: " + (err.message || "Unknown error"), 20, 40);
                context.fillText("Your analysis will still work correctly.", 20, 70);
                context.fillText("Check browser console for details.", 20, 90);
            } catch (fallbackErr) {
                console.error("Even fallback display failed:", fallbackErr);
            }
        }
    }
    
    // Handle explanation-only response
    function handleExplanationResponse(data) {
        console.log("Handling explanation response");
        
        // First, ensure essential UI elements exist
        if (!elements.feedbackLoading || !elements.feedbackResult || !elements.feedbackError) {
            console.error("Critical UI elements missing - check HTML structure");
            alert("Error: The application is missing important elements. Please refresh the page.");
            return;
        }
        
        try {
            // Hide loading
            elements.feedbackLoading.style.display = 'none';
            
            // Reset analyze button (if it exists)
            if (elements.analyzeBtn) {
                elements.analyzeBtn.disabled = false;
                elements.analyzeBtn.innerHTML = '<i class="fas fa-lightbulb me-1"></i> <span id="analyze-btn-text">Get Explanation</span>';
            }
            
            // Safety check - ensure we have valid data
            if (!data) {
                throw new Error("No response data received");
            }
            
            // Debug log
            console.log("Response data type:", typeof data);
            if (typeof data === 'object') {
                console.log("Response data keys:", Object.keys(data));
            }
            
            // Always default to success if the explanation exists
            const isSuccess = data.success !== false && !!data.explanation;
            
            // Handle success case
            if (isSuccess) {
                console.log("Successful response - displaying explanation");
                
                // Show explanation
                elements.feedbackResult.style.display = 'block';
                elements.feedbackError.style.display = 'none';
                
                // Safety check for explanation content
                if (!data.explanation) {
                    console.warn("Missing explanation in successful response");
                    data.explanation = "The AI generated an explanation, but it was empty. Please try again with a clearer image.";
                }
                
                // Update UI with data - with safer HTML handling
                try {
                    // Extra safety check for the explanation content
                    if (typeof data.explanation === 'string') {
                        elements.explanationContent.innerHTML = data.explanation;
                    } else if (data.explanation) {
                        // If it's not a string but exists, convert it to string
                        elements.explanationContent.textContent = JSON.stringify(data.explanation);
                    } else {
                        // Fallback for missing explanation
                        elements.explanationContent.innerHTML = '<div class="alert alert-warning">No explanation content was provided. Please try again.</div>';
                    }
                    
                    // Create nice feedback content
                    elements.feedbackContent.innerHTML = 
                        '<div class="alert alert-success">' +
                        '<h5 class="alert-heading"><i class="fas fa-lightbulb me-2"></i>Question Analysis</h5>' +
                        '<p>This problem has been analyzed by the AI. The explanation tab provides a detailed solution.</p>' +
                        '<hr>' +
                        '<p class="mb-0">Click the "Full Explanation" tab above to see the complete step-by-step solution.</p>' +
                        '</div>';
                    
                    // Tips tab - Extract or generate some useful tips from the explanation
                    let tipContent = '';
                    try {
                        // Try to extract key points or formulas mentioned in the explanation
                        const explanation = data.explanation;
                        
                        // Look for any sections that might have key concepts
                        let conceptSection = '';
                        if (explanation.includes('Key Concepts') || explanation.includes('key concepts')) {
                            // Try to extract the key concepts section
                            const conceptMatch = explanation.match(/key concepts[:\s]+([\s\S]+?)(?=##|\n\n\n|$)/i);
                            if (conceptMatch && conceptMatch[1]) {
                                conceptSection = conceptMatch[1].trim();
                            }
                        }
                        
                        // If we found a concept section, use it; otherwise provide generic tips
                        if (conceptSection) {
                            tipContent = 
                                '<h5>Key Concepts for this Question:</h5>' +
                                '<div class="mb-3">' + conceptSection + '</div>';
                        } else {
                            tipContent = 
                                '<h5>Study Tips:</h5>' +
                                '<ul class="mb-3">' +
                                '<li>Review the full explanation to understand the solution approach</li>' +
                                '<li>Practice similar questions to reinforce your understanding</li>' +
                                '<li>Pay attention to the mathematical techniques used in the solution</li>' +
                                '<li>Try to solve the problem on your own before reviewing the explanation</li>' +
                                '</ul>';
                        }
                    } catch (e) {
                        console.error('Error generating tips:', e);
                        tipContent = 
                            '<div class="alert alert-success">' +
                            '<h5 class="alert-heading"><i class="fas fa-lightbulb me-2"></i>Study Tips</h5>' +
                            '<p>Review the full explanation to understand this question thoroughly.</p>' +
                            '<hr>' +
                            '<p class="mb-0">Try to solve similar problems to practice the concepts demonstrated in the explanation.</p>' +
                            '</div>';
                    }
                    
                    elements.tipsContent.innerHTML = tipContent;
                    
                    console.log("UI updated with explanation data");
                } catch (uiError) {
                    console.error("Error updating UI with explanation:", uiError);
                    elements.explanationContent.innerHTML = '<div class="alert alert-danger">Error rendering explanation. Please try again.</div>';
                }
                
                elements.feedbackSubject.textContent = data.subject || 'Mathematics';
                elements.feedbackScore.style.display = 'none';
                
                // Update timestamp
                const now = new Date();
                elements.feedbackTimestamp.textContent = 'Generated on ' + now.toLocaleDateString() + ' at ' + now.toLocaleTimeString();
                
                // Display captured image (if available)
                try {
                    displayCapturedImageInFeedback();
                } catch (imgErr) {
                    console.error("Failed to display image:", imgErr);
                }
                
                // Try to typeset any math with MathJax if available
                if (window.MathJax) {
                    try {
                        window.MathJax.typeset();
                    } catch (err) {
                        console.error('MathJax typesetting failed:', err);
                    }
                }
            } else {
                // Error handling for explicit errors from server
                console.warn("Error response from server:", data.message || "Unknown error");
                
                // Show error
                elements.feedbackResult.style.display = 'none';
                elements.feedbackError.style.display = 'block';
                elements.errorMessage.textContent = data.message || 'An error occurred processing your request. Please try again.';
                
                // Add retry button if not already present
                if (!elements.errorMessage.nextElementSibling || !elements.errorMessage.nextElementSibling.classList.contains('btn')) {
                    const retryButton = document.createElement('button');
                    retryButton.className = 'btn btn-outline-primary mt-3';
                    retryButton.innerHTML = '<i class="fas fa-redo me-1"></i> Try Again';
                    retryButton.onclick = function() {
                        elements.captureTab.click();
                    };
                    elements.errorMessage.parentNode.appendChild(retryButton);
                }
            }
        } catch (error) {
            // Handle exceptions in response handling
            console.error("Exception in handleExplanationResponse:", error);
            
            // Show error
            elements.feedbackResult.style.display = 'none';
            elements.feedbackError.style.display = 'block';
            elements.errorMessage.textContent = 'An error occurred while processing the AI response. Please try again.';
            
            // Add retry button
            if (!elements.errorMessage.nextElementSibling || !elements.errorMessage.nextElementSibling.classList.contains('btn')) {
                const retryButton = document.createElement('button');
                retryButton.className = 'btn btn-outline-primary mt-3';
                retryButton.innerHTML = '<i class="fas fa-redo me-1"></i> Try Again';
                retryButton.onclick = function() {
                    elements.captureTab.click();
                };
                elements.errorMessage.parentNode.appendChild(retryButton);
            }
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
            elements.feedbackTimestamp.textContent = 'Generated on ' + now.toLocaleDateString() + ' at ' + now.toLocaleTimeString();
            
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
        // Hide loading and reset display states
        elements.feedbackLoading.style.display = 'none';
        elements.feedbackPlaceholder.style.display = 'none';
        elements.feedbackResult.style.display = 'none';
        
        // Reset analyze button if it exists
        if (elements.analyzeBtn) {
            elements.analyzeBtn.disabled = false;
            elements.analyzeBtn.innerHTML = '<i class="fas fa-lightbulb me-1"></i> <span id="analyze-btn-text">Analyze with AI</span>';
        }
        
        console.error('API Error:', error);
        
        // Show error container
        elements.feedbackError.style.display = 'block';
        
        // Extract error message safely
        const errorMessage = error instanceof Error ? error.message : 
                            typeof error === 'string' ? error : 
                            error && error.message ? error.message : 
                            'Unknown error occurred';
        
        console.log("Error details:", errorMessage);
        
        // Default error message with more helpful details
        let errorMsg = 'Error processing your request. Please try again with a clearer image.';
        let errorDetails = '';
        let actionSuggestion = 'Try uploading a different image or capturing again with better lighting.';
        
        // Determine the type of error and provide appropriate messaging
        
        // 1. Consent or permission errors
        if (errorMessage.match(/consent|permission|403|unauthorized access/i)) {
            errorMsg = 'You need to provide consent for AI image analysis.';
            actionSuggestion = 'Please accept the terms and try again.';
        }
        // 2. Authentication errors
        else if (errorMessage.match(/login|auth|401|authenticate|unauthenticated/i)) {
            errorMsg = 'You need to log in to use this feature.';
            actionSuggestion = '<a href="/auth/login?next=' + encodeURIComponent(window.location.pathname) + '">Login now</a> to continue.';
        }
        // 3. Timeout errors
        else if (errorMessage.match(/timeout|timed out|too long/i)) {
            errorMsg = 'The request timed out. This may happen if:';
            errorDetails = 
                '<ul class="my-2">' +
                '<li>The image is too complex or unclear</li>' +
                '<li>The server is experiencing high traffic</li>' +
                '<li>Your internet connection is unstable</li>' +
                '</ul>';
            actionSuggestion = 'Try again with a simpler or clearer image, or try later when traffic may be lower.';
        }
        // 4. Image format or size errors
        else if (errorMessage.match(/image format|image size|too large|file size|resolution/i)) {
            errorMsg = 'There was a problem with the image format or size.';
            actionSuggestion = 'Try a different image in JPG or PNG format, or resize your image to be smaller.';
        }
        // 5. AI/OpenAI errors
        else if (errorMessage.match(/openai|ai service|ai model|gpt/i)) {
            errorMsg = 'The AI analysis service is temporarily unavailable.';
            actionSuggestion = 'Please try again later. If the problem persists, contact support.';
        }
        // 6. Credits or quota errors
        else if (errorMessage.match(/credit|quota|payment|subscription|insufficient/i)) {
            errorMsg = 'You don\'t have enough credits for this operation.';
            actionSuggestion = 'Please <a href="/auth/buy-credits">purchase more credits</a> to continue using AI features.';
        }
        
        // Build final error message
        let errorHtml = '<div class="alert alert-danger">' + errorMsg + '</div>';
        
        if (errorDetails) {
            errorHtml += '<div class="mt-3">' + errorDetails + '</div>';
        }
        
        errorHtml += '<div class="mt-3 alert alert-info"><i class="fas fa-lightbulb me-2"></i> ' + actionSuggestion + '</div>';
        
        // Update error message and display
        elements.errorMessage.innerHTML = errorHtml;
        
        // Add retry button
        const retryButton = document.createElement('button');
        retryButton.className = 'btn btn-outline-primary mt-3';
        retryButton.innerHTML = '<i class="fas fa-redo me-1"></i> Try Again';
        retryButton.onclick = function() {
            // Remove any existing buttons
            if (elements.errorMessage.nextElementSibling) {
                elements.errorMessage.parentNode.removeChild(elements.errorMessage.nextElementSibling);
            }
            
            // Hide error and go back to capture step
            elements.feedbackError.style.display = 'none';
            elements.captureTab.click();
            
            // Start camera again if on the camera tab
            if (document.querySelector('#camera-tab.active')) {
                startCamera();
            }
        };
        
        // Only add the button if it doesn't already exist
        if (!elements.errorMessage.nextElementSibling || !elements.errorMessage.nextElementSibling.classList.contains('btn')) {
            elements.errorMessage.parentNode.appendChild(retryButton);
        }
        
        // Scroll to error message to ensure visibility
        elements.feedbackError.scrollIntoView({ behavior: 'smooth' });
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
        console.log('Setting up file input event listener');
        elements.fileInput.addEventListener('change', function(event) {
            console.log('File input change detected');
            if (this.files && this.files.length > 0) {
                console.log('Processing file:', this.files[0].name);
                // Process the file
                processFile(this.files[0]);
            } else {
                console.error('No files selected or files property is null');
            }
        });
    } else {
        console.error('File input element not found in the DOM. Check the ID in the HTML.');
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
            
            // Ensure we have an image to analyze
            if (!capturedImageData) {
                // Show error
                elements.feedbackTab.click();
                elements.feedbackLoading.style.display = 'none';
                elements.feedbackError.style.display = 'block';
                elements.errorMessage.textContent = 'No image captured or uploaded. Please take or upload a photo first.';
                return;
            }
            
            // Disable analyze button during processing
            elements.analyzeBtn.disabled = true;
            elements.analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Processing...';
            
            // Enable and show feedback step immediately to show loading state
            elements.feedbackTab.disabled = false;
            elements.feedbackTab.click();
            
            // Show loading
            elements.feedbackLoading.style.display = 'block';
            elements.feedbackResult.style.display = 'none';
            elements.feedbackPlaceholder.style.display = 'none';
            elements.feedbackError.style.display = 'none';
            
            // Check consent
            fetch('/api/check-ai-consent')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('HTTP error! Status: ' + response.status);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("Consent check data:", data);
                    
                    if (data.success && data.consent_given) {
                        // User has consent - verify OpenAI connection
                        console.log("User has valid AI consent. Checking OpenAI connection...");
                        
                        // Test OpenAI connection before proceeding
                        return fetch('/api/test-openai')
                            .then(response => response.json())
                            .then(testData => {
                                if (testData.success) {
                                    console.log('OpenAI connection confirmed, proceeding with analysis');
                                    try {
                                        window.proceedWithAnalysis();
                                    } catch (analysisError) {
                                        console.error('Error in proceedWithAnalysis:', analysisError);
                                        // Show error in feedback tab
                                        elements.feedbackLoading.style.display = 'none';
                                        elements.feedbackError.style.display = 'block';
                                        elements.errorMessage.textContent = 'An error occurred starting the analysis. Please try again.';
                                        
                                        // Reset analyze button
                                        elements.analyzeBtn.disabled = false;
                                        elements.analyzeBtn.innerHTML = '<i class="fas fa-lightbulb me-1"></i> <span id="analyze-btn-text">Analyze with AI</span>';
                                    }
                                } else {
                                    console.error('OpenAI test failed:', testData.message);
                                    throw new Error('OpenAI API error: ' + testData.message);
                                }
                            });
                    } else {
                        // User needs consent
                        console.log("User needs to provide AI consent. Showing consent modal.");
                        console.log("Consent reason:", data.reason || "Unknown");
                        
                        // Reset analyze button
                        elements.analyzeBtn.disabled = false;
                        elements.analyzeBtn.innerHTML = '<i class="fas fa-lightbulb me-1"></i> <span id="analyze-btn-text">Analyze with AI</span>';
                        
                        // Go back to capture tab
                        elements.captureTab.click();
                        
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
                    
                    // Reset analyze button
                    elements.analyzeBtn.disabled = false;
                    elements.analyzeBtn.innerHTML = '<i class="fas fa-lightbulb me-1"></i> <span id="analyze-btn-text">Analyze with AI</span>';
                    
                    // Hide loading
                    elements.feedbackLoading.style.display = 'none';
                    
                    // Show error in feedback tab
                    elements.feedbackError.style.display = 'block';
                    elements.errorMessage.textContent = 'Failed to verify your AI consent status. Please try again.';
                    
                    // Add a "Try Again" button
                    if (!elements.errorMessage.nextElementSibling || !elements.errorMessage.nextElementSibling.classList.contains('btn')) {
                        const retryButton = document.createElement('button');
                        retryButton.className = 'btn btn-outline-primary mt-3';
                        retryButton.innerHTML = '<i class="fas fa-redo me-1"></i> Try Again';
                        retryButton.onclick = function() {
                            // Go back to capture tab
                            elements.captureTab.click();
                        };
                        elements.errorMessage.parentNode.appendChild(retryButton);
                    }
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
    
    // Upload New Image button
    if (elements.newUploadBtn) {
        elements.newUploadBtn.addEventListener('click', function() {
            // Clear previous capture
            capturedImageData = null;
            
            // Reset UI while keeping feedback hidden
            elements.feedbackResult.style.display = 'none';
            
            // Show upload display
            document.getElementById('upload-container').style.display = 'block';
            
            // Reset analyze button
            elements.analyzeBtn.disabled = false;
            elements.analyzeBtn.innerHTML = '<i class="fas fa-lightbulb me-1"></i> <span id="analyze-btn-text">Analyze with AI</span>';
            
            // Reset capture result
            elements.captureResult.style.display = 'none';
            
            // Go back to capture step but stay on upload tab
            elements.captureTab.click();
            document.getElementById('upload-tab').click();
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
    // Don't automatically check OpenAI status - wait for user to click Analyze
    
    // Clean up on page unload
    window.addEventListener('beforeunload', function() {
        stopCameraStream();
    });
});