# TripRescue — DevHack 2026 MVP

TripRescue is a web prototype for **PS 4.1: AI Agent for Travel Disruption Recovery**. It demonstrates how a traveller can enter a disruption, set a budget/time limit, compare alternative options and receive a recovery checklist.

## Important demo limitation

This MVP uses **simulated transport options, providers, times and prices**. It does not access live flight/train/hotel inventory, real bookings, or make reservations. The ranking is an explainable, rule-based scoring heuristic, not a trained AI/ML model. Clearly explain this during your demo.

## Features

- Responsive travel-recovery UI
- Flight, train and hotel disruption scenarios
- User-entered origin, destination, budget, time limit and priority
- Python Flask API (`POST /api/recovery`)
- Ranked options with budget/time flags
- Recovery action plan and transparent data notice
- Health endpoint (`GET /health`)

## Run locally (Windows)

1. Install Python 3.10 or newer.
2. Open this folder in VS Code.
3. In the terminal, create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   ```

4. Install requirements:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Start the app:

   ```powershell
   python app.py
   ```

6. Open `http://127.0.0.1:5000` in your browser.

## API example

```bash
curl -X POST http://127.0.0.1:5000/api/recovery \
  -H "Content-Type: application/json" \
  -d '{"disruption_type":"flight","origin":"Mangalore","destination":"Delhi","disruption":"Flight cancelled unexpectedly","budget":5000,"max_extra_hours":12,"priority":"balanced"}'
```

## Suggested four-minute demo

1. **0:00–0:30:** Explain the problem: travel disruptions force travellers to search multiple places under time pressure.
2. **0:30–1:00:** Enter a cancelled flight, route, budget and time limit.
3. **1:00–2:00:** Generate the plan and explain why the options are ranked.
4. **2:00–3:00:** Change the priority to “Lowest cost” and generate again.
5. **3:00–3:35:** Show the recovery action plan and the transparent simulated-data notice.
6. **3:35–4:00:** Explain next steps: connect verified transport/hotel APIs, check booking policies, and add user-confirmed alerts.

## GitHub upload

Create a new repository on GitHub, then from this folder run:

```bash
git init
git add .
git commit -m "Build TripRescue travel recovery MVP"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Replace the remote URL with your own repository URL. Do not commit private API keys or passwords.

## Next-stage integrations (not implemented)

- A verified flight-search provider such as Amadeus for alternative flight offers. Check current API access, test-data limitations, terms and quota before use.
- A routing provider for travel-time alternatives where appropriate.
- Live disruption alerts from official transport providers, subject to available APIs and permitted use.
- User confirmation before any booking or cancellation action.

## References

- Flask Quickstart: https://flask.palletsprojects.com/en/stable/quickstart/
- Amadeus Self-Service API FAQ: https://admin.developers.amadeus.com/self-service/apis-docs/guides/developer-guides/faq/
- Google Routes API alternative routes: https://developers.google.com/maps/documentation/routes/alternative-routes
