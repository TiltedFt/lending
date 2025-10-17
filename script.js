// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, observerOptions);

document.querySelectorAll('.scroll-fade').forEach(el => {
    observer.observe(el);
});

// Form submission handling
function handleFormSubmit(form, successMessageId) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = form.querySelector('input[type="email"]').value;
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        
        // Disable button and show loading state
        submitBtn.disabled = true;
        submitBtn.textContent = 'Joining...';
        
        try {
            // Google Forms integration - ReadSage Waitlist
            const formID = '1FAIpQLSezpM8q4yrMs4lwfFJWt4V8gJa5s27Pwzapsbsy78VDLWMC_g';
            const formURL = `https://docs.google.com/forms/d/e/${formID}/formResponse`;

            // Entry ID for "Email Address" field
            const formData = new FormData();
            formData.append('entry.1493514912', email);

            // Submit to Google Forms (no-cors mode - we won't get response but it works!)
            await fetch(formURL, {
                method: 'POST',
                mode: 'no-cors',
                body: formData
            });

            console.log('Email submitted to Google Forms:', email);
            
            // Hide form and show success message
            form.style.display = 'none';
            const successMessage = document.getElementById(successMessageId);
            successMessage.classList.add('show');
            
            // Optional: Send to Google Analytics or tracking
            if (typeof gtag !== 'undefined') {
                gtag('event', 'generate_lead', {
                    'event_category': 'engagement',
                    'event_label': 'waitlist_signup'
                });
            }
            
        } catch (error) {
            console.error('Error submitting form:', error);
            alert('Something went wrong. Please try again.');
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });
}

// Initialize forms
const heroForm = document.getElementById('hero-form');
const ctaForm = document.getElementById('cta-form');

if (heroForm) {
    handleFormSubmit(heroForm, 'success-message');
}

if (ctaForm) {
    handleFormSubmit(ctaForm, 'cta-success-message');
}

// Header scroll effect
let lastScroll = 0;
const header = document.querySelector('.header');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll <= 0) {
        header.style.boxShadow = 'none';
    } else {
        header.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
    }
    
    lastScroll = currentScroll;
});

// Email validation
document.querySelectorAll('input[type="email"]').forEach(input => {
    input.addEventListener('blur', function() {
        const email = this.value;
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (email && !emailRegex.test(email)) {
            this.style.borderColor = '#ef4444';
        } else {
            this.style.borderColor = '';
        }
    });
    
    input.addEventListener('input', function() {
        this.style.borderColor = '';
    });
});
