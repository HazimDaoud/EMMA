document.addEventListener('DOMContentLoaded', function () {
    var datapoints_to_display = 100
    var ctx = document.getElementById("plot").getContext('2d');

    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({length: datapoints_to_display}, (_, index) => index + 1),
            datasets: [
                {
                    label: 'X',
                    data: [],
                    fill: false,
                    borderColor: 'red',
                    borderWidth: 1
                },
                {
                    label: 'Y',
                    data: [],
                    fill: false,
                    borderColor: 'green',
                    borderWidth: 1
                },
                {
                    label: 'Z',
                    data: [],
                    fill: false,
                    borderColor: 'blue',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            datasets: {
                line: {
                    pointRadius: 0 // disable for all `'line'` datasets
                }
            }
        }
    });

    var socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('connect', function () {
        console.log('Connected to server');
        socket.emit('get_measurements');
    });

    socket.on('measurements', function (data) {
        // Assuming data is an array of three values [x, y, z]
        myChart.data.datasets[0].data.push(data.data[0]); // X
        myChart.data.datasets[1].data.push(data.data[1]); // Y
        myChart.data.datasets[2].data.push(data.data[2]); // Z

        // Keep only the last 30 data points
        if (myChart.data.datasets[0].data.length > datapoints_to_display) {
            myChart.data.datasets[0].data.shift();
            myChart.data.datasets[1].data.shift();
            myChart.data.datasets[2].data.shift();
        }

        myChart.update();

        var fallStatus = document.getElementById('fallStatus');
        fallStatus.innerText = data.classification ? 'Fall detected!' : 'All right!';
        fallStatus.style.color = data.classification ? 'red' : 'green';
    });
});
