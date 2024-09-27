document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-clinic');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const clinicId = this.getAttribute('data-clinic-id');
            if (confirm('Are you sure you want to delete this clinic?')) {
                fetch(`/delete-clinic/${clinicId}/`, { 
                    method: 'POST',
                    headers:{
                        'X-CSRFToken': csrftoken,  
                        'Content-Type': 'application/json'
                    } 
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            this.closest('.clinic-form').remove();
                        } else {
                            alert('Failed to delete clinic. Please try again.');
                        }
                    });
                }
            });
        });
    });

// for edit_surgon_profile, add another clinic or education.
document.addEventListener('DOMContentLoaded', function() {
    function addFormset(button, formsetPrefix) {
        const formset = document.getElementById(formsetPrefix + '-TOTAL_FORMS');
        const formCount = parseInt(formset.value);
        const newForm = document.querySelector('.' + formsetPrefix.toLowerCase() + '-form').cloneNode(true);
        
        newForm.innerHTML = newForm.innerHTML.replace(new RegExp(formsetPrefix + '-\\d+', 'g'), formsetPrefix + '-' + formCount);
        newForm.innerHTML = newForm.innerHTML.replace(/__prefix__/g, formCount);
        
        // Clear the values of the new form
        newForm.querySelectorAll('input:not([type=hidden]), select, textarea').forEach(input => {
            input.value = '';
        });
        
        document.querySelector('.' + formsetPrefix.toLowerCase() + '-form:last-of-type').after(newForm);
        
        formset.value = formCount + 1;
    }

        document.getElementById('add-clinic').addEventListener('click', function() {
            addFormset(this, 'clinic_formset');
    });

    document.getElementById('add-education').addEventListener('click', function() {
        addFormset(this, 'education_formset');
    });
}); 
