function openRejectModal(id){

const modal = document.getElementById("rejectModal");
const form = document.getElementById("rejectForm");

form.action = "/tasks/"+id+"/reject/";

modal.style.display = "flex";

}

function openResubmitModal(id){

const modal = document.getElementById("resubmitModal");
const form = document.getElementById("resubmitForm");

form.action = "/tasks/"+id+"/resubmit/";

modal.style.display = "flex";

}

window.addEventListener("click",function(e){

const rejectModal = document.getElementById("rejectModal");
const resubmitModal = document.getElementById("resubmitModal");

if(e.target === rejectModal){
rejectModal.style.display="none";
}

if(e.target === resubmitModal){
resubmitModal.style.display="none";
}

});