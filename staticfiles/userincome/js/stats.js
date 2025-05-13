const renderChat = (data, labels) => {
    const ctx = document.getElementById('myChart').getContext('2d');
    const getRandomType = () => {
        const types = [
          "bar",
          "pie",
          "line",
          "doughnut",
          "polarArea",
        ];
        return types[Math.floor(Math.random() * types.length)];
      };
      const type = getRandomType();
    const myChart = new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                label: 'Last 6 months eppenses',
                data: data,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            title: {
                display: true,
                text: 'Income per category'
            }
        }
    });

};

const getChartData=()=>{
    fetch('/income/income_summery').then(res=>res.json()).then(result=>{
        console.log('result',result)
        const income_data = result.income_source_amount;
        const [labels,data] = [
            Object.keys(income_data),
            Object.values(income_data),
        ];
        renderChat(data,labels);
    });
};



document.onload=getChartData();