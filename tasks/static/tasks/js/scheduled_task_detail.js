document.addEventListener("DOMContentLoaded", function(){

const tabs = document.querySelectorAll(".tab-btn");

tabs.forEach(btn => {

btn.addEventListener("click", function(){

const tab = this.dataset.tab;

document.querySelectorAll(".tab-btn").forEach(b=>{
b.classList.remove("active")
})

document.querySelectorAll(".tab-content").forEach(c=>{
c.classList.remove("active")
})

this.classList.add("active")

document.getElementById(tab).classList.add("active")

})

})

})