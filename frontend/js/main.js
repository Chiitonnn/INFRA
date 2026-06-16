document.addEventListener('DOMContentLoaded', function () {
    fetchStats();
});

async function fetchStats() {
    try {
        const response = await fetch('http://192.168.10.10:8000/biens/');
        const data = await response.json();
        document.getElementById('biens-count').textContent = data.length || 0;
        document.getElementById('transactions-count').textContent = data.length || 0;
    } catch (error) {
        console.log('API indisponible');
    }
}