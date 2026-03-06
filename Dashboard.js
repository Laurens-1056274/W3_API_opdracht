let allData;
let chart;
const currentStudentId = 8;
let chartType = "all";


fetch("data-sample-small.json")
  .then(res => res.json())
  .then(data => {
      allData = data.entries;
      showChartByMonth(chartType);
  })
  .catch(err => console.error("Error loading JSON:", err));

document.getElementById("chartTypeSelect").addEventListener("change", (e) => {
chartType = e.target.value;
showChartByMonth(chartType);
});
function showChartByMonth(type) {
const studentEntries = allData.filter(e => e.student.id === currentStudentId);
let monthlyData = {};

 studentEntries.forEach(entry => {
    entry.learningGoals.forEach(goal => {
      goal.snapshots.forEach(snapshot => {
        if(type === "all" || snapshot.source.type === type) {
          const month = snapshot.at.slice(0,7);
          if(!monthlyData[month]) monthlyData[month] = [];
          monthlyData[month].push(snapshot.taxonomy);
        }
      });
    });
  });
const months = Object.keys(monthlyData).sort();
  if(months.length === 0) {
    alert("Geen data voor " + type);
    if(chart) chart.destroy();
    return;
  }
const labels = months;
  const kennenData = [];
  const kunnenData = [];
  const confidenceData = [];
  months.forEach(month => {
    const monthSets = monthlyData[month];
    let kennenSum=0, kunnenSum=0, confidenceSum=0, count=0;
    monthSets.forEach(set => {
      set.forEach(t => {
        kennenSum += t.kennen;
        kunnenSum += t.kunnen;
        confidenceSum += t.confidence;
        count++;
      });
    });
    kennenData.push(kennenSum / count);
    kunnenData.push(kunnenSum / count);
    confidenceData.push(confidenceSum / count);
  });
    if(chart) chart.destroy();
    chart = new Chart(document.getElementById("myChart"), {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: "Kennen", data: kennenData, backgroundColor: 'rgba(54, 162, 235, 0.6)' },
        { label: "Kunnen", data: kunnenData, backgroundColor: 'rgba(255, 206, 86, 0.6)' },
        { label: "Confidence", data: confidenceData, backgroundColor: 'rgba(75, 192, 192, 0.6)' }
      ]
    },
 options: {
      responsive: true,
      plugins: {
        legend: { position: 'top', labels: { font: { size: 14, family:'Arial', weight:'bold' } } },
        title: { display: true, text: `Voortgang per Maand (${type})`, font: { size: 18, family:'Arial', weight:'bold' } }
      },
      scales: {
        y: { beginAtZero: true, max: 1, ticks: { font: { size:12, family:'Arial' } } },
        x: { ticks: { font: { size:12, family:'Arial' } } }
      }
    }
  });
}


