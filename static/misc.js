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