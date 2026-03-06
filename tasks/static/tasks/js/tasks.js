// Date filter
let selectedDates = [];

document.addEventListener("DOMContentLoaded", function () {

    const dateInput = document.getElementById("dateRange");

    if (dateInput) {

        // URL parameters read
        const params = new URLSearchParams(window.location.search);

        let start = params.get("start");
        let end = params.get("end");

        let defaultDates = [];

        if (start) defaultDates.push(start);
        if (end) defaultDates.push(end);

        flatpickr("#dateRange", {
            mode: "range",
            dateFormat: "Y-m-d",
            defaultDate: defaultDates,
            onChange: function (dates) {
                selectedDates = dates;
            }
        });

        // page reload হলেও selectedDates maintain
        if (defaultDates.length > 0) {
            selectedDates = defaultDates.map(d => new Date(d));
        }

    }

    // Today button
    const todayBtn = document.getElementById("todayBtn");

    if (todayBtn) {

        todayBtn.addEventListener("click", function (e) {

            e.preventDefault();

            let d = new Date();

            let today =
                d.getFullYear() + "-" +
                String(d.getMonth() + 1).padStart(2, "0") + "-" +
                String(d.getDate()).padStart(2, "0");

            window.location.href = "?start=" + today + "&end=" + today;

        });

    }

});


// Date format (Local time)
function formatDate(date) {

    let year = date.getFullYear();
    let month = String(date.getMonth() + 1).padStart(2, "0");
    let day = String(date.getDate()).padStart(2, "0");

    return year + "-" + month + "-" + day;

}


// Filter
function applyFilter() {

    if (selectedDates.length === 0) return;

    let start = formatDate(selectedDates[0]);
    let end = start;

    if (selectedDates.length === 2) {
        end = formatDate(selectedDates[1]);
    }

    window.location.href = "?start=" + start + "&end=" + end;

}


// Task modal
function openTaskModal() {
    document.getElementById("taskModal").style.display = "flex";
}

function closeTaskModal() {
    document.getElementById("taskModal").style.display = "none";
}


// Reject modal
function openRejectModal(id) {

    let modal = document.getElementById("rejectModal");
    let form = document.getElementById("rejectForm");

    form.action = "/tasks/" + id + "/reject/";

    modal.style.display = "flex";
}

function closeRejectModal() {
    document.getElementById("rejectModal").style.display = "none";
}


// Outside click close
window.onclick = function (e) {

    let taskModal = document.getElementById("taskModal");
    let rejectModal = document.getElementById("rejectModal");

    if (e.target === taskModal) {
        taskModal.style.display = "none";
    }

    if (e.target === rejectModal) {
        rejectModal.style.display = "none";
    }

};

// Search task
const searchInput = document.getElementById("taskSearch");

if (searchInput) {

    searchInput.addEventListener("keyup", function () {

        let value = this.value.toLowerCase();

        document.querySelectorAll("#taskTable tbody tr").forEach(function (row) {

            row.textContent.toLowerCase().includes(value)
                ? row.style.display = ""
                : row.style.display = "none";

        });

    });

}



// Status tabs filter
const tabs = document.querySelectorAll(".tab");

if (tabs.length > 0) {

    const rows = document.querySelectorAll("#taskTable tbody tr");

    tabs.forEach(tab => {

        tab.addEventListener("click", () => {

            tabs.forEach(t => t.classList.remove("active"));
            tab.classList.add("active");

            const status = tab.dataset.status;

            rows.forEach(row => {

                if (status === "all" || row.dataset.status === status) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }

            });

        });

    });

}