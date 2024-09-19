document.addEventListener('DOMContentLoaded', function() {
    console.log("Script loaded: [clinic_form].js");
    const addClinicButton = document.getElementById('add-clinic');
    const clinicFormsDiv = document.getElementById('clinic-forms');
    let totalForms = document.getElementById('id_clinic_set-TOTAL_FORMS');

    addClinicButton.addEventListener('click', function() {
        const currentFormCount = parseInt(totalForms.value);
        const newForm = clinicFormsDiv.firstElementChild.cloneNode(true);

        // Update form attributes (like IDs and names) so they are unique
        const formRegex = new RegExp(`clinic_set-(\\d+)-`, 'g');
        newForm.innerHTML = newForm.innerHTML.replace(formRegex, `clinic_set-${currentFormCount}-`);

        // Clear the input fields
        const inputs = newForm.querySelectorAll('input, textarea');
        inputs.forEach(input => input.value = '');

        // Append the new form to the formset
        clinicFormsDiv.appendChild(newForm);

        // Update the total number of forms
        totalForms.value = currentFormCount + 1;
    });
});
