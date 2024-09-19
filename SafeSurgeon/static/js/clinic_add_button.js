
    document.addEventListener('DOMContentLoaded', function() {
        console.log("DOM loaded from inline script");
        const addClinicButton = document.getElementById('add-clinic');
        const clinicFormsContainer = document.getElementById('clinic-forms');
        const managementForm = document.querySelector('input[name$=TOTAL_FORMS]');
    
        console.log("Add Clinic button:", addClinicButton);
        console.log("Clinic Forms Container:", clinicFormsContainer);
        console.log("Management Form:", managementForm);
    
        if (addClinicButton && clinicFormsContainer && managementForm) {
            addClinicButton.addEventListener('click', function() {
                console.log("Add Clinic button clicked");
                alert("Add Clinic button clicked!");
    
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


/*

document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded from inline script");
    const addClinicButton = document.getElementById('add-clinic');
    const clinicFormsContainer = document.getElementById('clinic-forms');
    const managementForm = document.querySelector('input[name$=TOTAL_FORMS]');

    console.log("Add Clinic button:", addClinicButton);
    console.log("Clinic Forms Container:", clinicFormsContainer);
    console.log("Management Form:", managementForm);

    if (addClinicButton && clinicFormsContainer && managementForm) {
        addClinicButton.addEventListener('click', function() {
            console.log("Add Clinic button clicked");
            alert("Add Clinic button clicked!");

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
*/