document.addEventListener("DOMContentLoaded", function () {

document.querySelectorAll(".task-row").forEach(row => {

row.addEventListener("click", function(e){

// action button ক্লিক করলে redirect হবে না
if(e.target.closest("a") || e.target.closest("button")){
return;
}

const url = this.dataset.url;

if(url){
window.location.href = url;
}

});

});

});