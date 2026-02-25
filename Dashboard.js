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


