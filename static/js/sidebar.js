function toggleSidebar(){

let sidebar = document.getElementById("sidebar");

if(window.innerWidth <= 768){

sidebar.classList.toggle("open");

}else{

sidebar.classList.toggle("collapsed");

}

}


/* Click outside sidebar → close */

document.addEventListener("click", function(e){

let sidebar = document.getElementById("sidebar");
let menuBtn = document.querySelector(".mobile-menu-btn");

if(window.innerWidth <= 768){

if(
sidebar.classList.contains("open") &&
!sidebar.contains(e.target) &&
!menuBtn.contains(e.target)
){
sidebar.classList.remove("open");
}

}

});