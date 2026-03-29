/* =========================
   GLOBAL STATE
========================= */

let selectedDates = [];


/* =========================
   PAGE INIT
========================= */

document.addEventListener("DOMContentLoaded", function () {

    initDateFilter();
    initTodayButton();
    initTaskSearch();
    initStatusTabs();
    initRowClick();

});


/* =========================
   DATE FILTER (Flatpickr)
========================= */

function initDateFilter(){

    const dateInput = document.getElementById("dateRange");

    if(!dateInput) return;

    flatpickr("#dateRange",{
        mode:"range",
        dateFormat:"Y-m-d",
        onChange:function(dates){
            selectedDates = dates;
        }
    });

}


/* =========================
   TODAY BUTTON
========================= */

function initTodayButton(){

    const todayBtn = document.getElementById("todayBtn");

    if(!todayBtn) return;

    todayBtn.addEventListener("click",function(e){

        e.preventDefault();

        let today = new Date();

        // set global state
        selectedDates = [today, today];

        // 🔥 flatpickr input update (important)
        const fp = document.querySelector("#dateRange")._flatpickr;
        if(fp){
            fp.setDate([today, today], true);
        }

        // 🔥 apply filter
        applyAllFilters();

    });

}

/* =========================
   SEARCH TASK
========================= */

function initTaskSearch(){

    const searchInput = document.getElementById("taskSearch");

    if(!searchInput) return;

    searchInput.addEventListener("keyup",function(){

        let value = this.value.toLowerCase();

        document.querySelectorAll("#taskTable tbody tr").forEach(function(row){

            row.style.display =
                row.textContent.toLowerCase().includes(value)
                ? ""
                : "none";

        });

    });

}


/* =========================
   STATUS FILTER
========================= */

function initStatusTabs(){

    const tabs = document.querySelectorAll(".tab");

    if(tabs.length === 0) return;

    tabs.forEach(tab=>{

        tab.addEventListener("click",()=>{

            tabs.forEach(t=>t.classList.remove("active"));
            tab.classList.add("active");

            applyAllFilters(); // 🔥 combined filter

        });

    });

}


/* =========================
   MAIN FILTER ENGINE
========================= */

function applyAllFilters(){

    const type = document.getElementById("filterType")?.value || "assign";
    const activeTab = document.querySelector(".tab.active")?.dataset.status || "all";
    const searchValue = document.getElementById("taskSearch")?.value.toLowerCase() || "";

    let start = selectedDates[0] || null;
    let end = selectedDates[1] || selectedDates[0] || null;

    document.querySelectorAll("#taskTable tbody tr").forEach(row => {

        const assignDate = row.dataset.assign ? new Date(row.dataset.assign) : null;
        const deadlineDate = row.dataset.deadline ? new Date(row.dataset.deadline) : null;

        let targetDate = type === "assign" ? assignDate : deadlineDate;

        // === CONDITIONS ===

        let matchDate = true;
        let matchStatus = true;
        let matchSearch = true;

        // DATE
        if(start && targetDate){
            matchDate = targetDate >= start && targetDate <= end;
        }

        // STATUS
        if(activeTab !== "all"){
            matchStatus = row.dataset.status === activeTab;
        }

        // SEARCH
        if(searchValue){
            matchSearch = row.textContent.toLowerCase().includes(searchValue);
        }

        // FINAL
        let show = matchDate && matchStatus && matchSearch;

        row.style.display = show ? "" : "none";

    });

}


/* =========================
   APPLY FILTER BUTTON
========================= */

window.applyFilter = function(){
    applyAllFilters();
};


/* =========================
   ROW CLICK (SAFE)
========================= */

function initRowClick(){

    const rows = document.querySelectorAll(".task-row");

    rows.forEach(function(row){

        row.addEventListener("click", function(e){

            if(e.target.closest("a") || e.target.closest("button")){
                e.stopPropagation();
                return;
            }

            const url = row.dataset.url;

            if(url){
                window.location.href = url;
            }

        });

    });

}


/* =========================
   REJECT MODAL
========================= */

function openRejectModal(id) {

    const modal = document.getElementById("rejectModal");
    const form = document.getElementById("rejectForm");
    const input = document.getElementById("rejectAssignmentId");

    if (!modal || !form || !input) return;

    input.value = id;
    form.action = `/tasks/${id}/reject/`;

    modal.style.display = "flex";
}

function closeRejectModal() {

    const modal = document.getElementById("rejectModal");

    if (modal) {
        modal.style.display = "none";
    }

}

window.addEventListener("click", function(e) {

    const modal = document.getElementById("rejectModal");

    if (e.target === modal) {
        closeRejectModal();
    }

});