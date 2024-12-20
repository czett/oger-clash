function checkPW(){
    const pw1 = document.getElementById("pw1");
    const pw2 = document.getElementById("pw2");
    const btn = document.querySelector(".submit-btn");
    
    console.log("hola");
    if (pw1.value != pw2.value){
        console.log("hola");
        pw1.style.borderColor = "#d4040d";
        pw2.style.borderColor = "#d4040d";
        btn.disabled = true;
    }else{
        pw1.style.borderColor = "#beaf8d";
        pw2.style.borderColor = "#beaf8d";
        btn.disabled = false;
    }
}

function toggleShop(){
    const shop = document.querySelector(".shop");
    
    if (shop.dataset.visible == "true"){
        shop.dataset.visible = "false";
        shop.style.transform = "translateX(-100%)";
    }else{
        console.log("hewwo")
        shop.dataset.visible = "true";
        shop.style.transform = "translateX(0%)";
    }
}

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