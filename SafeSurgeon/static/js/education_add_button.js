
    document.addEventListener('DOMContentLoaded', function(){
    const addEducationButton = document.getElementById('add-education');
    const educationFormsContainer = document.getElementById('education-forms');
    const managementForm = document.getElementById('education-management-form');

    if  (addEducationButton && educationFormsContainer && managementForm) {
        addEducationButton.addEventListener('click', function() {
            const totalFormsInput = managementForm.querySelector('[name$=TOTAL_FORMS]');
            let formCount = parseInt(totalFormsInput.value);

            const lastForm = educationFormsContainer.children[educationFormsContainer.children.length - 1];
            const newForm = lastForm.cloneNode(true);

            newForm.innerHTML = newForm.innerHTML.replace(/education_set-\d+/g, `education_set-${formCount}`);
            newForm.innerHTML = newForm.innerHTML.replace(/-\d+-/g, `-${formCount}-`);

            newForm.querySelectorAll('input:not([type=hidden]), select, textarea').forEach(input => {
                input.value = '';
            });

            formCount++;
            totalFormsInput.value = formCount;

            educationFormsContainer.appendChild(newForm);
        });
    }
});
