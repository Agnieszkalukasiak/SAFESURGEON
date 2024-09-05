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
{% endblack %}