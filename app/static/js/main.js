document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('contact-form');
    if (!form) return;

    // Optional: copy commands
    const copyBtns = document.querySelectorAll('.copy-btn');
    copyBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const text = btn.getAttribute('data-copy');
            if(text) navigator.clipboard.writeText(text);
        });
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitBtn = document.getElementById('submit-btn');
        const feedback = document.getElementById('form-feedback');
        
        // Reset state
        submitBtn.disabled = true;
        submitBtn.textContent = 'Executing...';
        
        while (feedback.firstChild) {
            feedback.removeChild(feedback.firstChild);
        }
        
        const showMessage = (msg, isError) => {
            const div = document.createElement('div');
            div.className = isError ? 'alert alert-error' : 'alert alert-success';
            div.textContent = msg;
            feedback.appendChild(div);
        };
        
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
                showMessage(result.message, false);
                form.reset();
            } else {
                showMessage(result.message || 'Something went wrong.', true);
            }
        } catch (error) {
            showMessage('Network error. Please try again.', true);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Invoke Capability';
        }
    });
});
