// Get data from HTML data attribute
const knnDiv = document.getElementById('knn-metrics');
const knnData = JSON.parse(knnDiv.dataset.knndata);

const accuracy = knnData.accuracy;
const correctPct = knnData.correctPct;
const incorrectPct = knnData.incorrectPct;
const elapsedTime = knnData.elapsedTime;

// --- Bar Chart for Accuracy / Correct / Incorrect ---
const ctx1 = document.getElementById('knnChart').getContext('2d');
new Chart(ctx1, {
    type: 'bar',
    data: {
        labels: ['Accuracy', 'Correct %', 'Incorrect %'],
        datasets: [{
            label: 'KNN Performance (%)',
            data: [accuracy, correctPct, incorrectPct],
            backgroundColor: ['#3fbbc0', '#28a745', '#dc3545']
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { display: false },
            tooltip: { enabled: true }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 100,
                title: { display: true, text: 'Percentage (%)' }
            }
        }
    }
});

// --- Line Chart for Time Efficiency ---
const ctx2 = document.getElementById('timeChart').getContext('2d');
new Chart(ctx2, {
    type: 'line',
    data: {
        labels: ['KNN Model'],
        datasets: [{
            label: 'Time Efficiency (ms)',
            data: [elapsedTime],
            borderColor: '#ff9800',
            backgroundColor: 'rgba(255,152,0,0.2)',
            fill: true,
            tension: 0.3,
            pointBackgroundColor: '#ff9800',
            pointRadius: 6
        }]
    },
    options: {
        responsive: true,
        plugins: { legend: { display: true } },
        scales: {
            y: {
                beginAtZero: true,
                title: { display: true, text: 'Milliseconds (ms)' }
            }
        }
    }
});
