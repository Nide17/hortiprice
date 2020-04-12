/*EMPLOYEE JS CODES*/
//query selector bcz it's the first element

//get access to DOM elements
const header = document.querySelector('header');
const blueButton = document.getElementById('color-button-blue');
const brownButton = document.getElementById('color-button-brown');
const greenButton = document.getElementById('color-button-green');
const noneButton = document.getElementById('color-button-none');

const addPostButton = document.getElementById('add-post');
const removePostButton = document.getElementById('remove-post');
const articleSection = document.querySelector('section');

//Click event listeners
blueButton.addEventListener('click', () => {
    header.classList.remove('brown-background', 'green-background');
    header.classList.add('blue-background', 'text-white');
});

brownButton.addEventListener('click', () => {
    header.classList.remove('blue-background', 'green-background');
    header.classList.add('brown-background', 'text-white');
});

greenButton.addEventListener('click', () => {
    header.classList.remove('blue-background', 'brown-background');
    header.classList.add('green-background', 'text-white');
});

noneButton.addEventListener('click', () => {
    header.classList.remove('blue-background', 'brown-background', 'green-background', 'text-white');
});

addPostButton.addEventListener('click', () => {
    const newPost = createNewPost();
    articleSection.appendChild(newPost);
});

removePostButton.addEventListener('click', () => {
    const articleCount = articleSection.childElementCount;
    if (articleCount > 1) {
        articleSection.removeChild(articleSection.children[articleCount - 1]);
    }
})

//Page functions

function createNewPost() {
    let newArticle = document.createElement('article');
    let newHeading = document.createElement('h5');
    let newParagraph = document.createElement('p');

    newHeading.textContent = 'Another Post';
    newParagraph.textContent = 'In addition, RULINDO district has a higher number of applicants with 1342 applicants and MUSANZE with 1091 applicants while GISAGARA district has a low number with a total of 14 applicants and NYARUGENGE district has 29 applicants.';

    newArticle.appendChild(newHeading);
    newArticle.appendChild(newParagraph);

    newArticle.classList.add('list-group-item');

    return newArticle;
}
//APIs
//Access DOM elements
const reportSection = document.getElementById('weather-report');
const cityForm = document.getElementById('city-form');
const cityInput = document.getElementById('city');

//Prepare openweathermap.org request
let apiRequest = new XMLHttpRequest();

/*
 *capture and handle form submit ebent
 *prevent default behavior, prepare and send API request
 */
cityForm.addEventListener('submit', ($event) => {
    $event.preventDefault();
    const chosenCity = cityInput.value;
    apiRequest.open('GET', 'https://api.openweathermap.org/data/2.5/weather?q=' + chosenCity + '&APPID=b34fddd3dae4a2eb0ad363b62f98ba1e');
    apiRequest.send();
});

apiRequest.onreadystatechange = () => {
    if (apiRequest.readyState === 4) {

        if (apiRequest.status === 404) {
            reportSection.textContent = 'City not found!';
        }
        const response = JSON.parse(apiRequest.response);
        return reportSection.textContent = 'The weather in ' + response.name + ' is ' + response.weather[0].main + '.';
    }
}