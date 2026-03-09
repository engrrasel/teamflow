function toggleSidebar(){

let sidebar = document.getElementById("sidebar");
let overlay = document.getElementById("overlay");

if(window.innerWidth <= 768){

sidebar.classList.toggle("open");
overlay.classList.toggle("active");

}else{

sidebar.classList.toggle("collapsed");

}

}


/* Click outside sidebar → close */

document.addEventListener("click", function(e){

let sidebar = document.getElementById("sidebar");
let overlay = document.getElementById("overlay");
let menuBtn = document.querySelector(".mobile-menu-btn");

if(window.innerWidth <= 768){

if(
sidebar.classList.contains("open") &&
!sidebar.contains(e.target) &&
!menuBtn.contains(e.target)
){

sidebar.classList.remove("open");
overlay.classList.remove("active");

}

}

});