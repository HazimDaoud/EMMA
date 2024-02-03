document.addEventListener('DOMContentLoaded', function () {
    var datapoints_to_display = 200
    var ctx = document.getElementById("plot").getContext('2d');

    //ctx.canvas.width = 800;
    ctx.canvas.height = 200;

    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({length: datapoints_to_display}, (_, index) => index + 1),
            datasets: [
                {
                    label: 'X',
                    data: Array(datapoints_to_display).fill(0),
                    fill: false,
                    borderColor: '#fc4f46d2',
                    borderWidth: 2
                },
                {
                    label: 'Y',
                    data: Array(datapoints_to_display).fill(0),
                    fill: false,
                    borderColor: '#628B61',
                    borderWidth: 2
                },
                {
                    label: 'Z',
                    data: Array(datapoints_to_display).fill(0),
                    fill: false,
                    borderColor: '#2f3c7e',
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    min: 0,
                    max: datapoints_to_display,
                    title: {
                        display: true,
                        text: '# samples'
                    }
                },
                y: {
                    type: 'linear',
                    suggestedMin: -4,
                    suggestedMax: 4,
                    title: {
                        display: true,
                        text: 'acceleration [g]'
                    }
                }
            },
            datasets: {
                line: {
                    pointRadius: 0 // disable for all `'line'` datasets
                }
            },

        }
    });

    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var measurementsRequested = false; // Flag to track whether measurements are already requested
    socket.on('connect', function () {
        console.log('Connected to server');
        if (!measurementsRequested) {
            socket.emit('get_measurements');
            measurementsRequested = true; // Set the flag to true to indicate that measurements are requested
        }
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
        // Calculate the minimum and maximum values from the data
        //const minValue = Math.min(...myChart.data.datasets.flatMap(dataset => dataset.data));
        //const maxValue = Math.max(...myChart.data.datasets.flatMap(dataset => dataset.data));

        // Update the y-axis boundaries
        //myChart.options.scales.y.suggestedMin = minValue - 1; // Adding a buffer
        //myChart.options.scales.y.suggestedMax = maxValue + 1; // Adding a buffer
        if (!stop) {
            myChart.update();
            var fallStatusArduino = document.getElementById('fallStatusArduino');
            var fallStatusInterface = document.getElementById('fallStatusInterface');
        }

        fallStatusArduino.innerText = data.classification ? 'Fall detected!(Arduino)' : 'All right!';
        fallStatusArduino.style.color = data.classification ? '#fc4f46d2': '#628B61';
        fallStatusInterface.innerText = data.other_pred ? 'Fall detected! (Interface)' : 'All right!';
        fallStatusInterface.style.color = data.other_pred ? '#fc4f46d2': '#628B61';
        if (!freeze && data.classification && data.new_pred && !data.prev ) {
            // Simulate a fall button click
            freeze = true;
            simulateFallButtonClick();
        }
    });
});
