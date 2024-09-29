/* jshint esversion: 6 */

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


document.addEventListener('DOMContentLoaded', function() {
    const addEducationButton = document.getElementById('add-education');
    const educationForms = document.getElementById('education-formset');
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

document.addEventListener('DOMContentLoaded', function() {
    const countrySelect = document.getElementById('id_country');
    const citySelect = document.getElementById('id_city');
    const clinicSelects = document.querySelectorAll('select[id$="-clinic"]');

    function updateCities() {
        const selectedCountry = countrySelect.value;
        console.log('Selected country:', selectedCountry);  // Debugging
        
        // AJAX to fetch cities for the selected country
        fetch(`/get_cities/${selectedCountry}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Network response was not ok: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Received data:', data);  // Debugging
                
                // Clear existing options
                citySelect.innerHTML = '<option value="">---------</option>';

                const cities = Array.isArray(data) ? data : data.cities;
                
                if (!cities || cities.length === 0) {
                    console.log('No cities received');
                    return;
                }

                cities.forEach(city => {
                    if (city && city.id && city.name) {
                        const option = document.createElement('option');
                        option.value = city.id;
                        option.textContent = city.name;
                        citySelect.appendChild(option);
                    }
                });

                console.log('City select updated'); 

                updateClinics();
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }
        
    function updateClinics(){
        const selectedCity = citySelect.options[citySelect.selectedIndex].text;
        
        clinicSelects.forEach(select => {
            Array.from(select.options).forEach(option => {
                if (option.value === '' || option.text.includes(selectedCity)) {
                    option.style.display = '';
                } else {
                    option.style.display = 'none';
                }
            });
        });
    }

    if (countrySelect && citySelect) {
        countrySelect.addEventListener('change', updateCities);
        citySelect.addEventListener('change', updateClinics);
    
        // Initial update
        if (countrySelect.value) {
            updateCities();
        }
    }
});
