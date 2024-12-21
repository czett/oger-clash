function toggleCart(){
    const cart = document.querySelector(".cart");
    const buy = document.querySelector(".buy");
    const sl = document.querySelector(".shop-list");
    const st = document.querySelector(".shop-title");
    const checkout = document.querySelector(".checkout");
    
    if (cart.dataset.visible == "false"){
        cart.dataset.visible = "true";
        cart.style.opacity = "1";
        buy.style.visibility = "visible";
        buy.style.opacity = "1";
        cart.style.visibility = "visible";
        sl.style.transform = "translateY(-150%)";
        checkout.style.inset = "auto auto 80% 50%";
        checkout.innerHTML = "Weiter Shoppen";
        st.innerHTML = "Warenkorb";

        fetch('/api/get_cart')
        .then(res => res.json())
        .then(list => {
            document.querySelector('.cart .products').innerHTML = list.map(offer => `
            <div class="product">
                <div class="name">${offer.name}</div>
                <div class="price">${offer.price} <span class="material-symbols-rounded">diamond</span></div>
            </div>
            `).join('');
        });
    }else{
        buy.style.opacity = "0";
        buy.style.visibility = "hidden";
        cart.style.opacity = "0";
        cart.style.visibility = "hidden";
        console.log("hewwo")
        cart.dataset.visible = "false";
        sl.style.transform = "translateY(0%)";
        checkout.style.inset = "auto auto 0% 50%";
        checkout.innerHTML = "Zur Kasse";
        st.innerHTML = "Shop";
    }
}

function toCart(product){
    const name = product.dataset.name;
    const price = product.dataset.price;

    //let list;
    //fetch('/api/to_cart/' + name + '/' + price + '').then(res => res.json()).then(data => list = data);

    fetch('/api/to_cart/' + name + '/' + price)
        .then(res => res.json())
        .then(list => {
            document.querySelector('.cart .products').innerHTML = list.map(offer => `
            <div class="product">
                <div class="name">${offer.name}</div>
                <div class="price">${offer.price} <span class="material-symbols-rounded">diamond</span></div>
            </div>
            `).join('');
    });
}

function clearCart(){
    fetch('/api/clear_cart')
        .then(res => res.json())
        .then(list => {
            document.querySelector('.cart .products').innerHTML = list.map(offer => `
            <div class="product">
                <div class="name">${offer.name}</div>
                <div class="price">${offer.price} <span class="material-symbols-rounded">diamond</span></div>
            </div>
            `).join('');
    });
}

function buyCart() {
    fetch('/api/buy_cart')
        .then(res => res.json())
        .then(list => {
            document.querySelector('.cart .products').innerHTML = list.map(offer => `
            <div class="product">
                <div class="name">${offer.name}</div>
                <div class="price">${offer.price} <span class="material-symbols-rounded">diamond</span></div>
            </div>
            `).join('');
        })
        .then(() => fetch('/api/get_diamonds'))
        .then(res => res.json())
        .then(diamonds => {
            document.querySelector('.diacount').textContent = diamonds;
        });
}