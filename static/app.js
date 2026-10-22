const form = document.querySelector('#recovery-form');
const results = document.querySelector('#results');
const toast = document.querySelector('#toast');
const typeRadios = [...document.querySelectorAll('input[name="disruption_type"]')];

typeRadios.forEach(radio => radio.addEventListener('change', () => {
  document.querySelectorAll('.choice').forEach(label => label.classList.toggle('active', label.querySelector('input').checked));
  const disruption = document.querySelector('#disruption');
  if (radio.value === 'flight' && radio.checked) disruption.value = 'Service delayed by 3 hours';
  if (radio.value === 'train' && radio.checked) disruption.value = 'Train service cancelled';
  if (radio.value === 'hotel' && radio.checked) disruption.value = 'Hotel booking unavailable on arrival';
}));

function showToast(message) {
  toast.textContent = message; toast.classList.add('show');
  window.setTimeout(() => toast.classList.remove('show'), 2600);
}
function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
}
function renderOption(option, index) {
  return `<article class="option-card ${index === 0 ? 'recommended' : ''}">
    <div class="option-top"><div><div class="option-name">${escapeHTML(option.mode)} · ${escapeHTML(option.provider)}</div><div class="option-provider">${escapeHTML(option.departure)}</div></div>${index === 0 ? '<span class="recommend-tag">TOP MATCH</span>' : ''}</div>
    <div class="option-route">${escapeHTML(option.route)}</div>
    <div class="option-metrics"><span class="metric">₹ ${escapeHTML(option.cost.toLocaleString('en-IN'))}</span><span class="metric">Duration: ${escapeHTML(option.duration_display)}</span><span class="metric">Reliability: ${option.reliability}/5</span></div>
    <div class="flag ${option.within_budget && option.within_time ? 'good' : ''}">${option.within_budget ? '✓ Within budget' : '⚠ Above budget'}${option.within_time ? ' · Within time limit' : ' · Exceeds time limit'}</div>
    <p class="option-note">${escapeHTML(option.note)}</p></article>`;
}
function renderItinerary(item) {
  return `<article class="timeline-card"><div class="timeline-time">${escapeHTML(item.time)}</div><div><h4>${escapeHTML(item.title)}</h4><p>${escapeHTML(item.description)}</p></div></article>`;
}
form.addEventListener('submit', async event => {
  event.preventDefault();
  const button = form.querySelector('button[type="submit"]');
  const original = button.innerHTML;
  button.disabled = true; button.innerHTML = '<span>Building recovery plan…</span><span>↻</span>';
  const payload = Object.fromEntries(new FormData(form).entries());
  try {
    const response = await fetch('/api/recovery', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Unable to create a recovery plan.');
    document.querySelector('#result-title').textContent = data.title;
    document.querySelector('#result-subtitle').textContent = `Generated ${data.generated_at} · ${data.kind.toUpperCase()} disruption`;
    document.querySelector('#notice').textContent = data.notice;
    document.querySelector('#options-list').innerHTML = data.options.map(renderOption).join('');
    document.querySelector('#itinerary-list').innerHTML = data.itinerary.map(renderItinerary).join('');
    results.classList.remove('hidden');
    loadLiveFlights(payload.origin, payload.destination);
    results.scrollIntoView({behavior:'smooth', block:'start'});
    showToast('Your recovery plan is ready. Verify details before booking.');
  } catch (error) {
    showToast(error.message || 'Something went wrong. Please try again.');
  } finally {
    button.disabled = false; button.innerHTML = original;
  }
});
document.querySelector('#reset-button').addEventListener('click', () => {
  results.classList.add('hidden'); form.scrollIntoView({behavior:'smooth', block:'start'});
});
async function loadLiveFlights(origin, destination) {
  const message = document.querySelector('#flight-status-message');
  const list = document.querySelector('#flight-status-list');

  if (!message || !list) return;

  const departure = origin || document.querySelector('#origin').value;
  const arrival = destination || document.querySelector('#destination').value;

  message.textContent = 'Loading live flight information...';
  list.innerHTML = '';

  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 20000);

  try {
    const params = new URLSearchParams({dep_location: departure, arr_location: arrival});
    const response = await fetch(
      `/api/live-flights?${params}`,
      { signal: controller.signal }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Could not load flights.');
    }

    const flights = data.flights || [];

    if (flights.length === 0) {
      message.textContent = 'No matching flights were found.';
      return;
    }

    message.textContent =
      `Showing ${flights.length} flight(s) from ${data.departure} to ${data.arrival}.`;

    list.innerHTML = flights.map(flight => {
      const airline = flight.airline?.name || 'Unknown airline';
      const flightNumber = flight.flight?.iata || 'Flight number unavailable';
      const status = flight.flight_status || 'Status unavailable';
      const departure = flight.departure?.scheduled
        ? new Date(flight.departure.scheduled).toLocaleString()
        : 'Time unavailable';
      const arrival = flight.arrival?.scheduled
        ? new Date(flight.arrival.scheduled).toLocaleString()
        : 'Time unavailable';

      const card = document.createElement('article');
      card.className = 'option-card';
      card.textContent =
        `${airline} — ${flightNumber} | Status: ${status} | ` +
        `Departure: ${departure} | Arrival: ${arrival}`;

      return card.outerHTML;
    }).join('');

  } catch (error) {
    message.textContent =
      error.name === 'AbortError'
        ? 'Flight information is taking too long to load. Please try again.'
        : (error.message || 'Unable to load flight information. Please try again later.');
    console.error('Flight status error:', error);
  } finally {
    window.clearTimeout(timeout);
  }
}

loadLiveFlights();
