/* =========================
   ADD TASK MODAL
========================= */

window.openTaskModal = function () {
    const modal = document.getElementById("taskModal");
    if(modal){
        modal.style.display = "flex";
    }
}

window.closeTaskModal = function () {
    const modal = document.getElementById("taskModal");
    if(modal){
        modal.style.display = "none";
    }
}


/* =========================
   OUTSIDE CLICK CLOSE
========================= */

window.addEventListener("click", function(e){

    const modal = document.getElementById("taskModal");

    if(modal && e.target === modal){
        modal.style.display = "none";
    }

});


/* =========================
   PAGE INIT
========================= */

document.addEventListener("DOMContentLoaded", function(){

/* EMPLOYEE SEARCH */

const empSearch = document.getElementById("empSearch");

if(empSearch){

empSearch.addEventListener("keyup", function(){

const filter = this.value.toLowerCase();
const items = document.querySelectorAll(".employee-item");

items.forEach(function(item){

const name = item.textContent.toLowerCase();

item.style.display = name.includes(filter) ? "" : "none";

});

});

}


/* CUSTOMER SEARCH */

const search = document.getElementById("customerSearch");

if(search){

search.addEventListener("keyup", function(){

const filter = this.value.toLowerCase();
const options = document.querySelectorAll("#customerSelect option");

options.forEach(function(option){

const text = option.textContent.toLowerCase();

option.style.display = text.includes(filter) ? "" : "none";

});

});

}

});


/* =========================
   SELECT ALL EMPLOYEES
========================= */

window.selectAllEmployees = function(){

const checkboxes = document.querySelectorAll(
'.employee-list input[type="checkbox"]'
);

checkboxes.forEach(function(cb){
cb.checked = true;
});

}