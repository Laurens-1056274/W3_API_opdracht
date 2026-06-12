let allLearningGoals;
let chart;
let chartType = "all";
const classSelect = document.getElementById("classSelect");
const classOverviewBody = document.getElementById("classOverviewBody");

if (classSelect?.value) {
	loadClassData(classSelect.value);
	loadClassOverview(classSelect.value);
}


document.getElementById("chartTypeSelect").addEventListener("change", (e) => {
	chartType = e.target.value;
	showChartByMonth(chartType);
});


classSelect?.addEventListener("change", (e) => {
	const klas = e.target.value;
	loadClassData(klas);
	loadClassOverview(klas);
});


function loadClassData(klas) {
	fetch(`/api/class/voortgang?klas=${encodeURIComponent(klas)}`)
		.then((res) => {
			if (!res.ok) throw new Error("Niet ingelogd of serverfout");
			return res.json();
		})
		.then((data) => {
			allLearningGoals = data.learningGoals || [];
			showChartByMonth(chartType);
		})
		.catch((err) => console.error("Error loading class data:", err));
}


function loadClassOverview(klas) {
	fetch(`/api/class/leerlingen?klas=${encodeURIComponent(klas)}`)
		.then((res) => {
			if (!res.ok) throw new Error("Kon klasoverzicht niet laden");
			return res.json();
		})
		.then((data) => {
			renderClassOverview(data.students || []);
		})
		.catch((err) => {
			console.error("Error loading class overview:", err);
			renderClassOverview([]);
		});
}


function renderClassOverview(students) {
	if (!classOverviewBody) return;

	if (!Array.isArray(students) || students.length === 0) {
		classOverviewBody.innerHTML = `
			<tr>
				<td colspan="5">Geen leerlingendata gevonden voor deze klas</td>
			</tr>
		`;
		return;
	}

	classOverviewBody.innerHTML = students
		.map(
			(student) => `
			<tr>
				<td>${student.name ?? "-"}</td>
				<td>${formatValue(student.avg_kennen)}</td>
				<td>${formatValue(student.avg_kunnen)}</td>
				<td>${formatValue(student.global_progress)}</td>
				<td>${student.status ?? "-"}</td>
			</tr>
		`
		)
		.join("");
}


function formatValue(value) {
	return value === null || value === undefined ? "-" : `${(value / 10).toFixed(2)}`;
}


function showChartByMonth(type) {
	if (!Array.isArray(allLearningGoals) || allLearningGoals.length === 0) {
		if (chart) chart.destroy();
		return;
	}

	let monthlyData = {};

	allLearningGoals.forEach((goal) => {
		(goal.snapshots || []).forEach((snapshot) => {
			const sourceType = snapshot.source?.type?.toLowerCase() || "";
			const requestedType = type.toLowerCase();
			const date = snapshot.at?.slice(0, 10);

			if (!date || (type !== "all" && sourceType !== requestedType)) {
				return;
			}

			const grade = getSnapshotGrade(snapshot.taxonomy);

			if (grade === null) {
				return;
			}

			if (!pointsByDate.has(date)) {
				pointsByDate.set(date, []);
			}

			pointsByDate.get(date).push(grade);
			allGrades.push(grade);
		});
	});

	const dates = Array.from(pointsByDate.keys()).sort();

	if (dates.length === 0) {
		if (chart) chart.destroy();
		console.warn("Geen data voor", type);
		return;
	}

	const labels = dates.map(formatDateLabel);
	const gradeData = [];
	const medianValue = getMedian(allGrades);

	// Display class average
	const classAverageDisplay = document.getElementById("classAverageDisplay");
	if (classAverageDisplay) {
		classAverageDisplay.textContent = medianValue.toFixed(2);
	}

	dates.forEach((date) => {
		const dateGrades = pointsByDate.get(date) || [];
		const average = dateGrades.reduce((sum, value) => sum + value, 0) / dateGrades.length;
		gradeData.push(Math.round(average));
	});


	if (chart) chart.destroy();


	chart = new Chart(document.getElementById("myChart"), {
		type: "line",
		data: {
			labels,
			datasets: [
				{
					label: "Cijfer",
					data: gradeData,
					borderColor: "rgba(22, 172, 247, 1)",
					backgroundColor: "rgba(22, 172, 247, 0.15)",
					pointBackgroundColor: "rgba(22, 172, 247, 1)",
					pointRadius: 4,
					tension: 0.3,
					fill: false,
				},
				{
					label: "Gemiddelde",
					data: labels.map(() => medianValue),
					borderColor: "rgba(120, 120, 120, 0.9)",
					borderDash: [2, 6],
					pointRadius: 0,
					fill: false,
				},
			],
		},
		options: {
			responsive: true,
			maintainAspectRatio: false,
			plugins: {
				legend: {
					position: "top",
					labels: { font: { size: 14, family: "Arial", weight: "bold" } },
				},
				title: {
					display: true,
					text: `Voortgang per tijd (${type})`,
					font: { size: 18, family: "Arial", weight: "bold" },
				},
			},
			scales: {
				y: {
					beginAtZero: true,
					max: 10,
					title: {
						display: true,
						text: "Cijfer",
					},
					ticks: {
						font: { size: 12, family: "Arial" },
						callback: (value) => value.toFixed(2),
					},
				},
				x: {
					title: {
						display: true,
						text: "Tijd",
					},
					ticks: { font: { size: 12, family: "Arial" } },
				},
			},
		},
	});
}

function getSnapshotGrade(taxonomy) {
	if (!Array.isArray(taxonomy) || taxonomy.length === 0) {
		return null;
	}

	let kennenSum = 0;
	let kennenCount = 0;
	let kunnenSum = 0;
	let kunnenCount = 0;

	taxonomy.forEach((item) => {
		if (typeof item?.kennen === "number") {
			kennenSum += item.kennen;
			kennenCount++;
		}
		if (typeof item?.kunnen === "number") {
			kunnenSum += item.kunnen;
			kunnenCount++;
		}
	});

	if (kennenCount === 0 && kunnenCount === 0) {
		return null;
	}

	const kennenAverage = kennenCount > 0 ? kennenSum / kennenCount : null;
	const kunnenAverage = kunnenCount > 0 ? kunnenSum / kunnenCount : null;
	const parts = [kennenAverage, kunnenAverage].filter((value) => value !== null);

	return Math.round((parts.reduce((sum, value) => sum + value, 0) / parts.length) * 10);
}

function getMedian(values) {
	if (!Array.isArray(values) || values.length === 0) {
		return 0;
	}

	const average = values.reduce((sum, value) => sum + value, 0) / values.length;
	return Math.round(average * 100) / 100;
}

function formatDateLabel(dateValue) {
	const [year, month, day] = dateValue.split("-");
	return `${day}-${month}-${year}`;
}