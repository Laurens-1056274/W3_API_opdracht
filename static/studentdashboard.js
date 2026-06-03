let allLearningGoals;
let chart;
let chartType = "all";

fetch("/api/student/voortgang")
	.then((res) => {
		if (!res.ok) throw new Error("Niet ingelogd of serverfout");
		return res.json();
	})
	.then((data) => {
		allLearningGoals = data.learningGoals;
		showChartByMonth(chartType);
	})
	.catch((err) => console.error("Error loading data:", err));

document.getElementById("chartTypeSelect").addEventListener("change", (e) => {
	chartType = e.target.value;
	showChartByMonth(chartType);
});
function showChartByMonth(type) {
	let monthlyData = {};

	allLearningGoals.forEach((goal) => {
		goal.snapshots.forEach((snapshot) => {
			if (type === "all" || snapshot.source.type === type) {
				const month = snapshot.at.slice(0, 7);
				if (!monthlyData[month]) monthlyData[month] = [];
				monthlyData[month].push(snapshot.taxonomy);
			}
		});
	});
	const months = Object.keys(monthlyData).sort();
	if (months.length === 0) {
		alert("Geen data voor " + type);
		if (chart) chart.destroy();
		return;
	}
	const labels = months.map(m => {
    const [year, month] = m.split("-");
    return `${month}-${year}`;
	});
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
		kennenData.push(parseFloat(((kennenSum / count) * 10).toFixed(1)));
		kunnenData.push(parseFloat(((kunnenSum / count) * 10).toFixed(1)));

	});
	if (chart) chart.destroy();
	chart = new Chart(document.getElementById("myChart"), {
		type: "line",
		data: {
			labels,
			datasets: [
				{
					label: "Kennen",
					data: kennenData,
					backgroundColor: "rgba(54, 162, 235, 0.6)",
				},
				{
					label: "Kunnen",
					data: kunnenData,
					backgroundColor: "rgba(255, 206, 86, 0.6)",
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
					text: `Voortgang per maand (${type}) — 0-10`,
					font: { size: 18, family: "Arial", weight: "bold" },
				},
			},
			scales: {
				y: {
					beginAtZero: true,
					max: 10,
					ticks: {
						font: { size: 12, family: "Arial" },
						callback: (value) => value.toFixed(1),
					},
				},
				x: { ticks: { font: { size: 12, family: "Arial" } } },
			},
		},
	});
}
