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
