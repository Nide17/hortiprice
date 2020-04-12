//DOM ELEMENTS REFERENCES
const firstNameInput = document.getElementById('first-name');
const LastNameInput = document.getElementById('last-name');
const submitButton = document.getElementById('submit-button');
const sidebar = document.getElementById('sidebar');
const commentForm = document.getElementById('comment-form');


submitButton.addEventListener('click', ($event) => {
    //TO PREVENT SUBMIT TO REFRESH
    $event.preventDefault();
    sidebar.textContent = 'Hi there, this is' +' ' +firstNameInput.value + ' ' +LastNameInput.value;
    //RESET THE FORM AFTER SUBMIT
    commentForm.reset(); 
});
