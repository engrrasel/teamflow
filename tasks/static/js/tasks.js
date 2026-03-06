document.addEventListener("DOMContentLoaded",function(){

flatpickr("#dateRange",{
mode:"range",
dateFormat:"Y-m-d"
});

const tabs=document.querySelectorAll(".tab");
const rows=document.querySelectorAll("#taskTable tbody tr");

tabs.forEach(tab=>{
tab.addEventListener("click",()=>{

tabs.forEach(t=>t.classList.remove("active"));
tab.classList.add("active");

const status=tab.dataset.status;

rows.forEach(row=>{
if(status==="all" || row.dataset.status===status){
row.style.display="";
}else{
row.style.display="none";
}
});

});
});

document.getElementById("taskSearch").addEventListener("keyup",function(){

let value=this.value.toLowerCase();

rows.forEach(row=>{
row.textContent.toLowerCase().includes(value)
? row.style.display=""
: row.style.display="none";
});

});

});

function openTaskModal(){
document.getElementById("taskModal").style.display="flex";
}

function closeTaskModal(){
document.getElementById("taskModal").style.display="none";
}