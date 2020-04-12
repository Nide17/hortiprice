const passwordInput = document.getElementById('password-input');
const confirmPassword = document.getElementById('confirm-password');
const errorMsg = document.getElementById('error-message');

confirmPassword.addEventListener('blur', () => {
    if (passwordInput.value == confirmPassword.value) {
        passwordInput.style.border = 'thin solid green';
        confirmPassword.style.border = 'thin solid green';
        errorMsg.style.display = 'none';
    } else {
        passwordInput.style.border = 'thin solid red';
        confirmPassword.style.border = 'thin solid red';
        errorMsg.style.display = 'inline';
        errorMsg.textContent = 'Passwords must match!'
        signupButton.setAttribute('disabled', 'true');
    }
});

const signupButton = document.getElementById('signup-button')

passwordInput.addEventListener('input', ($event) => {
    if ($event.target.value.length >=4 && $event.target.value.length <=10) 
    {
        signupButton.removeAttribute('disabled');
    } else {
        signupButton.setAttribute('disabled', 'true');
    }
});