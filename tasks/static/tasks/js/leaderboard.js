document.addEventListener("DOMContentLoaded", function () {

    const buttons = document.querySelectorAll(".lb-btn");
    const tabs = document.querySelectorAll(".lb-content");

    buttons.forEach(function (btn) {

        btn.addEventListener("click", function () {

            // remove active class
            buttons.forEach(function (b) {
                b.classList.remove("active");
            });

            tabs.forEach(function (t) {
                t.classList.remove("active");
            });

            // activate button
            btn.classList.add("active");

            // activate tab
            const tabId = btn.getAttribute("data-tab");
            const tab = document.getElementById(tabId);

            if (tab) {
                tab.classList.add("active");
            }

        });

    });

});