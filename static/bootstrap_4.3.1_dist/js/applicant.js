const marksInput = document.getElementById('marks-input"');
const saveButton = document.getElementById('save-btn');
const updateButton = document.getElementById('update-btn');

marksInput.addEventListener('input', ($event) => {
    if ($event.target.value.length > 0 && $event.target.value.length <= 4) {
        // updateButton.removeAttribute('disabled');
        saveButton.removeAttribute('disabled');

    } else {
        //updateButton.setAttribute('disabled', 'true');
        saveButton.removeAttribute('disabled', 'true');

    }
});