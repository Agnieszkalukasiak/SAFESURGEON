console.log("This script is running");
document.addEventListener('DOMContentLoaded', function(){
    console.log("Script loaded: education_add_button.js");
    const addEducationButton = document.getElementById('add-education');
    const educationFormsContainer = document.getElementById('education-managment-form');
    const managementForm = document.querySelector('input[name$=TOTAL_FORMS]');

    if (addEducationButton && educationFormsContainer && managementForm) {
        addEducationButton.addEventListener('click', function() {
            let formCount = parseInt(managementForm.value);
           
            if (educationFormsContainer.children.length > 0){
                const lastForm = educationFormsContainer.children[educationFormsContainer.children.length - 1];
                const newForm = lastForm.cloneNode(true);

                newForm.innerHTML = newForm.innerHTML.replace(/education_set-\d+/g, `education_set-${formCount}`);
                newForm.innerHTML = newForm.innerHTML.replace(/-\d+-/g, `-${formCount}-`);

                newForm.querySelectorAll('input:not([type=hidden]), select, textarea').forEach(input => {
                    input.value = '';
                });

                formCount++;
                managementForm.value = formCount;

                educationFormsContainer.appendChild(newForm);
                console.log("New education form added");
            } else {
                console.error("No existing education forms to clone");
            }
        });
    } else {
        console.error("Required elements not found for education form");
        console.log("Add Education button:", addEducationButton);
        console.log("Education Forms Container:", educationFormsContainer);
        console.log("Management Form:", managementForm);
    }
});