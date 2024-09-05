document.getElementById('country').addEventListener('change', function(){ 
    const countryId=this.value;
    const citySelect=document.getEleementById('city');
    citySelect.innerHTML = '<option value="">Select City</option>';

    if(countryId){
        fetch('/api/cities/${countryId}/')
        .then(response=>response.json())
        .then(cities => {
            cities.forEach(city => {
                const option=document.createElement('option');
                option.value=city.id;
                option.textContent = city.name;
                citySelect.apoendChild(option);
            });
        });
    }
});

// add to get_verified

    document.addEventListener('DOMContentLoaded', function() {
        // Dynamic form fields for country, city, and clinic
        const countrySelect = document.getElementById('{{ form.country.id_for_label }}');
        const citySelect = document.getElementById('{{ form.city.id_for_label }}');
        const clinicSelect = document.getElementById('{{ form.clinic.id_for_label }}');

        countrySelect.addEventListener('change', function() {
            // AJAX call to get cities for selected country
            // Update citySelect options
        });

        citySelect.addEventListener('change', function() {
            // AJAX call to get clinics for selected city
            // Update clinicSelect options
        });

        // Add education form dynamically
        const addEducationBtn = document.getElementById('add-education');
        const educationForms = document.getElementById('education-forms');
        let formCount = parseInt(document.getElementById('id_education-TOTAL_FORMS').value);

        addEducationBtn.addEventListener('click', function() {
            const newForm = educationForms.children[0].cloneNode(true);
            formCount++;
            newForm.innerHTML = newForm.innerHTML.replace(/form-(\d+)/g, `form-${formCount}`);
            newForm.innerHTML = newForm.innerHTML.replace(/__prefix__/g, formCount);
            educationForms.appendChild(newForm);
            
            const totalForms = document.getElementById('id_education-TOTAL_FORMS');
            totalForms.value = formCount + 1;
        });
    });
