/**
 * Admission Portal - Enhanced Main JavaScript
 * Contains modern functionality for the admission portal
 */

// Function to toggle password visibility
function togglePasswordVisibility(inputId, iconId) {
    const passwordInput = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Function to update application progress
function updateApplicationProgress(completionData) {
    const steps = ['personal', 'education', 'documents'];
    
    steps.forEach(step => {
        const stepElement = document.getElementById(`step-${step}`);
        if (stepElement) {
            if (completionData[step]) {
                stepElement.classList.add('completed');
                stepElement.classList.remove('current');
            } else {
                stepElement.classList.remove('completed');
                stepElement.classList.add('current');
                // Exit the loop at the first incomplete step
                return;
            }
        }
    });
    
    // Update progress percentage with animation
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        // Save original width
        const currentWidth = progressBar.style.width;
        
        // Set width to 0 then animate to target
        progressBar.style.transition = 'none';
        progressBar.style.width = '0%';
        
        // Force reflow
        void progressBar.offsetWidth;
        
        // Animate to target width
        progressBar.style.transition = 'width 1s ease-in-out';
        progressBar.style.width = completionData.completion_percentage + '%';
        progressBar.setAttribute('aria-valuenow', completionData.completion_percentage);
        
        // Update text after delay for smoother appearance
        setTimeout(() => {
            progressBar.textContent = Math.round(completionData.completion_percentage) + '%';
        }, 500);
    }
}

// Function to animate counting from 0 to target number
function animateCounter(element, target, duration = 1000) {
    let start = 0;
    const increment = target / (duration / 16); // 60fps
    const timer = setInterval(() => {
        start += increment;
        if (start >= target) {
            element.textContent = Math.round(target);
            clearInterval(timer);
        } else {
            element.textContent = Math.round(start);
        }
    }, 16);
}

// Function to add staggered entrance animations to elements
function animateElementsIn(selector, delay = 100) {
    const elements = document.querySelectorAll(selector);
    elements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * delay);
    });
}

// Function to detect when elements are in viewport and animate them
function animateOnScroll() {
    const elements = document.querySelectorAll('.animate-on-scroll');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });
    
    elements.forEach(element => {
        observer.observe(element);
    });
}

// Function to validate form fields in real-time
function setupFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                if (input.checkValidity()) {
                    input.classList.remove('is-invalid');
                    input.classList.add('is-valid');
                } else {
                    input.classList.remove('is-valid');
                    input.classList.add('is-invalid');
                }
            });
        });
        
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Highlight the first invalid field and scroll to it
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    firstInvalid.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                }
            }
            
            form.classList.add('was-validated');
        });
    });
}

// Main document ready function
document.addEventListener('DOMContentLoaded', function() {
    // Add animation classes to elements
    document.querySelectorAll('.card').forEach(card => {
        card.classList.add('animate-on-scroll');
    });
    
    // Initialize animations
    animateOnScroll();
    animateElementsIn('.fade-in-element');
    
    // Add navbar shadow on scroll
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add animation to flash messages
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        // Fade out flash messages after 5 seconds
        setTimeout(() => {
            message.classList.add('fade-out');
            setTimeout(() => {
                message.remove();
            }, 500);
        }, 5000);
    });

    // Print functionality with preview dialog
    const printButtons = document.querySelectorAll('.btn-print');
    printButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Show print preview message
            const printMsg = document.createElement('div');
            printMsg.className = 'print-preview-message';
            printMsg.innerHTML = `
                <div class="print-preview-content">
                    <i class="fas fa-print fa-2x mb-3"></i>
                    <h4>Preparing Print View</h4>
                    <p>Your document is being prepared for printing...</p>
                </div>
            `;
            document.body.appendChild(printMsg);
            
            // Show print dialog after brief delay
            setTimeout(() => {
                document.body.removeChild(printMsg);
                window.print();
            }, 800);
        });
    });

    // Confirm submission with custom dialog
    const confirmForm = document.querySelector('form.needs-confirmation');
    if (confirmForm) {
        confirmForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Create modal for confirmation
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.id = 'confirmSubmitModal';
            modal.setAttribute('tabindex', '-1');
            modal.innerHTML = `
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title">Confirm Submission</h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <p>Are you sure you want to submit your application? Once submitted, you will not be able to make any further changes.</p>
                            <p class="small text-muted">Please ensure all information is accurate before confirming.</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="confirmSubmitBtn">Yes, Submit Application</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
            
            // Handle confirmation
            document.getElementById('confirmSubmitBtn').addEventListener('click', () => {
                bsModal.hide();
                confirmForm.removeEventListener('submit', arguments.callee);
                setTimeout(() => {
                    confirmForm.submit();
                }, 500);
            });
            
            // Remove modal from DOM after hiding
            modal.addEventListener('hidden.bs.modal', function () {
                document.body.removeChild(modal);
            });
        });
    }

    // Application progress calculation with animation
    const progressBars = document.querySelectorAll('.progress-bar[data-percentage]');
    progressBars.forEach(bar => {
        const percentage = parseInt(bar.getAttribute('data-percentage'), 10);
        
        // Animate the progress bar
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.transition = 'width 1s ease-out';
            bar.style.width = percentage + '%';
            bar.setAttribute('aria-valuenow', percentage);
            
            // Animate the counter
            const counterEl = bar.querySelector('.counter') || bar;
            let start = 0;
            const duration = 1000;
            const increment = percentage / (duration / 16);
            
            const timer = setInterval(() => {
                start += increment;
                if (start >= percentage) {
                    counterEl.textContent = percentage + '%';
                    clearInterval(timer);
                } else {
                    counterEl.textContent = Math.round(start) + '%';
                }
            }, 16);
        }, 300);
    });

    // Enhanced document file input preview with validation
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        // Create custom file input UI
        const wrapper = document.createElement('div');
        wrapper.className = 'custom-file-wrapper';
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);
        
        const label = document.createElement('label');
        label.className = 'custom-file-label';
        label.innerHTML = `
            <div class="file-placeholder">
                <i class="fas fa-cloud-upload-alt"></i>
                <span>Choose file</span>
                <small>or drag and drop</small>
            </div>
            <div class="file-selected" style="display: none;">
                <i class="fas fa-file"></i>
                <span class="file-name">No file selected</span>
                <button type="button" class="btn-close clear-file"></button>
            </div>
        `;
        wrapper.appendChild(label);
        
        // Add drag and drop functionality
        label.addEventListener('dragover', e => {
            e.preventDefault();
            label.classList.add('dragover');
        });
        
        label.addEventListener('dragleave', () => {
            label.classList.remove('dragover');
        });
        
        label.addEventListener('drop', e => {
            e.preventDefault();
            label.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                input.files = e.dataTransfer.files;
                const event = new Event('change', { bubbles: true });
                input.dispatchEvent(event);
            }
        });
        
        // File selection handler
        input.addEventListener('change', function() {
            const placeholder = label.querySelector('.file-placeholder');
            const selected = label.querySelector('.file-selected');
            const fileName = label.querySelector('.file-name');
            const preview = document.querySelector(`#${this.id}-preview`);
            
            if (this.files && this.files[0]) {
                // Show selected UI
                placeholder.style.display = 'none';
                selected.style.display = 'flex';
                fileName.textContent = this.files[0].name;
                
                // Set icon based on file type
                const icon = selected.querySelector('i');
                const fileExt = this.files[0].name.split('.').pop().toLowerCase();
                
                if (['jpg', 'jpeg', 'png', 'gif'].includes(fileExt)) {
                    icon.className = 'fas fa-file-image';
                } else if (['pdf'].includes(fileExt)) {
                    icon.className = 'fas fa-file-pdf';
                } else if (['doc', 'docx'].includes(fileExt)) {
                    icon.className = 'fas fa-file-word';
                } else {
                    icon.className = 'fas fa-file';
                }
                
                // Preview image if applicable
                if (preview && ['jpg', 'jpeg', 'png', 'gif'].includes(fileExt)) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        if (preview.tagName === 'IMG') {
                            preview.src = e.target.result;
                            preview.style.display = 'block';
                            
                            // Add zoom effect
                            preview.addEventListener('click', () => {
                                const zoomModal = document.createElement('div');
                                zoomModal.className = 'image-zoom-modal';
                                zoomModal.innerHTML = `
                                    <div class="zoom-content">
                                        <img src="${e.target.result}" alt="Zoomed preview">
                                        <button class="zoom-close"><i class="fas fa-times"></i></button>
                                    </div>
                                `;
                                document.body.appendChild(zoomModal);
                                
                                zoomModal.addEventListener('click', () => {
                                    document.body.removeChild(zoomModal);
                                });
                            });
                        }
                    };
                    reader.readAsDataURL(this.files[0]);
                }
                
                // Show file info
                const fileInfoEl = document.querySelector(`#${this.id}-info`);
                if (fileInfoEl) {
                    const fileSize = (this.files[0].size / 1024).toFixed(2);
                    fileInfoEl.innerHTML = `
                        <span class="badge bg-light text-dark">
                            <i class="fas fa-info-circle me-1"></i> ${fileExt.toUpperCase()} · ${fileSize} KB
                        </span>
                    `;
                    fileInfoEl.style.display = 'block';
                }
            } else {
                // Reset to placeholder UI
                placeholder.style.display = 'flex';
                selected.style.display = 'none';
                
                // Clear preview
                if (preview) {
                    preview.src = '';
                    preview.style.display = 'none';
                }
                
                // Clear file info
                const fileInfoEl = document.querySelector(`#${this.id}-info`);
                if (fileInfoEl) {
                    fileInfoEl.style.display = 'none';
                }
            }
        });
        
        // Clear file button
        const clearBtn = label.querySelector('.clear-file');
        clearBtn.addEventListener('click', e => {
            e.stopPropagation();
            
            // Clear the input
            input.value = '';
            const event = new Event('change', { bubbles: true });
            input.dispatchEvent(event);
        });
    });
    
    // Setup form validation
    setupFormValidation();
    
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                window.scrollTo({
                    top: target.offsetTop - 70,
                    behavior: 'smooth'
                });
            }
        });
    });
});
