/* =========================
   MODAL CONTROL
========================= */

function getTaskModal(){
return document.getElementById("taskModal");
}

window.openTaskModal=function(){

const modal=getTaskModal();
if(modal) modal.style.display="flex";

};

window.closeTaskModal=function(){

const modal=getTaskModal();
if(modal) modal.style.display="none";

};


/* =========================
   OUTSIDE CLICK CLOSE
========================= */

window.addEventListener("click",function(e){

const modal=getTaskModal();

if(modal && e.target===modal){
modal.style.display="none";
}

});


/* =========================
   PAGE INIT
========================= */

document.addEventListener("DOMContentLoaded",function(){

/* EMPLOYEE SEARCH */

const empSearch=document.getElementById("empSearch");

if(empSearch){

empSearch.addEventListener("input",function(){

const filter=this.value.toLowerCase();
const items=document.querySelectorAll("#employeeList .employee-item");

items.forEach(function(item){

const name=item.textContent.toLowerCase();

item.style.display=name.includes(filter) ? "" : "none";

});

});

}


/* CUSTOMER SEARCH */

const customerSearch=document.getElementById("customerSearch");

if(customerSearch){

customerSearch.addEventListener("input",function(){

const filter=this.value.toLowerCase();
const options=document.querySelectorAll("#customerSelect option");

options.forEach(function(option){

const text=option.textContent.toLowerCase();

option.style.display=text.includes(filter) ? "" : "none";

});

});

}

});


/* =========================
   SELECT ALL EMPLOYEES
========================= */

window.selectAllEmployees=function(){

const items=document.querySelectorAll("#employeeList .employee-item");

items.forEach(function(item){

if(item.style.display!=="none"){

const cb=item.querySelector('input[type="checkbox"]');

if(cb) cb.checked=true;

}

});

};


let allSelected=false;

function toggleEmployees(){

const checks=document.querySelectorAll(".emp-check");

checks.forEach(function(c){

const item=c.closest(".employee-item");

if(item && item.style.display!=="none"){
c.checked=!allSelected;
}

});

allSelected=!allSelected;

const btn=document.getElementById("selectAllBtn");

if(btn){
btn.innerText=allSelected ? "Unselect All" : "Select All";
}

}