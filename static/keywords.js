// Global variables
let allKeywords = [];
let currentFilter = 'all';
let currentSort = 'performance';

// Initialize on page load
document.addEventListener("DOMContentLoaded", function () {
    loadKeywords();
    setupEventListeners();
});

function setupEventListeners() {
    const subjectFilter = document.getElementById("subjectFilter");
    const sortSelect = document.getElementById("sortSelect");

    if (subjectFilter) {
        subjectFilter.addEventListener("change", function() {
            currentFilter = this.value;
            renderKeywords();
        });
    }

    if (sortSelect) {
        sortSelect.addEventListener("change", function() {
            currentSort = this.value;
            renderKeywords();
        });
    }
}

function loadKeywords() {
    const loadingMessage = document.getElementById("loadingMessage");
    const container = document.getElementById("keywordsContainer");
    const noResults = document.getElementById("noResults");

    const xhr = new XMLHttpRequest();
    xhr.open("GET", "/api/student/keywords");

    xhr.onload = function () {
        loadingMessage.style.display = "none";

        if (xhr.status === 200) {
            const result = JSON.parse(xhr.responseText);
            allKeywords = result.keywords || [];

            if (allKeywords.length === 0) {
                noResults.style.display = "block";
                return;
            }

            // Populate subject filter
            populateSubjectFilter();

            // Render keywords
            container.style.display = "grid";
            renderKeywords();
        } else {
            noResults.style.display = "block";
            const errorMsg = document.createElement("p");
            errorMsg.textContent = "Fout bij het laden van kernwoorden: " + xhr.statusText;
            errorMsg.style.color = "#dc3545";
            noResults.appendChild(errorMsg);
        }
    };

    xhr.onerror = function () {
        loadingMessage.style.display = "none";
        noResults.style.display = "block";
        const errorMsg = document.createElement("p");
        errorMsg.textContent = "Netwerkfout bij het laden van kernwoorden";
        errorMsg.style.color = "#dc3545";
        noResults.appendChild(errorMsg);
    };

    xhr.send();
}

function populateSubjectFilter() {
    const subjectFilter = document.getElementById("subjectFilter");
    const subjects = new Set();

    allKeywords.forEach(keyword => {
        keyword.subjects.forEach(subject => subjects.add(subject));
    });

    // Clear existing options except "Alle vakken"
    while (subjectFilter.options.length > 1) {
        subjectFilter.remove(1);
    }

    // Add subject options
    Array.from(subjects).sort().forEach(subject => {
        const option = document.createElement("option");
        option.value = subject;
        option.textContent = subject;
        subjectFilter.appendChild(option);
    });
}

function renderKeywords() {
    const container = document.getElementById("keywordsContainer");
    const noResults = document.getElementById("noResults");

    // Filter keywords
    let filteredKeywords = allKeywords;
    if (currentFilter !== 'all') {
        filteredKeywords = allKeywords.filter(keyword => 
            keyword.subjects.includes(currentFilter)
        );
    }

    // Sort keywords
    filteredKeywords = sortKeywords(filteredKeywords, currentSort);

    // Clear container
    container.innerHTML = "";

    if (filteredKeywords.length === 0) {
        container.style.display = "none";
        noResults.style.display = "block";
        return;
    }

    container.style.display = "grid";
    noResults.style.display = "none";

    // Render each keyword card
    filteredKeywords.forEach(keyword => {
        const card = createKeywordCard(keyword);
        container.appendChild(card);
    });
}

function sortKeywords(keywords, sortType) {
    const sorted = [...keywords];

    switch (sortType) {
        case 'alphabetical':
            sorted.sort((a, b) => a.keyword.localeCompare(b.keyword));
            break;
        case 'kennen':
            sorted.sort((a, b) => (b.avg_kennen || 0) - (a.avg_kennen || 0));
            break;
        case 'kunnen':
            sorted.sort((a, b) => (b.avg_kunnen || 0) - (a.avg_kunnen || 0));
            break;
        case 'performance':
        default:
            // Already sorted by performance (weakest first) from backend
            break;
    }

    return sorted;
}

function createKeywordCard(keyword) {
    const card = document.createElement("div");
    card.className = "keyword-card";

    const avgKennen = keyword.avg_kennen || 0;
    const avgKunnen = keyword.avg_kunnen || 0;
    const avgTotal = (avgKennen + avgKunnen) / 2;

    // Determine strength category
    const strength = getStrengthCategory(avgTotal);
    card.classList.add(strength);

    // Create card HTML
    card.innerHTML = `
        <div class="keyword-header">
            <div class="keyword-name">${escapeHtml(keyword.keyword)}</div>
            <div class="keyword-badge ${strength}">${getStrengthLabel(avgTotal)}</div>
        </div>

        <div class="keyword-subjects">
            <i class="fa fa-book"></i> ${keyword.subjects.join(", ")}
        </div>

        <div class="keyword-scores">
            <div class="score-item">
                <div class="score-label">Kennen</div>
                <div class="score-value" style="color: ${getScoreColor(avgKennen)}">
                    ${avgKennen.toFixed(1)}
                </div>
            </div>
            <div class="score-item">
                <div class="score-label">Kunnen</div>
                <div class="score-value" style="color: ${getScoreColor(avgKunnen)}">
                    ${avgKunnen.toFixed(1)}
                </div>
            </div>
        </div>

        <div class="keyword-progress">
            <div class="progress-bar-container">
                <div class="progress-bar ${strength}" style="width: ${(avgTotal / 10) * 100}%"></div>
            </div>
            <div style="text-align: center; font-size: 0.85rem; color: #718096;">
                Gemiddeld: ${avgTotal.toFixed(1)}
            </div>
        </div>

        <div class="keyword-meta">
            <span>
                <i class="fa fa-chart-line"></i> ${keyword.snapshot_count} metingen
            </span>
            <span>
                <i class="fa fa-bullseye"></i> ${keyword.learning_goals.length} leerdoelen
            </span>
        </div>

        <div class="keyword-goals">
            <a href="#" class="toggle-goals" style="color: #4895ef; text-decoration: none;">
                <i class="fa fa-chevron-down"></i> Toon leerdoelen
            </a>
            <div class="keyword-goals-list">
                ${keyword.learning_goals.map(lg => `<div class="goal-item">• ${escapeHtml(lg.title)}</div>`).join('')}
            </div>
        </div>
    `;

    // Add click handler for toggling learning goals
    const toggleLink = card.querySelector('.toggle-goals');
    const goalsList = card.querySelector('.keyword-goals-list');
    
    toggleLink.addEventListener('click', function(e) {
        e.preventDefault();
        goalsList.classList.toggle('show');
        const icon = this.querySelector('i');
        if (goalsList.classList.contains('show')) {
            icon.className = 'fa fa-chevron-up';
            this.innerHTML = '<i class="fa fa-chevron-up"></i> Verberg leerdoelen';
        } else {
            icon.className = 'fa fa-chevron-down';
            this.innerHTML = '<i class="fa fa-chevron-down"></i> Toon leerdoelen';
        }
    });

    return card;
}

function getStrengthCategory(score) {
    if (score >= 7.0) return 'strong';
    if (score >= 5.5) return 'moderate';
    return 'weak';
}

function getStrengthLabel(score) {
    if (score >= 7.0) return 'Goed';
    if (score >= 5.5) return 'Voldoende';
    return 'Aandacht nodig';
}

function getScoreColor(score) {
    if (score >= 7.0) return '#28a745';
    if (score >= 4.0) return '#ffc107';
    return '#dc3545';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}