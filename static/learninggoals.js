function applyFilter() {
    const select = document.getElementById("chartTypeSelect");
    const noResults = document.getElementById("noResults");
    const items = document.querySelectorAll(".learning-goal");
    const selected = select.value;

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
}
document.addEventListener("DOMContentLoaded", function () {
    const select = document.getElementById("chartTypeSelect");
    const container = document.querySelector(".scroll-container");

    const xhr = new XMLHttpRequest();
    xhr.open("GET", "/api/student/voortgang");

    xhr.onload = function () {
        const result = JSON.parse(xhr.responseText);
        const data = result.learningGoals || [];

        data.forEach(x => {
            const div = document.createElement("div");
            div.className = "learning-goal";
            div.setAttribute("data-subject", x.subject);
            div.innerHTML = `
                <hr style="background: linear-gradient(to bottom, rgba(255,255,255,0.1), transparent);">
                <h2 style="text-align: center;">${x.title}</h2>
                <p>Vak: ${x.subject}</p>

                <div class="profile-container">
                    <div class="profile-card">
                        <p>Kernwoorden bij dit leerdoel: ${x.keywords.join(", ")}</p>

                        <p>
                            Gemiddelde Kennen: ${x.avg_kennen}
                            <span class="${x.avg_kennen >= 5.5 ? "voldoende" : "onvoldoende"}" style="padding: 0 10px;">
                                ${x.avg_kennen >= 5.5 ? "voldoende" : "onvoldoende"}
                            </span>
                        </p>

                        <p>
                            Gemiddelde Kunnen: ${x.avg_kunnen}
                            <span class="${x.avg_kunnen >= 5.5 ? "voldoende" : "onvoldoende"}" style="padding: 0 10px;">
                                ${x.avg_kunnen >= 5.5 ? "voldoende" : "onvoldoende"}
                            </span>
                        </p>
                    </div>
                </div>
            `;
            container.appendChild(div);
        });

        applyFilter();
    };
    xhr.send();
    select.addEventListener("change", applyFilter);
});
