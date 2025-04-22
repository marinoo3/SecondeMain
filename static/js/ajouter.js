// GLOBALS

const FORM = document.forms["add-form"];
const POPUP = document.querySelector('#added-popup');



// UTILS

function markAsRequire(element) {

    let parent = element.parentElement;
    let required_info = document.createElement('p');

    required_info.classList.add('required-info');
    required_info.textContent = '*';

    parent.appendChild(required_info);
}

function unmarkAsRequire(element) {

    let parent = element.parentElement;
    let required_info = parent.querySelector('.required-info');

    if (required_info) {
        required_info.remove();
    }
}



// GLOBAL EVENTS

document.addEventListener('DOMContentLoaded', function() {

    // unmark as required when filled (input)

    for(input of FORM.querySelectorAll('input')) {

        input.addEventListener('change', function() {
            if (this.value) {
                unmarkAsRequire(this);
            }
        });
    }

    // unmark as required when filled (select)

    for(select of FORM.querySelectorAll('select')) {

        select.addEventListener('change', function() {
            if (this.value) {
                this.classList.remove('default-select');
                unmarkAsRequire(this);
            } else {
                this.classList.add('default-select');
            }
        });
    }
});



// SEARCH EMAIL EVENT

FORM['email'].addEventListener('change', async function() {

    if(this.value == '') {
        return
    }

    let status = 'Utilisateur sera créé en ajoutant le produit';
    let icon = 'imgs/user-add.svg';
    let color = 'var(--warning)';

    const response = await fetch('/search_customer/' + this.value, {
        method: 'GET',
        headers: {'Content-Type': 'application/json'}
    });

    if(!response.ok) {
        throw new Error('Network response was not ok');
    }

    const result = await response.json();
    if(result.exists) {
        status = 'Utilisateur trouvé dans la base de donnée';
        icon = 'imgs/user-check.svg';
        color = 'var(--good)';
    }

    let contact_status = document.querySelector('.contact-status');
    let status_p = contact_status.querySelector('p');
    status_p.textContent = status;
    status_p.style.color = color;
    let icon_img = contact_status.querySelector('img');
    icon_img.src = icon;
});



// OWN BY MATCHY EVENT

FORM['checkbox'].addEventListener('change', async function() {
    if (this.checked == true) {
        FORM['name'].setAttribute("readonly", "");
        FORM['name'].setAttribute("value", "Matchy");
        FORM['lastname'].setAttribute("readonly", "");
        FORM['lastname'].setAttribute("value", "Cycling");
        FORM['email'].setAttribute("readonly", "");
        FORM['email'].setAttribute("value", "hello@matchycycling.com");
        FORM['phone'].setAttribute("readonly", "");
        FORM['phone'].setAttribute("value", "");
    } else {
        FORM['name'].removeAttribute("readonly");
        FORM['name'].setAttribute("value", "");
        FORM['lastname'].removeAttribute("readonly");
        FORM['lastname'].setAttribute("value", "");
        FORM['email'].removeAttribute("readonly");
        FORM['email'].setAttribute("value", "");
        FORM['phone'].removeAttribute("readonly");
        FORM['phone'].setAttribute("value", "");
    }
});



// SLIDER EVENT

FORM['etat'].addEventListener('input', function() {

    // slider function

    const sliderValue = (this.value - 1) * 33;

    this.style.background = `linear-gradient(to right, #4644e9 ${sliderValue}%, #393939 ${sliderValue}%)`;

    labels = document.querySelectorAll('.etat-wrapper .slider-labels > div');
    for (l of labels) {
        l.classList.remove('selected');
    }

    labels[this.value - 1].classList.add('selected');
});



// SUBMIT EVENT

FORM.addEventListener('submit', async function(e) {

    e.preventDefault();

    // check for requiered field and skip if missing

    let missing = false;

    for(element of FORM.querySelectorAll('input, select')) { 
        if(['phone'].includes(element.name)) {
            // skip non requiered fields
            continue;
        }  
        else if(element.value == '') {
            missing = true;
            markAsRequire(element);
        }
    }

    if (missing == true) {
        return
    }

    const ajouter_button = FORM['submit-button'];
    ajouter_button.classList.add('disabled');

    // collect the data and requests the python API

    const formData = new FormData(FORM);
    const data = Object.fromEntries(formData.entries());

    const response = await fetch('/ajouter', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    }); 

    if(!response.ok) {
        throw new Error('Network response was not ok');
    }

    // show success popup

    const result = await response.json();
    if(result.status == 200) {

        popup_t = POPUP.querySelector('h2');
        popup_t.textContent = '#' + result.data['id'];
        popup_p = POPUP.querySelector('p');
        popup_p.textContent = result.data['product_title'] + " à été ajouté a l'inventaire de seconde main."
        POPUP.classList.add('active');
        popup_b = POPUP.querySelector('button');
        popup_b.focus();
    }
})


// POPUP EVENT

POPUP.addEventListener('click', function() {
    location.reload();
});