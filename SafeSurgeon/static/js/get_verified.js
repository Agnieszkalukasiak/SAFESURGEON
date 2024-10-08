/* jshint esversion: 6 */
    
// add another clinic button
document.addEventListener('DOMContentLoaded', function() {
    console.log("Script loaded: [clinic_add_button].js");
    const addClinicButton = document.getElementById('add-clinic');
    const clinicFormsContainer = document.getElementById('clinic-forms');
    const managementForm = document.querySelector('input[name$=TOTAL_FORMS]');
    
    console.log("Add Clinic button:", addClinicButton);
    console.log("Clinic Forms Container:", clinicFormsContainer);
    console.log("Management Form:", managementForm);
    
    if (addClinicButton && clinicFormsContainer && managementForm) {
        addClinicButton.addEventListener('click', function() {
            
    
            let formCount = parseInt(managementForm.value);
            console.log("Current form count:", formCount);
    
    
            if (clinicFormsContainer.children.length > 0) {
                const lastForm = clinicFormsContainer.children[clinicFormsContainer.children.length - 1];
                const newForm = lastForm.cloneNode(true);
                console.log("New form cloned");
    
                newForm.innerHTML = newForm.innerHTML.replace(/clinic_set-\d+/g, `clinic_set-${formCount}`);
                newForm.innerHTML = newForm.innerHTML.replace(/-\d+-/g, `-${formCount}-`);
                console.log("Form index updated");
    
                newForm.querySelectorAll('input:not([type=hidden]), select').forEach(input => {
                    input.value = '';
                });
                console.log("Input values cleared");
    
                formCount++;
                managementForm.value = formCount;
                console.log("Total forms updated to:", managementForm.value);
    
                clinicFormsContainer.appendChild(newForm);
                console.log("New form appended");
            } else {
                console.error("No existing clinic forms to clone");
            }
        });
    } else {
        console.error("Required elements not found");
        console.log("Add Clinic button:", addClinicButton);
        console.log("Clinic Forms Container:", clinicFormsContainer);
        console.log("Management Form:", managementForm);
    }
});

/*city select */
document.addEventListener('DOMContentLoaded', function() {
    const countrySelect = document.querySelector('select[name="country"]');
    const citySelect = document.querySelector('select[name="city"]');
    const cityUrl = window.cityUrl;

    countrySelect.addEventListener('change', function() {
        const countryId = this.value;
        if (countryId) {
            fetch(`${cityUrl}${countryId}`)
                .then(response => response.json())
                .then(data => {
                    citySelect.innerHTML = '<option value="">---------</option>';
                    data.cities.forEach(city => {
                        const option = new Option(city.name, city.id);
                        citySelect.add(option);
                    });
                });
        } else {
            citySelect.innerHTML = '<option value="">---------</option>';
        }
    });
});

/*clinic select */
document.addEventListener('DOMContentLoaded', function() {
    const citySelect = document.querySelector('select[name="city"]');
    const clinicSelects = document.querySelectorAll('select[name$="-clinic"]');
    const clinicUrl = window.clinicUrl;

    citySelect.addEventListener('change', function() {
        const cityId = this.value;
        if (cityId) {
            fetch(`${clinicUrl}${cityId}`)
                .then(response => response.json())
                .then(data => {
                    clinicSelects.forEach(clinicSelect => {
                        clinicSelect.innerHTML = '<option value="">---------</option>';
                        data.clinics.forEach(clinic => {
                            const option = new Option(clinic.name, clinic.id);
                            clinicSelect.add(option);
                        });
                    });
                });
        } else {
            clinicSelects.forEach(clinicSelect => {
                clinicSelect.innerHTML = '<option value="">---------</option>';
            });
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const addEducationButton = document.getElementById('add-education');
    const educationForms = document.getElementById('education-forms');
    const totalFormsInput = document.querySelector('#id_education-TOTAL_FORMS');
    
    if (addEducationButton) {
        addEducationButton.addEventListener('click', function() {
            const formCount = educationForms.children.length;
            const newForm = educationForms.children[0].cloneNode(true);
            
            newForm.innerHTML = newForm.innerHTML.replace(/-\d+-/g, `-${formCount}-`);
            newForm.querySelectorAll('input, select').forEach(input => {
                input.value = '';
                input.id = input.id.replace(/-\d+-/, `-${formCount}-`);
                input.name = input.name.replace(/-\d+-/, `-${formCount}-`);
            });
            
            educationForms.appendChild(newForm);
            totalFormsInput.value = formCount + 1;
        });
    }
});
