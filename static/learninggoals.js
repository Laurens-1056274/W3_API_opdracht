document.addEventListener("DOMContentLoaded", function () {
    const select = document.getElementById("chartTypeSelect");

    select.addEventListener("change", function () {
        const selected = this.value;
        const items = document.querySelectorAll(".learning-goal");

        items.forEach(item => {
            const subject = item.getAttribute("data-subject");

            if (selected === "AlleVakken" || selected === subject) {
                item.style.display = "block";
            } else {
                item.style.display = "none";
            }
        });
    });
});