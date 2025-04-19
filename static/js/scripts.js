// General purpose script file

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
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

    // Print functionality
    const printButtons = document.querySelectorAll('.btn-print');
    printButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    });

    // Confirm submission
    const confirmForm = document.querySelector('form.needs-confirmation');
    if (confirmForm) {
        confirmForm.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to submit your application? You will not be able to make changes after submission.')) {
                e.preventDefault();
            }
        });
    }

    // Application progress calculation
    const progressBars = document.querySelectorAll('.progress-bar[data-percentage]');
    progressBars.forEach(bar => {
        const percentage = bar.getAttribute('data-percentage');
        bar.style.width = percentage + '%';
        bar.setAttribute('aria-valuenow', percentage);
    });

    // Document file input preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const preview = document.querySelector(`#${this.id}-preview`);
            if (preview && this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    if (preview.tagName === 'IMG') {
                        preview.src = e.target.result;
                        preview.style.display = 'block';
                    }
                };
                reader.readAsDataURL(this.files[0]);
                
                // Show file name
                const fileNameDisplay = document.querySelector(`#${this.id}-name`);
                if (fileNameDisplay) {
                    fileNameDisplay.textContent = this.files[0].name;
                }
            }
        });
    });
});

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
    
    // Update progress percentage
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        progressBar.style.width = completionData.completion_percentage + '%';
        progressBar.setAttribute('aria-valuenow', completionData.completion_percentage);
        progressBar.textContent = Math.round(completionData.completion_percentage) + '%';
    }
}
