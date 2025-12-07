const form = document.getElementById('predict-form');
const historicalEl = document.getElementById('historical');
const horizonEl = document.getElementById('horizon');
const errorEl = document.getElementById('error');
const exampleBtn = document.getElementById('example-btn');

let chart = null;

function showError(msg){ errorEl.textContent = msg; errorEl.classList.remove('hidden'); }
function clearError(){ errorEl.classList.add('hidden'); errorEl.textContent = ''; }

if(exampleBtn){
  exampleBtn.addEventListener('click', ()=>{
    historicalEl.value = '45,56';
    horizonEl.value = '24';
  });
}

form.addEventListener('submit', async (e)=>{
  e.preventDefault();
  clearError();
  let raw = historicalEl.value.trim();
  if(!raw){ showError('Enter at least one historical temperature'); return; }
  let arr = raw.split(',').map(s=>parseFloat(s.trim())).filter(x=>!Number.isNaN(x));
  if(arr.length===0){ showError('Could not parse numbers from input'); return; }
  let horizon = parseInt(horizonEl.value) || 24;

  try{
    const res = await fetch('/predict', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ historical_temps: arr, prediction_length: horizon })
    });

    if(!res.ok){ const tx = await res.text(); throw new Error(tx||res.statusText); }

    const data = await res.json();
    renderChart(arr, data.forecast);
  }catch(err){ showError(err.message); }
});

function renderChart(history, forecastSamples){
  // forecastSamples is an array of sample trajectories; compute median and bands
  const samples = forecastSamples; // [num_samples][horizon]
  const horizon = samples[0].length;

  // compute median and percentiles
  const med = []; const p10 = []; const p90 = [];
  for(let t=0;t<horizon;t++){
    const vals = samples.map(s=>s[t]);
    vals.sort((a,b)=>a-b);
    const mid = vals[Math.floor(vals.length/2)];
    med.push(mid);
    p10.push(vals[Math.floor(vals.length*0.1)]);
    p90.push(vals[Math.floor(vals.length*0.9)]);
  }

  // x labels: history indices + future steps
  const labels = [];
  for(let i=0;i<history.length;i++) labels.push('t-' + (history.length - i));
  for(let i=1;i<=horizon;i++) labels.push('t+' + i);

  const historyDataset = {
    label: 'History',
    data: [...history, ...Array(horizon).fill(null)],
    borderColor: '#111827',
    backgroundColor: '#111827',
    tension: 0.2,
    pointRadius: 3,
  };

  const medianDataset = {
    label: 'Median Forecast',
    data: [...Array(history.length).fill(null), ...med],
    borderColor: '#2563eb',
    backgroundColor: '#2563eb',
    tension: 0.2,
    pointRadius: 2,
  };

  const bandDataset = {
    label: '10-90% band',
    data: [...Array(history.length).fill(null), ...p90],
    borderColor: 'transparent',
    backgroundColor: 'rgba(37,99,235,0.12)',
    fill: '+1',
  };

  const lowerBandDataset = {
    label: 'lower',
    data: [...Array(history.length).fill(null), ...p10],
    borderColor: 'transparent',
    backgroundColor: 'rgba(0,0,0,0)',
    fill: false,
  };

  const datasets = [historyDataset, medianDataset, bandDataset, lowerBandDataset];

  const ctx = document.getElementById('forecastChart').getContext('2d');
  if(chart) chart.destroy();
  chart = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      plugins: { legend: { position: 'top' } },
      scales: { y: { title: { display: true, text: 'Temperature' } } }
    }
  });
}
