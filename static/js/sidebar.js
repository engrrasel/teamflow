const sidebar = document.getElementById("sidebar");
const overlay = document.getElementById("overlay");


/* restore sidebar state immediately */

(function(){

const state = localStorage.getItem("sidebar-state");

if(state === "collapsed"){
sidebar.classList.add("collapsed");
document.documentElement.classList.add("sidebar-collapsed");
}

})();


/* toggle sidebar */

function toggleSidebar(e){

if(e) e.stopPropagation();

if(window.innerWidth <= 768){

sidebar.classList.toggle("open");
overlay.classList.toggle("active");

}else{

sidebar.classList.toggle("collapsed");

/* save state */

if(sidebar.classList.contains("collapsed")){
localStorage.setItem("sidebar-state","collapsed");
document.documentElement.classList.add("sidebar-collapsed");
}else{
localStorage.setItem("sidebar-state","expanded");
document.documentElement.classList.remove("sidebar-collapsed");
}

}

}


/* mobile outside click */

document.addEventListener("click", function(e){

if(window.innerWidth <= 768){

if(
sidebar.classList.contains("open") &&
!sidebar.contains(e.target)
){

sidebar.classList.remove("open");
overlay.classList.remove("active");

}

}

});