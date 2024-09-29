/* jshint esversion: 6 */

document.addEventListener('DOMContentLoaded', function () {
    const countrySelect = document.getElementById('country_select');
    const citySelect = document.getElementById('city_select');

    // Store all city options
    const allCityOptions = Array.from(citySelect.options);

    countrySelect.addEventListener('change', function () {
        const selectedCountryId = this.value;

        // Clear current city options
        citySelect.innerHTML = '<option value="">Select a city</option>';

        if (selectedCountryId) {
            // Filter and add city options for the selected country
            allCityOptions.forEach(option => {
                if (option.dataset.countryId === selectedCountryId) {
                    citySelect.appendChild(option.cloneNode(true));
                }
            });
        }
    });
});