const leerdoelenLijst = document.getElementById("leerdoelenlijst");
const taxonomieLijst = document.getElementById("taxonomielijst");
const kernwoordenLijst = document.getElementById("kernwoordenlijst");
const klasSelect = document.getElementById("klas");
const vakkenSelect = document.getElementById("vakken");
 
klasSelect.addEventListener("change", function() {
    loadData();
});
 
vakkenSelect.addEventListener("change", function() {
    loadData();
});
 
function loadData() {
    const klas = klasSelect.value;
    const vak = vakkenSelect.value;
 
    fetch(API_URL + "?klas=" + klas + "&vak=" + vak)
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            toonLeerdoelen(data);
            toonTaxonomieniveaus(data);
            toonKernwoorden(data);
        });
}
 
function toonLeerdoelen(data) {
    const goals = data.learningGoals;
    const selectedVak = vakkenSelect.value;
    let html = "";
 
    for (let i = 0; i < goals.length; i++) {
        let goal = goals[i];
 
        if (goal.subject == selectedVak) {
            let gemiddelde = "Geen score";
 
            if (goal.avg_kennen != null && goal.avg_kunnen != null) {
                let som = goal.avg_kennen + goal.avg_kunnen;
                let avg = som / 2;
                let score = (avg * 10).toFixed(1);
                //We hebben gekozen voor 5.5 als voldoende. Dit kan worden aangepast naar wens van de opdrachtgever//
                let css = score < 5.5 ? "onvoldoende" : "voldoende";
                gemiddelde = "<span class='" + css + "'>" + score + "</span>";

            }
 
            html = html + "<div class='goal-item'>";
            html = html + "<h3>" + goal.title + "</h3>";
            html = html + "<p>Gemiddelde: " + gemiddelde + "</p>";
            html = html + "</div>";
        }
    }
 
    if (html == "") {
        leerdoelenLijst.innerHTML = "<p>Geen leerdoelen gevonden.</p>";
    } else {
        leerdoelenLijst.innerHTML = html;
    }
}
 
function toonTaxonomieniveaus(data) {
    const goals = data.learningGoals;
    const selectedVak = vakkenSelect.value;
    let html = "";
 
    for (let i = 0; i < goals.length; i++) {
        let goal = goals[i];
 
        if (goal.subject == selectedVak) {
            let snapshots = goal.snapshots;
            let taxonomy = [];
 
            if (snapshots.length > 0) {
                let laatsteSnapshot = snapshots[snapshots.length - 1];
                taxonomy = laatsteSnapshot.taxonomy;
            }
 
            html = html + "<div class='goal-item'>";
            html = html + "<h3>" + goal.title + "</h3>";
            html = html + "<ul>";
 
            for (let j = 0; j < taxonomy.length; j++) {
                let item = taxonomy[j];
                //We hebben gekozen voor 5.5 als voldoende. Dit kan worden aangepast naar wens van de opdrachtgever//
                let kennenScore = (item.kennen * 10).toFixed(1);
                let kunnenScore = (item.kunnen * 10).toFixed(1);

                let kennen = parseFloat(kennenScore) < 5.5 ? "onvoldoende" : "voldoende";
                let kunnen = parseFloat(kunnenScore) < 5.5 ? "onvoldoende" : "voldoende";

                html = html + "<li>" + item.level +
                ": kennen <span class='" + kennen + "'>" + kennenScore + "</span>" +
                ", kunnen <span class='" + kunnen + "'>" + kunnenScore + "</span></li>";
            }
        }
    }
 
    if (html == "") {
        taxonomieLijst.innerHTML = "<p>Geen taxonomieniveaus gevonden.</p>";
    } else {
        taxonomieLijst.innerHTML = html;
    }
}

 
function toonKernwoorden(data) {
    const goals = data.learningGoals;
    const selectedVak = vakkenSelect.value;
    let html = "";
 
    for (let i = 0; i < goals.length; i++) {
        let goal = goals[i];
 
        if (goal.subject == selectedVak) {
            
            html = html + "<div class='keyword-goal-group'>";
            html = html + "<h4>" + goal.title + "</h4>";
            html = html + "<div class='keyword-group'>";
 
            for (let j = 0; j < goal.keywords.length; j++) {
                let keyword = goal.keywords[j];

                html = html + "<span class='kernwoorden-overzicht'>" + keyword + "</span>";
            }


 
            html = html + "</div>";
            html = html + "</div>";
        }
    }
 
    if (html == "") {
        kernwoordenLijst.innerHTML = "<p>Geen kernwoorden gevonden.</p>";
    } else {
        kernwoordenLijst.innerHTML = html;
    }
}
 
loadData();
