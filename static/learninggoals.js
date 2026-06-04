document.addEventListener("DOMContentLoaded", function () {
    const select = document.getElementById("chartTypeSelect");
    const items = document.querySelectorAll(".learning-goal");
    const noResults = document.getElementById("noResults");

    select.addEventListener("change", function () {
        const selected = this.value;
        let visibleCount = 0;

        items.forEach(item => {
            const subject = item.getAttribute("data-subject");

            if (selected === "AlleVakken" || selected === subject) {
                item.style.display = "block";
                visibleCount++;
            } else {
                item.style.display = "none";
            }
        });

        noResults.style.display = visibleCount === 0 ? "block" : "none";
    });
});