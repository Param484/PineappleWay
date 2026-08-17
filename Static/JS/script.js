// =========================
// PineappleWay JavaScript
// =========================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {

    anchor.addEventListener("click", function(e){

        e.preventDefault();

        document.querySelector(this.getAttribute("href"))
        .scrollIntoView({
            behavior:"smooth"
        });

    });

});

// Navbar Shadow on Scroll
window.addEventListener("scroll",function(){

    let navbar=document.querySelector(".navbar");

    if(window.scrollY>50){
        navbar.classList.add("shadow");
    }
    else{
        navbar.classList.remove("shadow");
    }

});

// Welcome Message
console.log("✈️ Welcome to PineappleWay");