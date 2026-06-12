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
    var html = "";
 
    for (var i = 0; i < goals.length; i++) {
        var goal = goals[i];
 
        if (goal.subject == selectedVak) {
            var gemiddelde = "Geen score";
 
            if (goal.avg_kennen != null && goal.avg_kunnen != null) {
                var som = goal.avg_kennen + goal.avg_kunnen;
                var avg = som / 2;
                gemiddelde = (avg * 10).toFixed(1);
            }
 
            html = html + "<div class='goal-item'>";
            html = html + "<h3>" + goal.title + "</h3>";
            html = html + "<p>Vak: " + goal.subject + "</p>";
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
    var html = "";
 
    for (var i = 0; i < goals.length; i++) {
        var goal = goals[i];
 
        if (goal.subject == selectedVak) {
            var snapshots = goal.snapshots;
            var taxonomy = [];
 
            if (snapshots.length > 0) {
                var laatsteSnapshot = snapshots[snapshots.length - 1];
                taxonomy = laatsteSnapshot.taxonomy;
            }
 
            html = html + "<div class='goal-item'>";
            html = html + "<h3>" + goal.title + "</h3>";
            html = html + "<p>Laatste taxonomie:</p>";
            html = html + "<ul>";
 
            for (var j = 0; j < taxonomy.length; j++) {
                var item = taxonomy[j];
                html = html + "<li>" + item.level + ": kennen " + item.kennen + ", kunnen " + item.kunnen + "</li>";
            }
 
            html = html + "</ul>";
            html = html + "</div>";
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
    var kernwoorden = [];
    var html = "";
 
    for (var i = 0; i < goals.length; i++) {
        var goal = goals[i];
 
        if (goal.subject == selectedVak) {
            for (var j = 0; j < goal.keywords.length; j++) {
                var keyword = goal.keywords[j];
 
                if (kernwoorden.indexOf(keyword) == -1) {
                    kernwoorden.push(keyword);
                }
            }
        }
    }
 
    for (var i = 0; i < kernwoorden.length; i++) {
        html = html + "<span class='keyword-chip'>" + kernwoorden[i] + "</span>";
    }
 
    if (html == "") {
        kernwoordenLijst.innerHTML = "<p>Geen kernwoorden gevonden.</p>";
    } else {
        kernwoordenLijst.innerHTML = html;
    }
}
 
loadData();
