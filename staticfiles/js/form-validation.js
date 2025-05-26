// Form validation script

document.addEventListener('DOMContentLoaded', function() {
    // Fetch all forms that need validation
    const forms = document.querySelectorAll('.needs-validation');
    
    // Loop over them and prevent submission if invalid
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Additional validation for specific fields
    
    // Phone number validation
    const phoneInputs = document.querySelectorAll('input[name="phone"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function() {
            // Allow only numbers and some special characters
            this.value = this.value.replace(/[^\d+\-() ]/g, '');
            
            // Check if the phone number meets minimum length
            if (this.value.replace(/[^\d]/g, '').length < 10) {
                this.setCustomValidity('Phone number must be at least 10 digits');
            } else {
                this.setCustomValidity('');
            }
        });
    });
    
    // PIN code validation
    const pincodeInputs = document.querySelectorAll('input[name="pincode"]');
    pincodeInputs.forEach(input => {
        input.addEventListener('input', function() {
            // Allow only numbers
            this.value = this.value.replace(/[^\d]/g, '');
            
            // Check if the PIN code is valid (assuming 6 digits for India)
            if (this.value.length !== 6) {
                this.setCustomValidity('PIN code must be 6 digits');
            } else {
                this.setCustomValidity('');
            }
        });
    });
    
    // Date of birth validation
    const dobInputs = document.querySelectorAll('input[name="date_of_birth"]');
    dobInputs.forEach(input => {
        input.addEventListener('change', function() {
            const selectedDate = new Date(this.value);
            const today = new Date();
            
            // Check if date is in the future
            if (selectedDate > today) {
                this.setCustomValidity('Date of birth cannot be in the future');
            } 
            // Check if the applicant is at least 15 years old
            else {
                const age = today.getFullYear() - selectedDate.getFullYear();
                const monthDiff = today.getMonth() - selectedDate.getMonth();
                
                if (age < 15 || (age === 15 && monthDiff < 0)) {
                    this.setCustomValidity('Applicant must be at least 15 years old');
                } else {
                    this.setCustomValidity('');
                }
            }
        });
    });
    
    // Year of passing validation
    const yearInputs = document.querySelectorAll('input[name="year_of_passing"]');
    yearInputs.forEach(input => {
        input.addEventListener('input', function() {
            // Allow only numbers
            this.value = this.value.replace(/[^\d]/g, '');
            
            const year = parseInt(this.value);
            const currentYear = new Date().getFullYear();
            
            // Check if year is valid
            if (isNaN(year) || year < 1950 || year > currentYear) {
                this.setCustomValidity(`Year must be between 1950 and ${currentYear}`);
            } else {
                this.setCustomValidity('');
            }
        });
    });
    
    // Percentage/CGPA validation
    const percentageInputs = document.querySelectorAll('input[name="percentage_marks"]');
    percentageInputs.forEach(input => {
        input.addEventListener('input', function() {
            // Allow only numbers and a decimal point
            this.value = this.value.replace(/[^\d.]/g, '');
            
            const percentage = parseFloat(this.value);
            
            // Check if percentage is valid
            if (isNaN(percentage) || percentage < 0 || percentage > 100) {
                this.setCustomValidity('Percentage/CGPA must be between 0 and 100');
            } else {
                this.setCustomValidity('');
            }
        });
    });
    
    // File upload validation
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            
            if (file) {
                // Check file size (max 5MB)
                const maxSize = 5 * 1024 * 1024; // 5MB in bytes
                if (file.size > maxSize) {
                    this.setCustomValidity('File size should not exceed 5MB');
                    return;
                }
                
                // Check file type
                const fileType = file.type;
                const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
                
                // Add PDF for documents that allow it
                if (this.id === 'aadhar' || this.id === 'marksheet') {
                    validTypes.push('application/pdf');
                }
                
                if (!validTypes.includes(fileType)) {
                    this.setCustomValidity('Invalid file type. Please upload a JPG, PNG' + 
                                         (validTypes.includes('application/pdf') ? ' or PDF' : ''));
                    return;
                }
                
                this.setCustomValidity('');
            }
        });
    });
    
    // Password strength validation
    const passwordInputs = document.querySelectorAll('input[name="password"]');
    passwordInputs.forEach(input => {
        input.addEventListener('input', function() {
            const password = this.value;
            const minLength = 8;
            const hasUpperCase = /[A-Z]/.test(password);
            const hasLowerCase = /[a-z]/.test(password);
            const hasNumbers = /\d/.test(password);
            const hasNonAlphas = /\W/.test(password);
            
            if (password.length < minLength) {
                this.setCustomValidity('Password must be at least 8 characters long');
            } else if (!hasUpperCase || !hasLowerCase) {
                this.setCustomValidity('Password must contain both uppercase and lowercase letters');
            } else if (!hasNumbers) {
                this.setCustomValidity('Password must contain at least one number');
            } else if (!hasNonAlphas) {
                this.setCustomValidity('Password must contain at least one special character');
            } else {
                this.setCustomValidity('');
            }
            
            // Update strength meter if exists
            const strengthMeter = document.getElementById('password-strength-meter');
            if (strengthMeter) {
                let strength = 0;
                if (password.length >= minLength) strength++;
                if (hasUpperCase && hasLowerCase) strength++;
                if (hasNumbers) strength++;
                if (hasNonAlphas) strength++;
                
                // Update the strength meter
                strengthMeter.value = strength;
                
                // Update the strength text
                const strengthText = document.getElementById('password-strength-text');
                if (strengthText) {
                    const strengthLabels = ['Weak', 'Fair', 'Good', 'Strong'];
                    strengthText.textContent = strengthLabels[strength - 1] || '';
                    
                    // Update text color
                    strengthText.className = 'text-' + 
                        (strength === 1 ? 'danger' : 
                         strength === 2 ? 'warning' : 
                         strength === 3 ? 'info' : 'success');
                }
            }
        });
    });
    
    // Confirm password validation
    const confirmPasswordInputs = document.querySelectorAll('input[name="confirm_password"]');
    confirmPasswordInputs.forEach(input => {
        input.addEventListener('input', function() {
            const password = document.querySelector('input[name="password"]').value;
            
            if (this.value !== password) {
                this.setCustomValidity('Passwords do not match');
            } else {
                this.setCustomValidity('');
            }
        });
    });
});
