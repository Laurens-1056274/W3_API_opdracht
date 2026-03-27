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
	return value === null || value === undefined ? "-" : `${value}`;
}


function showChartByMonth(type) {
	if (!Array.isArray(allLearningGoals) || allLearningGoals.length === 0) {
		if (chart) chart.destroy();
		return;
	}

	let monthlyData = {};

	allLearningGoals.forEach((goal) => {
		goal.snapshots.forEach((snapshot) => {
			const sourceType = snapshot.source?.type?.toLowerCase() || "";


			if (type === "all" || sourceType === type.toLowerCase()) {
				const month = snapshot.at.slice(0, 7);

				if (!monthlyData[month]) monthlyData[month] = [];
				monthlyData[month].push(snapshot.taxonomy);
			}
		});
	});

	const months = Object.keys(monthlyData).sort();


	if (months.length === 0) {
		if (chart) chart.destroy();
		console.warn("Geen data voor", type);
		return;
	}

	const labels = months;
	const kennenData = [];
	const kunnenData = [];

	months.forEach((month) => {
		const monthSets = monthlyData[month];

		let kennenSum = 0,
			kunnenSum = 0,
			count = 0;

		monthSets.forEach((set) => {
			set.forEach((t) => {
				kennenSum += t.kennen;
				kunnenSum += t.kunnen;
				count++;
			});
		});

		if (count === 0) {
			kennenData.push(0);
			kunnenData.push(0);
		} else {
			kennenData.push(Math.round((kennenSum / count) * 100));
			kunnenData.push(Math.round((kunnenSum / count) * 100));
		}
	});


	if (chart) chart.destroy();


	chart = new Chart(document.getElementById("myChart"), {
		type: "bar",
		data: {
			labels,
			datasets: [
				{
					label: "Kennen",
					data: kennenData,
					backgroundColor: "rgba(0, 204, 102, 0.6)",
				},
				{
					label: "Kunnen",
					data: kunnenData,
					backgroundColor: "rgba(22, 172, 247, 0.6)",
				},
			],
		},
		options: {
			responsive: true,
			plugins: {
				legend: {
					position: "top",
					labels: { font: { size: 14, family: "Arial", weight: "bold" } },
				},
				title: {
					display: true,
					text: `Voortgang per Maand (${type})`,
					font: { size: 18, family: "Arial", weight: "bold" },
				},
			},
			scales: {
				y: {
					beginAtZero: true,
					max: 100,
					ticks: {
						font: { size: 12, family: "Arial" },
						callback: (value) => value,
					},
				},
				x: { ticks: { font: { size: 12, family: "Arial" } } },
			},
		},
	});
}