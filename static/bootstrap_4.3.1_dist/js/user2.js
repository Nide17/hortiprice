const cropsResult = document.getElementById('crops-result');
const categoryResult = document.getElementById('category-result');
const kindResult = document.getElementById('kind-result');

/*
*FAIL TO WORK

const radioButtons = document.getElemementsByName('cat-name');
*/
const kindDropdown = document.getElementById('applicant-kind');
kindResult.textContent = kindDropdown.value;


/*
 *CHECKBOXES EVENT LISTENERS
 */

document.getElementById('garlic-checkbox').addEventListener('change', ($event) => {
    if ($event.target.checked) {
        cropsResult.children[0].classList.remove('text-secondary');
    } else {
        cropsResult.children[0].classList.add('text-secondary');
    }
});

document.getElementById('tamarillo-checkbox').addEventListener('change', ($event) => {
    if ($event.target.checked) {
        cropsResult.children[1].classList.remove('text-secondary');
    } else {
        cropsResult.children[1].classList.add('text-secondary');
    }
});

document.getElementById('chilli-checkbox').addEventListener('change', ($event) => {
    if ($event.target.checked) {
        cropsResult.children[2].classList.remove('text-secondary');
    } else {
        cropsResult.children[2].classList.add('text-secondary');
    }
});

/*
*RADIO LISTENERS

for (let i=0; i < radioButtons.length; i++) {
    radioButtons[i].addEventListener('change', ($event) => {
        categoryResult.textContent = $event.target.value;
    });
}


*DROP LISTENERS
*/

kindDropdown.addEventListener('change', ($event) => {
    kindResult.textContent = $event.target.value;
});