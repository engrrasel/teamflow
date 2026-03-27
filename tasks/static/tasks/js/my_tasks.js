// ================= TAB SYSTEM =================
document.addEventListener("DOMContentLoaded", function () {

    // ---------- Tabs ----------
    const tabs = document.querySelectorAll(".tab-btn");
    const contents = document.querySelectorAll(".tab-content");

    tabs.forEach(tab => {
        tab.addEventListener("click", function () {

            const target = this.dataset.tab;

            tabs.forEach(t => t.classList.remove("active"));
            contents.forEach(c => c.classList.remove("active"));

            this.classList.add("active");
            document.getElementById(target).classList.add("active");
        });
    });


    // ================= ROW CLICK CONTROL =================
    document.querySelectorAll(".clickable-row").forEach(row => {

        row.addEventListener("click", function () {

            const isChecked = this.dataset.checked === "true";

            if (!isChecked) {
                alert("Please check in first");
                return;
            }

            window.location.href = this.dataset.url;
        });

    });


    // ================= CHECK-IN =================
    document.querySelectorAll(".checkin-btn").forEach(btn => {

        btn.addEventListener("click", function (e) {
            e.stopPropagation();

            const assignmentId = this.dataset.id;
            const detailUrl = this.dataset.url;
            const button = this;
            const row = this.closest("tr");

            console.log("CHECK-IN CLICKED", assignmentId); // ✅ এখানে রাখুন

            if (!assignmentId) {
                alert("Assignment ID missing");
                return;
            }

            if (!navigator.geolocation) {
                alert("Geolocation not supported");
                return;
            }

            button.innerText = "Checking...";
            button.disabled = true;

            navigator.geolocation.getCurrentPosition(function (position) {

                const lat = position.coords.latitude;
                const lng = position.coords.longitude;

                fetch(`/tasks/check-in/${assignmentId}/`, { // 🔥 URL FIX
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "X-CSRFToken": getCSRFToken()
                    },
                    body: `lat=${lat}&lng=${lng}`
                })
                .then(res => res.json())
                .then(data => {

                    if (data.status === "success" || data.status === "already") {

                        button.innerText = `Checked in at ${data.time}`;
                        button.classList.remove("btn-success");
                        button.classList.add("btn-secondary");
                        button.disabled = true;

                        row.dataset.checked = "true";
                        row.classList.remove("disabled-row");

                        setTimeout(() => {
                            window.location.href = detailUrl;
                        }, 500);

                    } else {
                        button.innerText = "Check In";
                        button.disabled = false;
                        alert(data.message || "Check-in failed");
                    }

                })
                .catch(() => {
                    button.innerText = "Check In";
                    button.disabled = false;
                    alert("Server error");
                });

            }, function () {
                button.innerText = "Check In";
                button.disabled = false;
                alert("Location permission denied");
            });

        });

    });

});


// ================= CSRF =================
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : "";
}


// ================= LIVE LOCATION =================
function sendLocation() {

    if (!navigator.geolocation) return;

    navigator.geolocation.getCurrentPosition(function (pos) {

        let lat = pos.coords.latitude;
        let lng = pos.coords.longitude;

        fetch(`/tasks/update-location/?lat=${lat}&lng=${lng}`);

    });

}

// every 20 sec
setInterval(sendLocation, 20000);