
let startTime, timerInterval;

function startTimer() {
    startTime = Date.now();
    timerInterval = setInterval(() => {
        let elapsed = Date.now() - startTime;
        document.getElementById("timer").textContent = formatTime(elapsed);
    }, 1000);
}

function stopTimer() {
    clearInterval(timerInterval);
}

function resetTimer() {
    clearInterval(timerInterval);
    document.getElementById("timer").textContent = "00:00:00";
}

function formatTime(ms) {
    let totalSeconds = Math.floor(ms / 1000);
    let hours = String(Math.floor(totalSeconds / 3600)).padStart(2, '0');
    let minutes = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, '0');
    let seconds = String(totalSeconds % 60).padStart(2, '0');
    return `${hours}:${minutes}:${seconds}`;
}
