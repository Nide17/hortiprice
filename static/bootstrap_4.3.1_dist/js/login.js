const passswordInput = document.getElementById('password-input');
const submitButton = document.getElementById('submit-button');

passswordInput.addEventListener('input', ($event) => {
    if ($event.target.value.length >= 4 && $event.target.value.length <= 10) {
        submitButton.removeAttribute('disabled');
    } else {
        submitButton.setAttribute('disabled', 'true');
    }
});