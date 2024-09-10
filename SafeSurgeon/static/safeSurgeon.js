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
//thank you message for surgon profile
document.getElementById('surgeonForm').addEventListener('submit', function(e) {
    e.preventDefault();
    fetch(this.action, {
        method: 'POST',
        body: new FormData(this),
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('surgeonForm').style.display = 'none';
            document.getElementById('thankYouMessage').style.display = 'block';
        } else {
            alert('There was an error submitting the form. Please try again.');
        }
    });
});

// setting for cities to drop down in countries
$(document).ready(function() {
    $("#id_country").change(function () {
        var countryId = $(this).val(); //Get teh selected country ID
        if(countryId) {
            $.ajax({
                url: '/get-cities/' + countryId + '/',
                type:'GET',
                success: function (data) {
                    $("#id_city").html('');//clear the city dropown
                    $.each(data, function(key,value){
                        $("#id_city").append('<option value="' + value.id + '">'+value.name + '</option>');   
                    });
                },
                error:function(){
                    console.log("Error loading cities.");
                }
             });
        } else {
            $("#id_city").html(''); //clear city drop down if no country selected
        }
    });
});


//surgeon_profile and edit
document.addEventListener('DOMContentLoaded', function() {
    const addEducationBtn = document.getElementById('add-education');
    const educationFormset = document.getElementById('id_education_set-TOTAL_FORMS');
    
    addEducationBtn.addEventListener('click', function() {
        const formCount = parseInt(educationFormset.value);
        const newForm = document.querySelector('.education-form').cloneNode(true);
        
        // Update form index
        newForm.innerHTML = newForm.innerHTML.replace(/-\d+-/g, `-${formCount}-`);
        
        // Clear input values
        newForm.querySelectorAll('input, select').forEach(input => {
            input.value = '';
        });
        
        document.querySelector('.education-form').parentNode.insertBefore(newForm, addEducationBtn);
        educationFormset.value = formCount + 1;
    });
});

document.getElementById('add-education').addEventListener('click', function() {
    var formCount = parseInt(document.getElementById('id_education-TOTAL_FORMS').value);
    var newForm = document.querySelector('.education-form').cloneNode(true);
    var regex = new RegExp('education-\\d+', 'g');
    newForm.innerHTML = newForm.innerHTML.replace(regex, 'education-' + formCount);
    document.querySelector('.education-form').parentNode.insertBefore(newForm, this);
    document.getElementById('id_education-TOTAL_FORMS').value = formCount + 1;
});
// for the verify page
$(document).ready(function() {
    $('#country-select').change(function() {
        var countryId = $(this).val();
        if (countryId) {
            $.ajax({
                url: '/get-cities/' + countryId + '/',
                type: 'GET',
                success: function(data) {
                    $('#city-select').empty();
                    $('#city-select').append('<option value="">Select a city</option>');
                    $.each(data, function(key, value) {
                        $('#city-select').append('<option value="' + value.id + '">' + value.name + '</option>');
                    });
                    $('#city-select').prop('disabled', false);
                }
            });
        } else {
            $('#city-select').empty();
            $('#city-select').append('<option value="">Select a city</option>');
            $('#city-select').prop('disabled', true);
        }
    });
});