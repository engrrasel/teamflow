/* =========================
   GLOBAL DATE STORAGE
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

});


/* =========================
   DATE FILTER
========================= */

function initDateFilter(){

    const dateInput = document.getElementById("dateRange");

    if(!dateInput) return;

    const params = new URLSearchParams(window.location.search);

    let start = params.get("start");
    let end = params.get("end");

    let defaultDates = [];

    if(start) defaultDates.push(start);
    if(end) defaultDates.push(end);

    flatpickr("#dateRange",{
        mode:"range",
        dateFormat:"Y-m-d",
        defaultDate:defaultDates,
        onChange:function(dates){
            selectedDates = dates;
        }
    });

    if(defaultDates.length > 0){
        selectedDates = defaultDates.map(d => new Date(d));
    }

}


/* =========================
   TODAY BUTTON
========================= */

function initTodayButton(){

    const todayBtn = document.getElementById("todayBtn");

    if(!todayBtn) return;

    todayBtn.addEventListener("click",function(e){

        e.preventDefault();

        let d = new Date();

        let today =
            d.getFullYear()+"-"+
            String(d.getMonth()+1).padStart(2,"0")+"-"+
            String(d.getDate()).padStart(2,"0");

        window.location.href = "?start="+today+"&end="+today;

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
   STATUS TABS FILTER
========================= */

function initStatusTabs(){

    const tabs = document.querySelectorAll(".tab");

    if(tabs.length === 0) return;

    const rows = document.querySelectorAll("#taskTable tbody tr");

    tabs.forEach(tab=>{

        tab.addEventListener("click",()=>{

            tabs.forEach(t=>t.classList.remove("active"));
            tab.classList.add("active");

            const status = tab.dataset.status;

            rows.forEach(row=>{

                row.style.display =
                    status === "all" || row.dataset.status === status
                    ? ""
                    : "none";

            });

        });

    });

}


/* =========================
   DATE FORMAT
========================= */

function formatDate(date){

    let year = date.getFullYear();
    let month = String(date.getMonth()+1).padStart(2,"0");
    let day = String(date.getDate()).padStart(2,"0");

    return year+"-"+month+"-"+day;

}


/* =========================
   APPLY FILTER
========================= */

window.applyFilter = function(){

    if(selectedDates.length === 0) return;

    let start = formatDate(selectedDates[0]);
    let end = start;

    if(selectedDates.length === 2){
        end = formatDate(selectedDates[1]);
    }

    window.location.href = "?start="+start+"&end="+end;

};