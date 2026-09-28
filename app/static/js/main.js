document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('contact-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitBtn = document.getElementById('submit-btn');
        const feedback = document.getElementById('form-feedback');
        
        // Reset state
        submitBtn.disabled = true;
        submitBtn.textContent = 'Sending...';
        feedback.innerHTML = '';
        
        try {
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const result = await response.json();
            
            if (response.ok) {
                feedback.innerHTML = `<div class="alert alert-success">${result.message}</div>`;
                form.reset();
            } else {
                feedback.innerHTML = `<div class="alert alert-error">${result.message || 'Something went wrong.'}</div>`;
            }
        } catch (error) {
            feedback.innerHTML = `<div class="alert alert-error">Network error. Please try again.</div>`;
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Send Message';
        }
    });
});
