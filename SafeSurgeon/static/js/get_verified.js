document.addEventListener('DOMContentLoaded', function() {
    const citySelect = document.querySelector('select[name="city"]');
    const clinicSelects = document.querySelectorAll('select[name$="-clinic"]');
    const newClinicInputs = document.querySelectorAll('input[name$="-new_clinic_name"]');
    const clinicUrl = window.clinicUrl;

    function saveClinicSelections() {
        const selections = {};
        clinicSelects.forEach((select, index) => {
            selections[index] = {
                clinic: select.value,
                new_clinic: newClinicInputs[index].value
            };
        });
        localStorage.setItem('clinicSelections', JSON.stringify(selections));
    }

    function loadClinicSelections() {
        const savedSelections = JSON.parse(localStorage.getItem('clinicSelections') || '{}');
        clinicSelects.forEach((select, index) => {
            if (savedSelections[index]) {
                if (savedSelections[index].clinic && select.querySelector(`option[value="${savedSelections[index].clinic}"]`)) {
                    select.value = savedSelections[index].clinic;
                }
                if (savedSelections[index].new_clinic) {
                    newClinicInputs[index].value = savedSelections[index].new_clinic;
                }
            }
        });
    }

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

    // Load saved selections when the page loads
    loadClinicSelections();

    // Save selections when the form is submitted
    document.querySelector('form').addEventListener('submit', saveClinicSelections);
});

document.addEventListener('DOMContentLoaded', function() {
    const addButton = document.getElementById('add-education');
    if (addButton) {
        addButton.addEventListener('click', function() {
            // Wait a bit for the new form to be added to the DOM
            setTimeout(retrieveSecondFormData, 100);
        });
    }

    function retrieveSecondFormData() {
        const educationForms = document.querySelectorAll('[id^="education_set-"]');
        if (educationForms.length >= 2) {
            const secondForm = educationForms[1];
            const formData = new FormData(secondForm);
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            console.log('Second Education Form Data:', data);
        } else {
            console.log('Second education form not found');
        }
    }
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