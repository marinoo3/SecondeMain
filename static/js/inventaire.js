// GLOBALS

const LOADING = document.querySelector('#loading');
const PRODUCT_LIST = document.querySelector('.inventaire-container .products');
const PRODUCT_DETAIL = document.querySelector('.wrapper .details');
const VENDRE_BUTTON = document.querySelector('.vendre-button .main-button');
const DISCOUNT_ENTRY = document.querySelector('#discountCode');
const PRODUCT_TYPE = document.querySelector('#product-type');
const SEARCH_FILTER = document.querySelector('#search-filter');
SOLD_POPUP = document.querySelector('#sold-popup');



// GLOBAL EVENTS

document.addEventListener('DOMContentLoaded', function () {

    // load products when page loaded
    loadProducts('inventory');

});



// PRODUCT TYPE EVENT

PRODUCT_TYPE.addEventListener('change', async function () {
    const ft = this.value;
    await loadProducts(ft);

    const query = SEARCH_FILTER.value;
    if (query != "") {
        searchProducts(query);
    }

});



// PRODUCT SEARCH EVENT

SEARCH_FILTER.addEventListener('change', function() {
    this.blur();
});

SEARCH_FILTER.addEventListener('focusout', async function() {

    if (this.value != "") {
        searchProducts(this.value);
    }
    else {
        const ft = PRODUCT_TYPE.value;
        loadProducts(ft);
    }
});

async function searchProducts(query) {

    clearProducts();

    const response = await fetch('/search_products/' + query, {
        method: 'GET',
        headers: {'Content-Type': 'application/json'}
    });

    if(!response.ok) {
        throw new Error('Network response was not ok');
    }

    const result = await response.json();
    LOADING.classList.remove('is-loading');

    let selected = true;
    for(p of result.products) {
        displayProduct(p, selected);
        selected = false
    }
}

// LOAD PRODUCTS

function clearProducts() {

    LOADING.classList.add('is-loading');
    const no_result = document.querySelector('#no-result');
    no_result.style.display = 'none'

    let products = PRODUCT_LIST.querySelectorAll('li');
    for (p of products) {
        p.remove();
    }
}

async function loadProducts(ft) {

    clearProducts();

    const response = await fetch('/load_products/' + ft, {
        method: 'GET',
        headers: {'Content-Type': 'application/json'}
    });

    if(!response.ok) {
        throw new Error('Network response was not ok');
    }

    const result = await response.json();
    LOADING.classList.remove('is-loading');

    let selected = true;
    for(p of result.products.toReversed()) {
        displayProduct(p, selected);
        selected = false
    }
}

function displayProduct(p, selected) {

    let li = document.createElement('li');
    li.onclick = function() {
        selected_li = PRODUCT_LIST.querySelector('li.selected');
        selected_li.classList.remove('selected');
        this.classList.add('selected');
        previewProduct(p.id)
    };
    li.id = p.id;

    // main
    let main = document.createElement('div');
    main.classList.add('main');
    li.appendChild(main);
    let img = document.createElement('img');
    img.classList.add('product-icon');
    img.src = p.img_src;
    main.appendChild(img);
    let info = document.createElement('div');
    info.classList.add('info');
    main.appendChild(info);
    let title_p = document.createElement('p');
    title_p.classList.add('title');
    title_p.textContent = p.title;
    info.appendChild(title_p);
    let size_p = document.createElement('p');
    size_p.classList.add('size');
    size_p.textContent = p.size;
    info.appendChild(size_p);

    // seller
    let seller_p = document.createElement('p');
    seller_p.classList.add('seller');
    seller_p.textContent = '#' + p.id;
    li.appendChild(seller_p);

    // selected
    if (selected) {
        li.classList.add('selected');
        previewProduct(p.id);
    }

    PRODUCT_LIST.appendChild(li);
}



// PREVIEW PRODUCT

async function loadGiftCardInfo(id, code_input) {

    code_input.style.display = 'block';
    code_input.value = ''
    let balance_p = PRODUCT_DETAIL.querySelector('#balance');
    balance_p.textContent = '';

    if(id == "") {
        // if no gift card or discount code
        code_input.value = 'N/A';
        return
    }

    const response = await fetch('/get_giftcard_info/' + id, {
        method: 'GET',
        headers: {'Content-Type': 'application/json'}
    });

    if(!response.ok) {
        throw new Error('Network response was not ok');
    }

    const result = await response.json();
    const giftcard = result.giftcard;

    code_input.value = giftcard.code;

    balance_p = PRODUCT_DETAIL.querySelector('#balance');
    balance_p.textContent = giftcard.balance + '€';
}

async function previewProduct(id) {

    const response = await fetch('/preview_product/' + id, {
        method: 'GET',
        headers: {'Content-Type': 'application/json'}
    });

    if(!response.ok) {
        throw new Error('Network response was not ok');
    }

    const result = await response.json();
    const p = result.product;

    let preview = PRODUCT_DETAIL.querySelector('.product-preview');
    let img = preview.querySelector('.main img');
    img.src = p.img_src;
    let title_p = preview.querySelector('.title');
    title_p.textContent = p.title;
    let size_p = preview.querySelector('.size');
    size_p.textContent = p.size;
    let price = preview.querySelector('.price');
    let old_p = price.querySelector('.old');
    old_p.textContent = p.originalPrice + "€";
    let new_p = price.querySelector('.new');
    new_p.textContent = p.secondhandPrice + "€";

    let name_input = PRODUCT_DETAIL.querySelector('#name');
    name_input.value = p.sellerName;
    let lastname_input = PRODUCT_DETAIL.querySelector('#lastname');
    lastname_input.value = p.sellerLastName;
    let email_input = PRODUCT_DETAIL.querySelector('#email');
    email_input.value = p.sellerEmail;
    let phone_input = PRODUCT_DETAIL.querySelector('#phone');
    phone_input.value = p.sellerPhone;

    let code_input = PRODUCT_DETAIL.querySelector('#discountCode');
    code_input.parentElement.style.display = 'none';
    VENDRE_BUTTON.classList.remove('disabled');
    let code_section = PRODUCT_DETAIL.querySelector('.code-section');
    code_section.style.display = 'none';

    if(p.location == 'history') {
        VENDRE_BUTTON.classList.add('disabled');
        let code_section = PRODUCT_DETAIL.querySelector('.code-section');
        code_section.style.display = 'block';
        code_input.parentElement.style.display = 'flex';
        code_input.value = '';
        loadGiftCardInfo(p.discountID, code_input)
    }
}


// SELL PRODUCT

VENDRE_BUTTON.addEventListener('click', async function() {

    if(this.classList.contains('disabled')) {
        return;
    }

    this.classList.add('disabled');
    
    let selected_li = PRODUCT_LIST.querySelector('li.selected');
    let id = selected_li.id;

    const response = await fetch('/sell_product/' + id, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    });

    if(!response.ok) {
        throw new Error('Network response was not ok');
    }

    const result = await response.json();
    if(result.status == 'success') {
        popup_p = SOLD_POPUP.querySelector('p');
        popup_p.textContent = result.data['seller'] + ' à été notifié et un coupon lui a été envoyé'
        SOLD_POPUP.classList.add('active');
    }
});

SOLD_POPUP.querySelector('button').addEventListener('click', function() {
    location.reload();
});