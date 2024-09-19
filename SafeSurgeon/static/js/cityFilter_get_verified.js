
document.addEventListener('DOMContentLoaded', function() {
    console.log("Script loaded: [Ajax_get_verified].js");
    const countrySelect = document.querySelector('select[name="country"]');
    const citySelect = document.querySelector('select[name="city"]');
    const cityUrl = window.city.url;

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
