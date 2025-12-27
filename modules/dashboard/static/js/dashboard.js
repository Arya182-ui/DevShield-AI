// static/js/dashboard.js
// Handles dashboard interactivity: fetches metrics, renders charts and activity feed.

// Fetch all events and update dashboard with filters
let allEvents = [];
async function loadMetrics() {
  // Fetch all events for filtering
  const eventsRes = await fetch('/api/events');
  allEvents = await eventsRes.json();
  applyFilters();
  // Update header date
  const dateSpan = document.getElementById('header-date');
  if (dateSpan) {
    const now = new Date();
    dateSpan.textContent = now.toLocaleString();
  }
}

function applyFilters() {
  // Get filter values
  const dateStart = document.getElementById('filter-date-start').value;
  const dateEnd = document.getElementById('filter-date-end').value;
  const type = document.getElementById('filter-type').value;
  const riskMin = parseInt(document.getElementById('filter-risk-min').value) || 0;
  const riskMax = parseInt(document.getElementById('filter-risk-max').value) || 100;

  let filtered = allEvents.filter(ev => {
    let ok = true;
    if (dateStart) ok = ok && ev.timestamp >= dateStart;
    if (dateEnd) ok = ok && ev.timestamp <= dateEnd + 'T23:59:59';
    if (type) ok = ok && ev.secret_type === type;
    if (ev.risk_score !== undefined) ok = ok && ev.risk_score >= riskMin && ev.risk_score <= riskMax;
    return ok;
  });

  // Update metrics
  const totalBlocked = filtered.filter(ev => ev.action === 'block').length;
  document.getElementById('total-blocked').textContent = totalBlocked;

  // Type breakdown
  const typeList = document.getElementById('type-breakdown');
  typeList.innerHTML = '';
  const typeCounts = {};
  filtered.forEach(ev => { typeCounts[ev.secret_type] = (typeCounts[ev.secret_type] || 0) + 1; });
  for (const [type, count] of Object.entries(typeCounts)) {
    const li = document.createElement('li');
    li.textContent = `${type}: ${count}`;
    typeList.appendChild(li);
  }

  // Risk scores
  const riskScores = filtered.map(ev => ev.risk_score).filter(x => typeof x === 'number');
  renderRiskChart(riskScores);

  // Activity feed
  renderActivityFeed(filtered.sort((a, b) => b.timestamp.localeCompare(a.timestamp)));
}

// Filter button listeners
window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('filter-apply').onclick = applyFilters;
  document.getElementById('filter-reset').onclick = function() {
    document.getElementById('filter-date-start').value = '';
    document.getElementById('filter-date-end').value = '';
    document.getElementById('filter-type').value = '';
    document.getElementById('filter-risk-min').value = '';
    document.getElementById('filter-risk-max').value = '';
    applyFilters();
  };
});

// Render risk score chart using Chart.js
let riskChartInstance = null;
function renderRiskChart(scores) {
  const ctx = document.getElementById('riskChart').getContext('2d');
  if (riskChartInstance) {
    riskChartInstance.destroy();
  }
  const isDark = document.body.classList.contains('dark-mode');
  riskChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: scores.map((_, i) => `#${i + 1}`),
      datasets: [{
        label: 'Risk Score',
        data: scores,
        backgroundColor: isDark ? '#00b894' : '#2980b9',
        borderRadius: 8,
        maxBarThickness: 32,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: { enabled: true }
      },
      layout: {
        padding: { top: 40, bottom: 16, left: 8, right: 8 }
      },
      scales: {
        x: {
          ticks: { color: isDark ? '#e0e6ef' : '#2c3e50', padding: 4 },
          grid: { display: false }
        },
        y: {
          beginAtZero: true,
          max: 100,
          grace: '10%',
          title: { display: true, text: 'Risk Score', color: isDark ? '#e0e6ef' : '#2c3e50' },
          ticks: {
            color: isDark ? '#e0e6ef' : '#2c3e50',
            padding: 12,
            callback: function(value) { return value; }
          },
          grid: { color: isDark ? '#444a5a' : '#e0e6ef' }
        }
      }
    }
  });
}

// Render activity feed with subtle animation
function renderActivityFeed(events) {
  const feed = document.getElementById('activity-feed');
  feed.innerHTML = '';
  events.forEach(event => {
    const li = document.createElement('li');
    li.innerHTML = `<b>[${event.action.toUpperCase()}]</b> ${event.secret_type} (Risk: ${event.risk_score})<br><small>${event.timestamp}</small><br>${event.details}`;
    li.style.animation = 'fadeInUp 0.7s';
    feed.appendChild(li);
  });
}

// Dark/Light mode toggle
const modeToggle = document.getElementById('mode-toggle');
if (modeToggle) {
  modeToggle.onclick = function () {
    const isDark = document.body.classList.toggle('dark-mode');
    modeToggle.textContent = isDark ? '☀️ Light Mode' : '🌙 Dark Mode';
    // Re-render chart for new mode
    applyFilters();
  };
}

// Improved chart visuals: use contrasting bar color in dark mode
function getBarColor() {
  return document.body.classList.contains('dark-mode') ? '#00b894' : '#2980b9';
}

function renderRiskChart(scores) {
  const canvas = document.getElementById('riskChart');
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.font = '13px Arial';
  ctx.textAlign = 'center';
  const barWidth = 20;
  const gap = 10;
  scores.forEach((score, i) => {
    const x = i * (barWidth + gap) + 25;
    const y = canvas.height - (score * canvas.height / 100);
    ctx.fillStyle = getBarColor();
    ctx.fillRect(x, y, barWidth, canvas.height - y);
    ctx.fillStyle = document.body.classList.contains('dark-mode') ? '#fff' : '#555';
    ctx.fillText(score, x + barWidth / 2, y - 6);
  });
}

// Initial load
window.onload = loadMetrics;
