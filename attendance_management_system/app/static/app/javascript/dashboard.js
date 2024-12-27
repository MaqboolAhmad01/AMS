const playButton = document.getElementById('playButton');
const timerDisplay = document.getElementById('timer');
const modalOverlay = document.getElementById('modalOverlay');
const outTimeText = document.getElementById('outTime');
const saveButton = document.getElementById('saveButton');
const cancelButton = document.getElementById('cancelButton');

let timerInterval;
let seconds = 0; // To track the total elapsed time in seconds
let isRunning = false;
let user_id;

// Function to show the custom alert




function saveInTime() {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch('http://127.0.0.1:8080/app/check_in/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken  // Include CSRF token for Django
        },
        body: JSON.stringify()
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
        alert(data.message);
        
        
        if (data.attendance_id) {
            attendance_id = data.attendance_id;
            user_id = data.user_id;
            console.log("attendance_id",attendance_id);
            console.log("user_id",user_id);
            localStorage.setItem(`attendance_id_${user_id}`, attendance_id); 
            console.log(localStorage.getItem(`attendance_id_${user_id}`)); 
            console.log(`attendance_id_${user_id}`)
        }
    })
    .catch(error => {
        console.error('Error saving in time:', error);
    });
}

function saveOutTime() {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    attendance_id = localStorage.getItem(`attendance_id_${user_id}`)

    fetch('http://127.0.0.1:8080/app/check_out/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken  // Include CSRF token for Django
        },
        body: JSON.stringify({ 
            attendance_id: attendance_id // Replace with actual attendance record ID
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
        alert(data.message);
    })
    .catch(error => {
        console.error('Error saving out time:', error);
    });
}


function updateDisplay() {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const displaySeconds = seconds % 60;
    timerDisplay.textContent =
        (hrs < 10 ? '0' : '') + hrs + ':' +
        (mins < 10 ? '0' : '') + mins + ':' +
        (displaySeconds < 10 ? '0' : '') + displaySeconds;
}

// Function to start the timer
function startTimer() {
    timerInterval = setInterval(() => {
        seconds++; // Increment total seconds
        updateDisplay(); // Update the display every second
    },1000);
}


document.addEventListener("DOMContentLoaded", function() {

    fetchTimerData().then(data => {
        if (data) {
            const startTime = data.start_time;
            const elapsedTime = data.elapsed_seconds;
            user_id = data.user_id;
            
            if (startTime) {
                isRunning = true;
                playButton.innerHTML = '<i class="bi bi-stop-fill"></i>';
                seconds = elapsedTime ? parseInt(elapsedTime, 10) : 0; 
                updateDisplay(); // Update the timer display with the elapsed time
                startTimer(); // Start the timer if there was a start time
            } else {
                updateDisplay(); // Make sure to display the timer correctly if not running
            }
        } else {
            console.error('Error: No data received');
            updateDisplay(); // Fallback to default display update
        }
    }).catch(error => {
        console.error('Error fetching data:', error);
        updateDisplay(); // Handle display if fetch fails
    });
});


playButton.addEventListener('click', () => {
    
    if (!isRunning) {
        // Start timer
        isRunning = true;
        playButton.innerHTML = '<i class="bi bi-stop-fill"></i>';
        // localStorage.setItem('startTime', Date.now()); // Store the start time
        startTimer(); // Start the timer
        saveInTime();
    } else {
        // Stop timer and show modal
        isRunning = false;
        playButton.innerHTML = '<i class="bi bi-play-fill"></i>';
        clearInterval(timerInterval);
        // localStorage.setItem('elapsedTime', seconds); // Store the elapsed time

        // Show modal with current out time
        outTimeText.textContent = timerDisplay.textContent;
        modalOverlay.style.display = 'flex';
    }
});

function resetTimer() {
    clearInterval(timerInterval);
    
    seconds = 0; // Reset seconds
    updateDisplay(); // Reset display to 00:00:00
    isRunning = false;
    playButton.innerHTML = '<i class="bi bi-play-fill"></i>';
}

// Save and reset timer when user confirms
saveButton.addEventListener('click', () => {
    const outTime = timerDisplay.textContent;
    saveOutTime();
    resetTimer(); // Reset timer after saving
    modalOverlay.style.display = 'none'; // Close modal
});

// Close modal and continue timer when user cancels
cancelButton.addEventListener('click', () => {
    modalOverlay.style.display = 'none'; // Close modal
    if (!isRunning) { // Resume timer if it was stopped
        isRunning = true;
        playButton.innerHTML = '<i class="bi bi-stop-fill"></i>';
        startTimer(); // Restart the timer
    }
});

const ctx = document.getElementById('myChart').getContext('2d');
const myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: [],  // Empty initially, will be updated by fetched data
        datasets: [{
            label: 'Hours Worked',
            data: [],
            backgroundColor: '#004d3b'
        }]
    },
    options: {
        responsive:false,
        scales: {
            y: {
                beginAtZero: true,
                max: 12,
                
                ticks: {
                    callback: function(value) {
                        // Adjust y-axis scale based on data range
                        if (value < 60) {
                            return value + 's'; // Seconds scale (0 - 60s)
                        } else if (value < 3600) {
                            return Math.floor(value / 60) + 'm'; // Minutes scale (1m - 60m)
                        } else if (value < 43200) {
                            return Math.floor(value / 3600) + 'h'; // Hours scale (1h - 12h)
                        } else {
                            return Math.floor(value / 3600) + 'h'; // Extended hour scale (up to 24h)
                        }
                    }
                }
            },
            x: {
                grid: {
                    display: false 
                },
            }
        },
        plugins: {
            tooltip: {
                callbacks: {
                    label: function(tooltipItem) {
                        const value = tooltipItem.raw;
                        return `Hours Worked: ${Math.floor(value / 3600)}h ${Math.floor((value % 3600) / 60)}m ${value % 60}s`;
                    },
                    title: function(tooltipItems) {
                        return tooltipItems[0].label; // Display label of the hovered bar
                    }
                }
            }
        }
    }
});

// Function to fetch data and update the chart goes here...

// Function to fetch data from the server based on the selected timeframe
async function fetchData(timeframe) {
   

        try {
            const response = await fetch(`/app/attendance/${timeframe}`);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            if (timeframe=="day") {
                const totalTime = data.total_time;     
                // Update the h2 element with the received total time
                const formattedTime = `${totalTime.hours}h ${totalTime.minutes}m ${totalTime.seconds}s`;
                document.getElementById('worked-time').textContent = ` Worked Hours: ${formattedTime}`; 
                updateChart(data.labels, data.data);
            }
            else{
                if(timeframe=="week") {
                    values = Object.values(data).map(value => Math.floor(value));
                    labels =['M','T','W','T','F','S','S'];
                    updateChart(labels, values);
                    const totalSeconds = values.reduce((total, seconds) => total + seconds, 0);
                const hours = Math.floor(totalSeconds / 3600);

                const minutes = Math.floor((totalSeconds % 3600) / 60);
                const seconds = totalSeconds % 60;
                const formattedTime = `${hours}h ${minutes}m ${seconds}s`;
                document.getElementById('worked-time').textContent = ` Worked Hours: ${formattedTime}`; 
                console.log(totalSeconds)
                    
                }
                else if (timeframe=="month") {
                    const labels = data.labels
                    const values =data.values.map(value => Math.floor(value))
                    
                    updateChart(labels, values);
                    const totalSeconds = values.reduce((total, seconds) => total + seconds, 0);
                const hours = Math.floor(totalSeconds / 3600);

                const minutes = Math.floor((totalSeconds % 3600) / 60);
                const seconds = totalSeconds % 60;
                const formattedTime = `${hours}h ${minutes}m ${seconds}s`;
                document.getElementById('worked-time').textContent = ` Worked Hours: ${formattedTime}`; 
                console.log(totalSeconds)
                  
                }
                
                
            } 
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }
    
// }

// Function to update the chart with fetched data
function updateChart(labels, data) {
    const maxData = Math.max(...data);
    let maxScale;

    // Determine y-axis scale max based on max data value
    if (maxData < 60) {
        maxScale = 60;  // Seconds scale max
    } else if (maxData < 3600) {
        maxScale = 3600;  // Minutes scale max (60m)
    } else if (maxData < 43200) {
        maxScale = 43200;  // Hours scale max (12h)
    } else {
        maxScale = 86400;  // Extended hour scale max (24h)
    }

    myChart.data.labels = labels;
    myChart.data.datasets[0].data = data;
    myChart.options.scales.y.max = maxScale;  // Set max based on calculated value
    myChart.update();
}

// Event Listeners for Buttons
document.addEventListener("DOMContentLoaded", function() {
    const dayBtn = document.getElementById("day-btn");
    const weekBtn = document.getElementById("week-btn");
    const monthBtn = document.getElementById("month-btn");
    setActiveButton(dayBtn);
    fetchData('day');

    dayBtn.addEventListener("click", function() {
        setActiveButton(dayBtn);
        fetchData('day');
    });

    weekBtn.addEventListener("click", function() {
        setActiveButton(weekBtn);
        fetchData('week');
    });

    monthBtn.addEventListener("click", function() {
        setActiveButton(monthBtn);
        fetchData('month');
    });
});

// Set active button styling
function setActiveButton(button) {
    const buttons = [document.getElementById("day-btn"), document.getElementById("week-btn"), document.getElementById("month-btn")];
    buttons.forEach(btn => {
        btn.classList.remove("active");
    });
    button.classList.add("active");
}

async function fetchTimerData() {
    try {
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const response = await fetch(`http://127.0.0.1:8080/app/timer_info/`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}




