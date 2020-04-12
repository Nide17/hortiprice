/*MANAGER JS CODES*/

const articles = document.getElementsByTagName('article');
const paragraphs = document.getElementsByTagName('p');

const firstArticle = articles[0];
const secondParagraph = paragraphs[1];

const WhiteTextElements = document.getElementsByClassName('text-white');

const sidebar = document.getElementById('sidebar');

//Modify the DOM

const mainHeading = document.getElementById('main-heading'); 
mainHeading.textContent = 'Welcome Mr. Manager';
mainHeading.innerHTML = '<h1>Welcome Mr. Manager</h1>';

const header = document.getElementById('page-header');
header.classList.add('text-center');

sidebar.classList.remove('bg-info');
sidebar.classList.add('bg-primary');

header.style.padding = '1em';
header.classList.remove('bg-dark');
header.style.backgroundColor = '#854135';

//Create new article

let newArticle = document.createElement('article');
let newHeading = document.createElement('h3');
let newParagraph = document.createElement('p');

newHeading.textContent = 'Article 004-METHODOLOGY'
newParagraph.textContent = 'Fifty-eight (58) casual workers, who have the basic skills of Microsoft office and trained for receiving horticulture business ideas, carried out this activity.';

newArticle.appendChild(newHeading);
newArticle.appendChild(newParagraph);

newArticle.classList.add('m-2', 'p-2', 'border', 'border-secondary');

newArticle.setAttribute('id','art-004');

const main = document.querySelector('main');
main.appendChild(newArticle);


