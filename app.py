
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# DEMO DATA ONLY.
# These prices, departure times and journey durations are simulated.
# They are not live travel offers.

SAMPLE_OPTIONS = {
    "flight": [
        {
            "mode": "Flight",
            "provider": "SkyWays Demo",
            "route": "{origin} → Bengaluru → {destination}",
            "duration": 5.4,
            "cost": 6800,
            "departure": "14:30",
            "reliability": 4,
            "note": "One connection; allow enough time for the transfer."
        },
        {
            "mode": "Train",
            "provider": "RailConnect Demo",
            "route": "{origin} → Bengaluru → {destination}",
            "duration": 18,
            "cost": 1850,
            "departure": "16:00",
            "reliability": 3,
            "note": "Lower-cost alternative, but the journey takes longer."
        },
        {
            "mode": "Bus + Train",
            "provider": "RouteMix Demo",
            "route": "{origin} → Bengaluru by bus, then train",
            "duration": 20,
            "cost": 1450,
            "departure": "15:15",
            "reliability": 2,
            "note": "Budget option with a transfer; verify connection times."
        }
    ],

    "train": [
        {
            "mode": "Bus",
            "provider": "CoastLine Demo",
            "route": "{origin} → {destination} by road",
            "duration": 7.5,
            "cost": 950,
            "departure": "15:00",
            "reliability": 3,
            "note": "Road alternative; traffic may change journey time."
        },
        {
            "mode": "Train",
            "provider": "RailConnect Demo",
            "route": "Alternative train: {origin} → {destination}",
            "duration": 8.5,
            "cost": 720,
            "departure": "18:30",
            "reliability": 3,
            "note": "Sample schedule only; check the operator before booking."
        },
        {
            "mode": "Flight",
            "provider": "SkyWays Demo",
            "route": "{origin} → {destination}",
            "duration": 1.1,
            "cost": 4200,
            "departure": "17:10",
            "reliability": 4,
            "note": "Fast alternative; airport and check-in time are excluded."
        }
    ],

    "hotel": [
        {
            "mode": "Hotel",
            "provider": "Harbour Stay Demo",
            "route": "Alternative accommodation in {destination}",
            "duration": 0,
            "cost": 2200,
            "departure": "Check-in today",
            "reliability": 4,
            "note": "Sample nightly rate; confirm availability and cancellation terms."
        },
        {
            "mode": "Hotel",
            "provider": "Budget Nest Demo",
            "route": "Budget accommodation in {destination}",
            "duration": 0,
            "cost": 1250,
            "departure": "Check-in today",
            "reliability": 3,
            "note": "Lower-cost sample option; verify location and amenities."
        },
        {
            "mode": "Hotel",
            "provider": "City Comfort Demo",
            "route": "Accommodation near the transit hub in {destination}",
            "duration": 0,
            "cost": 3100,
            "departure": "Check-in today",
            "reliability": 4,
            "note": "Convenient for onward travel; sample price only."
        }
    ]
}


def rank_options(kind, budget, max_extra_hours, priority,
                 origin, destination):
    """Rank simulated alternatives against the user's preferences."""

    ranked = []

    for item in SAMPLE_OPTIONS[kind]:
        option = item.copy()

        # Insert the user's chosen locations.
        option["route"] = (
            option["route"]
            .replace("{origin}", origin)
            .replace("{destination}", destination)
        )

        cost = option["cost"]
        duration = option["duration"]
        reliability = option["reliability"]

        # Check the user's limits.
        within_budget = cost <= budget
        within_time = (
            True if kind == "hotel"
            else duration <= max_extra_hours
        )

        # Give every option a score from 0 to 100.
        # Lower price, shorter duration and higher reliability
        # are rewarded according to the selected priority.
        cost_score = max(0, 100 * (1 - cost / max(budget, cost)))

        time_score = (
            100 if kind == "hotel"
            else max(
                0,
                100 * (
                    1 - duration /
                    max(max_extra_hours, duration, 0.5)
                )
            )
        )

        reliability_score = reliability * 25

        if priority == "cheapest":
            score = (
                0.65 * cost_score
                + 0.15 * time_score
                + 0.20 * reliability_score
            )
        elif priority == "fastest":
            score = (
                0.15 * cost_score
                + 0.65 * time_score
                + 0.20 * reliability_score
            )
        elif priority == "reliable":
            score = (
                0.15 * cost_score
                + 0.15 * time_score
                + 0.70 * reliability_score
            )
        else:
            score = (
                0.40 * cost_score
                + 0.40 * time_score
                + 0.20 * reliability_score
            )

        # Penalise alternatives that exceed the user's limits.
        if not within_budget:
            score -= min(
                60,
                ((cost - budget) / max(budget, 1)) * 30
            )

        if not within_time:
            score -= min(
                60,
                (duration - max_extra_hours) * 4
            )

        option["within_budget"] = within_budget
        option["within_time"] = within_time
        option["score"] = round(score, 2)
        option["cost_display"] = f"₹{cost:,}"
        option["duration_display"] = (
            f"{duration:g} h" if kind != "hotel" else "N/A"
        )

        ranked.append(option)

    # Highest score appears first.
    return sorted(
        ranked,
        key=lambda option: option["score"],
        reverse=True
    )


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/api/recovery")
def recovery():
    payload = request.get_json(silent=True) or request.form

    # Read the selected disruption type.
    kind = str(payload.get("disruption_type", "flight")).lower().strip()

    if kind not in SAMPLE_OPTIONS:
        return jsonify({
            "error": "Please choose flight, train or hotel."
        }), 400

    try:
        budget = float(payload.get("budget", 5000))
        max_extra_hours = float(
            payload.get("max_extra_hours", 12)
        )
    except (TypeError, ValueError):
        return jsonify({
            "error": "Enter valid numbers for budget and journey time."
        }), 400

    if budget < 1:
        return jsonify({
            "error": "Budget must be at least ₹1."
        }), 400

    if max_extra_hours < 0:
        return jsonify({
            "error": "Journey time cannot be negative."
        }), 400

    priority = str(
        payload.get("priority", "balanced")
    ).lower().strip()

    if priority not in {
        "balanced", "cheapest", "fastest", "reliable"
    }:
        priority = "balanced"

    origin = str(
        payload.get("origin", "Mangalore")
    ).strip()[:80]

    destination = str(
        payload.get("destination", "Dubai")
    ).strip()[:80]

    disruption = str(
        payload.get(
            "disruption",
            "Service delayed by 3 hours"
        )
    ).strip()[:120]

    origin = origin or "your origin"
    destination = destination or "your destination"
    disruption = disruption or "Travel disruption reported"

    options = rank_options(
        kind,
        budget,
        max_extra_hours,
        priority,
        origin,
        destination
    )

    best = options[0]

    itinerary = [
        {
            "time": "Now",
            "title": "Confirm the disruption",
            "description": (
                f"Check the official operator notice for: "
                f"{disruption}. This prototype uses simulated scenarios."
            )
        },
        {
            "time": "Next",
            "title": "Check your existing booking",
            "description": (
                "Review refund, cancellation, baggage and rebooking "
                "conditions before paying for an alternative."
            )
        },
        {
            "time": "Recommended",
            "title": f"Evaluate {best['provider']}",
            "description": (
                f"{best['route']}. Sample cost: "
                f"{best['cost_display']}; journey time: "
                f"{best['duration_display']}. {best['note']}"
            )
        },
        {
            "time": "Before booking",
            "title": "Verify the alternative",
            "description": (
                "Confirm live availability, exact timings, final price "
                "and transfer risks with the official provider. "
                "This prototype does not make bookings."
            )
        }
    ]

    has_feasible_option = any(
        option["within_budget"] and option["within_time"]
        for option in options
    )

    if not has_feasible_option and kind != "hotel":
        notice = (
            "No sample alternative meets both your budget and time "
            "limits. Consider adjusting your limits or checking "
            "other providers."
        )
    else:
        notice = (
            "Demo mode: providers, prices and schedules are simulated, "
            "not live offers."
        )

    return jsonify({
        "title": f"Recovery plan: {origin} → {destination}",
        "kind": kind,
        "disruption": disruption,
        "priority": priority,
        "budget": budget,
        "max_extra_hours": max_extra_hours,
        "options": options,
        "itinerary": itinerary,
        "notice": notice,
        "generated_at": datetime.now().strftime("%d %b %Y, %H:%M")
    })


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "app": "TripRescue MVP"
    })


if __name__ == "__main__":
    app.run(debug=True)
