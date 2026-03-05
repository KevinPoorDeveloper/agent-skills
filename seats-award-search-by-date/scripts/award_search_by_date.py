#!/usr/bin/env python3
"""seats-award-search-by-date: Comprehensive day-by-day award flight availability search.

Searches ALL mileage programs for one origin and multiple destinations over a date range.
Generates HTML dashboard with calendar heatmaps, availability tables, program comparison cards.
Optionally generates 4K infographic via Venice.ai.
"""

import sys
import os
import json
import argparse
import time
import shutil
import base64
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from _seats_aero_lib.api import SeatsAeroAPI, MILEAGE_PROGRAMS, CABIN_CLASSES, PROGRAM_CODES, validate_date, save_json

try:
    import requests
except ImportError:
    print("ERROR: requests library required. Install with: pip install requests")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def safe_int(v):
    """Safely cast a value to int, returning 0 on failure."""
    if v is None:
        return 0
    try:
        return int(v)
    except (ValueError, TypeError):
        return 0


def safe_float(v):
    """Safely cast a value to float, returning 0.0 on failure."""
    if v is None:
        return 0.0
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0.0


def format_miles(v):
    """Format miles with comma separator, or dash if unavailable."""
    n = safe_int(v)
    if n <= 0:
        return "\u2014"
    return "{:,}".format(n)


def date_range(start_str, end_str):
    """Generate list of date strings from start to end inclusive."""
    start = datetime.strptime(start_str, "%Y-%m-%d")
    end = datetime.strptime(end_str, "%Y-%m-%d")
    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return dates


def cabin_prefix(cabin):
    """Map cabin name to field prefix."""
    mapping = {"economy": "Y", "premium": "W", "business": "J", "first": "F"}
    return mapping.get(cabin.lower(), "J")


def cabin_display(prefix):
    """Map field prefix to display name."""
    mapping = {"Y": "Economy", "W": "Premium Econ", "J": "Business", "F": "First"}
    return mapping.get(prefix, prefix)


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------

def collect_availability(api, origin, destinations, dates, source=None):
    """Query API for each day x destination combination. Returns list of records."""
    all_records = []
    total_calls = len(dates) * len(destinations)
    call_num = 0
    errors = []

    for dest in destinations:
        for ds in dates:
            call_num += 1
            sys.stdout.write("  [{c}/{t}] {o}->{d} on {s} ...".format(
                c=call_num, t=total_calls, o=origin, d=dest, s=ds))
            sys.stdout.flush()

            try:
                result = api.cached_search(
                    origin=origin,
                    destination=dest,
                    start_date=ds,
                    end_date=ds,
                    take=1000,
                    source=source
                )
                data = result.get("data", [])
                count = len(data)
                for rec in data:
                    rec["_queried_dest"] = dest
                all_records.extend(data)
                print(" -> {c} records".format(c=count))
            except Exception as e:
                err_msg = "{d} {s}: {e}".format(d=dest, s=ds, e=str(e))
                errors.append(err_msg)
                print(" -> ERROR: {e}".format(e=str(e)))

            time.sleep(0.5)

    print("\nCollection complete: {n} records, {e} errors, {c} API calls".format(
        n=len(all_records), e=len(errors), c=call_num))
    return all_records, errors


# ---------------------------------------------------------------------------
# Data analysis
# ---------------------------------------------------------------------------

def analyze_data(records, destinations, dates, highlight_cabin):
    """Analyze collected records into structured summary data."""
    analysis = {
        "total_records": len(records),
        "destinations": {},
        "programs": {},
        "by_date_dest": defaultdict(list),
        "insights": [],
    }

    for dest in destinations:
        analysis["destinations"][dest] = {
            "total_days": len(dates),
            "avail_days": set(),
            "best_Y": None, "best_Y_prog": "",
            "best_W": None, "best_W_prog": "",
            "best_J": None, "best_J_prog": "",
            "best_F": None, "best_F_prog": "",
            "programs_seen": set(),
        }

    for rec in records:
        dest = rec.get("_queried_dest", "")
        rec_date = rec.get("Date", rec.get("ParsedDate", ""))
        if rec_date and len(rec_date) >= 10:
            rec_date = rec_date[:10]
        source_prog = rec.get("Source", "unknown")

        key = rec_date + "_" + dest
        analysis["by_date_dest"][key].append(rec)

        if source_prog not in analysis["programs"]:
            analysis["programs"][source_prog] = {
                "days": set(), "destinations": set(),
                "best_Y": None, "best_W": None, "best_J": None, "best_F": None,
                "worst_Y": None, "worst_W": None, "worst_J": None, "worst_F": None,
                "record_count": 0
            }

        if dest in analysis["destinations"]:
            da = analysis["destinations"][dest]
            da["avail_days"].add(rec_date)
            da["programs_seen"].add(source_prog)

            for pfx in ["Y", "W", "J", "F"]:
                avail = rec.get(pfx + "Available", False)
                cost = safe_int(rec.get(pfx + "MileageCost", 0))
                if avail and cost > 0:
                    bkey = "best_" + pfx
                    pkey = "best_" + pfx + "_prog"
                    if da[bkey] is None or cost < da[bkey]:
                        da[bkey] = cost
                        da[pkey] = source_prog

        pa = analysis["programs"][source_prog]
        pa["days"].add(rec_date)
        pa["destinations"].add(dest)
        pa["record_count"] += 1

        for pfx in ["Y", "W", "J", "F"]:
            avail = rec.get(pfx + "Available", False)
            cost = safe_int(rec.get(pfx + "MileageCost", 0))
            if avail and cost > 0:
                best_key = "best_" + pfx
                worst_key = "worst_" + pfx
                if pa[best_key] is None or cost < pa[best_key]:
                    pa[best_key] = cost
                if pa[worst_key] is None or cost > pa[worst_key]:
                    pa[worst_key] = cost

    # Generate insights
    insights = []

    for pfx, cname in [("Y", "Economy"), ("W", "Premium Economy"), ("J", "Business"), ("F", "First")]:
        best_cost = None
        best_prog = ""
        best_dest = ""
        for dest in destinations:
            da = analysis["destinations"][dest]
            val = da.get("best_" + pfx)
            if val is not None and (best_cost is None or val < best_cost):
                best_cost = val
                best_prog = da.get("best_" + pfx + "_prog", "")
                best_dest = dest
        if best_cost is not None:
            insights.append("Best {cabin}: {prog} at {cost} miles to {dest}".format(
                cabin=cname, prog=best_prog, cost="{:,}".format(best_cost), dest=best_dest))

    if analysis["programs"]:
        most_prog = max(analysis["programs"].items(), key=lambda x: len(x[1]["days"]))
        insights.append("Most available program: {name} with {n} days of availability".format(
            name=most_prog[0], n=len(most_prog[1]["days"])))

    for dest in destinations:
        da = analysis["destinations"][dest]
        avail_set = da["avail_days"]
        blackout = [d for d in dates if d not in avail_set]
        if blackout and len(blackout) <= 10:
            insights.append("{dest} blackout dates: {dates}".format(
                dest=dest, dates=", ".join(blackout)))
        elif blackout:
            insights.append("{dest}: {n} days with no availability out of {t}".format(
                dest=dest, n=len(blackout), t=len(dates)))

    all_progs = set()
    for dest in destinations:
        all_progs.update(analysis["destinations"][dest]["programs_seen"])
    insights.append("Total programs with availability: {n} ({progs})".format(
        n=len(all_progs), progs=", ".join(sorted(all_progs))))

    analysis["insights"] = insights

    # Convert sets to sorted lists for JSON serialization
    for dest in destinations:
        da = analysis["destinations"][dest]
        da["avail_days"] = sorted(list(da["avail_days"]))
        da["programs_seen"] = sorted(list(da["programs_seen"]))
    for prog in analysis["programs"]:
        pa = analysis["programs"][prog]
        pa["days"] = sorted(list(pa["days"]))
        pa["destinations"] = sorted(list(pa["destinations"]))

    return analysis


# ---------------------------------------------------------------------------
# HTML building blocks
# ---------------------------------------------------------------------------

def build_css():
    """Return the dashboard CSS as a single string."""
    return """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    background: #0a0a0a; color: #e0e0e0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    padding: 20px; line-height: 1.5;
}
.container { max-width: 1400px; margin: 0 auto; }
h1 { color: #00d4ff; font-size: 2em; margin-bottom: 5px; }
h2 { color: #00d4ff; font-size: 1.4em; margin: 30px 0 15px 0;
     border-bottom: 1px solid #333; padding-bottom: 8px; }
h3 { color: #ff6b35; font-size: 1.1em; margin: 15px 0 10px 0; }
.subtitle { color: #888; font-size: 0.95em; margin-bottom: 20px; }
.cards-row {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 15px; margin-bottom: 25px;
}
.card {
    background: #1a1a2e; border-radius: 10px; padding: 18px;
    border: 1px solid #2a2a4a;
}
.card-title { color: #00d4ff; font-size: 1.1em; font-weight: 600; margin-bottom: 10px; }
.card-stat { display: flex; justify-content: space-between; padding: 4px 0;
             border-bottom: 1px solid #1f1f3a; }
.card-stat:last-child { border-bottom: none; }
.stat-label { color: #888; }
.stat-value { color: #e0e0e0; font-weight: 500; }
.stat-value.good { color: #00e676; }
.stat-value.warn { color: #ff6b35; }
.calendar-grid { margin-bottom: 25px; }
.cal-month-title { color: #ccc; font-size: 1em; font-weight: 600; margin: 10px 0 5px 0; }
.cal-header { display: grid; grid-template-columns: repeat(7, 1fr); gap: 3px; margin-bottom: 3px; }
.cal-header div { text-align: center; color: #666; font-size: 0.75em; padding: 4px; }
.cal-body { display: grid; grid-template-columns: repeat(7, 1fr); gap: 3px; }
.cal-day {
    aspect-ratio: 1; border-radius: 6px; display: flex; flex-direction: column;
    align-items: center; justify-content: center; font-size: 0.75em;
    cursor: default; position: relative; min-height: 38px;
}
.cal-day.empty { background: transparent; }
.cal-day.no-data { background: #1a1a1a; color: #444; }
.cal-day.avail { background: #0a3d0a; color: #00e676; border: 1px solid #00e676; }
.cal-day.no-avail { background: #3d0a0a; color: #ff5252; border: 1px solid #ff5252; }
.cal-day .day-num { font-weight: 700; }
.cal-day .day-cost { font-size: 0.65em; opacity: 0.85; }
.cal-day:hover .tooltip { display: block; }
.tooltip {
    display: none; position: absolute; bottom: 105%; left: 50%;
    transform: translateX(-50%); background: #1a1a2e;
    border: 1px solid #00d4ff; border-radius: 6px; padding: 8px 12px;
    white-space: nowrap; z-index: 100; font-size: 0.85em; color: #e0e0e0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.5);
}
.tooltip div { padding: 2px 0; }
table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 0.85em; }
thead th {
    background: #1a1a2e; color: #00d4ff; padding: 10px 8px;
    text-align: left; cursor: pointer; user-select: none;
    border-bottom: 2px solid #00d4ff; position: sticky; top: 0;
}
thead th:hover { background: #2a2a4e; }
tbody tr { border-bottom: 1px solid #1f1f1f; }
tbody tr:hover { background: #151528; }
td { padding: 8px; }
td.avail-cell { color: #00e676; font-weight: 500; }
td.unavail-cell { color: #555; }
.insights-list { list-style: none; padding: 0; }
.insights-list li {
    padding: 8px 12px; margin: 5px 0; background: #1a1a2e;
    border-radius: 6px; border-left: 3px solid #00d4ff;
}
.prog-cards {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 12px; margin-bottom: 25px;
}
.prog-card {
    background: #1a1a2e; border-radius: 8px; padding: 14px;
    border: 1px solid #2a2a4a;
}
.prog-name { color: #ff6b35; font-weight: 700; font-size: 1.05em; margin-bottom: 8px; }
.filter-row { display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; align-items: center; }
.filter-row select, .filter-row input {
    background: #1a1a2e; color: #e0e0e0; border: 1px solid #333;
    border-radius: 6px; padding: 6px 10px; font-size: 0.9em;
}
.filter-row label { color: #888; font-size: 0.85em; }
@media (max-width: 768px) {
    .cards-row { grid-template-columns: 1fr; }
    .prog-cards { grid-template-columns: 1fr; }
}
"""


def build_js():
    """Return the dashboard JavaScript as a single string."""
    return """
function filterTable() {
    var destVal = document.getElementById('filterDest').value;
    var progVal = document.getElementById('filterProg').value;
    var rows = document.querySelectorAll('#availTable tbody tr');
    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        var dMatch = (destVal === 'all' || row.getAttribute('data-dest') === destVal);
        var pMatch = (progVal === 'all' || row.getAttribute('data-prog') === progVal);
        row.style.display = (dMatch && pMatch) ? '' : 'none';
    }
}
function sortTable(th) {
    var table = document.getElementById('availTable');
    var tbody = table.querySelector('tbody');
    var rows = Array.from(tbody.querySelectorAll('tr'));
    var idx = Array.from(th.parentNode.children).indexOf(th);
    var asc = th.getAttribute('data-sort') !== 'asc';
    th.setAttribute('data-sort', asc ? 'asc' : 'desc');
    var ths = th.parentNode.querySelectorAll('th');
    for (var i = 0; i < ths.length; i++) {
        if (ths[i] !== th) ths[i].removeAttribute('data-sort');
    }
    rows.sort(function(a, b) {
        var aText = a.children[idx] ? a.children[idx].textContent.replace(/,/g, '').trim() : '';
        var bText = b.children[idx] ? b.children[idx].textContent.replace(/,/g, '').trim() : '';
        var aNum = parseFloat(aText);
        var bNum = parseFloat(bText);
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return asc ? aNum - bNum : bNum - aNum;
        }
        if (aText === '\u2014' || aText === '') aText = asc ? '\uffff' : '';
        if (bText === '\u2014' || bText === '') bText = asc ? '\uffff' : '';
        return asc ? aText.localeCompare(bText) : bText.localeCompare(aText);
    });
    for (var i = 0; i < rows.length; i++) {
        tbody.appendChild(rows[i]);
    }
}
"""


# ---------------------------------------------------------------------------
# HTML dashboard generation
# ---------------------------------------------------------------------------

def generate_html(records, analysis, origin, destinations, dates, start_date, end_date, highlight_cabin):
    """Generate a self-contained dark-themed HTML dashboard."""
    hp = cabin_prefix(highlight_cabin)
    gen_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dest_str = ", ".join(destinations)

    parts = []

    # Head
    parts.append("<!DOCTYPE html>")
    parts.append('<html lang="en">')
    parts.append("<head>")
    parts.append('<meta charset="UTF-8">')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    parts.append("<title>Award Search: " + origin + " to " + dest_str + "</title>")
    parts.append("<style>")
    parts.append(build_css())
    parts.append("</style>")
    parts.append("</head>")
    parts.append("<body>")
    parts.append('<div class="container">')

    # Header
    parts.append("<h1>" + origin + " &#x2708; " + dest_str + "</h1>")
    parts.append('<div class="subtitle">' + start_date + " to " + end_date
                 + " &middot; Generated " + gen_time
                 + " &middot; " + str(analysis["total_records"]) + " total records</div>")

    # --- Summary Cards ---
    parts.append("<h2>Destination Summary</h2>")
    parts.append('<div class="cards-row">')
    for dest in destinations:
        da = analysis["destinations"][dest]
        avail_count = len(da["avail_days"])
        total_d = da["total_days"]
        prog_count = len(da["programs_seen"])
        cls = " good" if avail_count > total_d * 0.5 else " warn"

        parts.append('<div class="card">')
        parts.append('<div class="card-title">' + origin + " &rarr; " + dest + "</div>")

        parts.append('<div class="card-stat"><span class="stat-label">Availability</span>')
        parts.append('<span class="stat-value' + cls + '">' + str(avail_count) + "/" + str(total_d) + " days</span></div>")

        for pfx, cname in [("Y", "Best Economy"), ("W", "Best Premium"), ("J", "Best Business"), ("F", "Best First")]:
            val = da.get("best_" + pfx)
            prog = da.get("best_" + pfx + "_prog", "")
            parts.append('<div class="card-stat"><span class="stat-label">' + cname + "</span>")
            if val is not None:
                display = "{:,}".format(val) + " (" + prog + ")"
                parts.append('<span class="stat-value good">' + display + "</span></div>")
            else:
                parts.append('<span class="stat-value">&mdash;</span></div>')

        parts.append('<div class="card-stat"><span class="stat-label">Programs</span>')
        parts.append('<span class="stat-value">' + str(prog_count) + "</span></div>")
        parts.append("</div>")  # card
    parts.append("</div>")  # cards-row

    # --- Calendar Heatmaps ---
    parts.append("<h2>Calendar Heatmap (" + cabin_display(hp) + ")</h2>")

    for dest in destinations:
        parts.append("<h3>" + origin + " &rarr; " + dest + "</h3>")

        months = defaultdict(list)
        for ds in dates:
            months[ds[:7]].append(ds)

        for ym in sorted(months.keys()):
            month_dates = months[ym]
            dt_first = datetime.strptime(month_dates[0], "%Y-%m-%d")
            month_name = dt_first.strftime("%B %Y")
            parts.append('<div class="calendar-grid">')
            parts.append('<div class="cal-month-title">' + month_name + "</div>")

            parts.append('<div class="cal-header">')
            for wd in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
                parts.append("<div>" + wd + "</div>")
            parts.append("</div>")

            parts.append('<div class="cal-body">')

            first_of_month = datetime.strptime(ym + "-01", "%Y-%m-%d")
            weekday_start = first_of_month.weekday()
            for _ in range(weekday_start):
                parts.append('<div class="cal-day empty"></div>')

            if first_of_month.month == 12:
                last_of_month = datetime(first_of_month.year + 1, 1, 1) - timedelta(days=1)
            else:
                last_of_month = datetime(first_of_month.year, first_of_month.month + 1, 1) - timedelta(days=1)

            date_set = set(dates)
            day_num = 1
            while day_num <= last_of_month.day:
                ds = ym + "-" + str(day_num).zfill(2)
                key = ds + "_" + dest
                recs = analysis["by_date_dest"].get(key, [])

                if ds not in date_set or not recs:
                    parts.append('<div class="cal-day no-data"><span class="day-num">' + str(day_num) + "</span></div>")
                else:
                    best_cost = None
                    for r in recs:
                        avail = r.get(hp + "Available", False)
                        cost = safe_int(r.get(hp + "MileageCost", 0))
                        if avail and cost > 0:
                            if best_cost is None or cost < best_cost:
                                best_cost = cost

                    if best_cost is not None:
                        cost_k = str(best_cost // 1000) + "k"
                        day_cls = "avail"
                    else:
                        cost_k = "\u2014"
                        day_cls = "no-avail"

                    tt_lines = []
                    tt_lines.append("<div><strong>" + ds + "</strong></div>")
                    for r in recs:
                        prog = r.get("Source", "?")
                        items = []
                        for pfx, cn in [("Y", "Y"), ("W", "W"), ("J", "J"), ("F", "F")]:
                            av = r.get(pfx + "Available", False)
                            mc = safe_int(r.get(pfx + "MileageCost", 0))
                            if av and mc > 0:
                                items.append(cn + ":" + "{:,}".format(mc))
                        if items:
                            tt_lines.append("<div>" + prog + ": " + " | ".join(items) + "</div>")
                    tooltip_html = "".join(tt_lines)

                    parts.append('<div class="cal-day ' + day_cls + '">')
                    parts.append('<span class="day-num">' + str(day_num) + "</span>")
                    parts.append('<span class="day-cost">' + cost_k + "</span>")
                    parts.append('<div class="tooltip">' + tooltip_html + "</div>")
                    parts.append("</div>")

                day_num += 1

            parts.append("</div>")  # cal-body
            parts.append("</div>")  # calendar-grid

    # --- Detailed Availability Table ---
    parts.append("<h2>Detailed Availability</h2>")

    parts.append('<div class="filter-row">')
    parts.append("<label>Destination:</label>")
    parts.append('<select id="filterDest" onchange="filterTable()">')
    parts.append('<option value="all">All</option>')
    for dest in destinations:
        parts.append('<option value="' + dest + '">' + dest + "</option>")
    parts.append("</select>")
    parts.append("<label>Program:</label>")
    parts.append('<select id="filterProg" onchange="filterTable()">')
    parts.append('<option value="all">All</option>')
    all_progs = sorted(set(r.get("Source", "") for r in records))
    for prog in all_progs:
        parts.append('<option value="' + prog + '">' + prog + "</option>")
    parts.append("</select>")
    parts.append("</div>")

    parts.append('<div style="overflow-x:auto;">')
    parts.append('<table id="availTable">')
    parts.append("<thead><tr>")
    for col in ["Date", "Dest", "Program", "Economy", "Premium", "Business", "First", "Taxes", "Direct?"]:
        parts.append('<th onclick="sortTable(this)">' + col + "</th>")
    parts.append("</tr></thead>")
    parts.append("<tbody>")

    sorted_recs = sorted(records, key=lambda r: (
        (r.get("Date", r.get("ParsedDate", "")) or "")[:10],
        r.get("_queried_dest", ""),
        r.get("Source", "")
    ))

    for rec in sorted_recs:
        rec_date = rec.get("Date", rec.get("ParsedDate", ""))
        if rec_date and len(rec_date) >= 10:
            rec_date = rec_date[:10]
        dest = rec.get("_queried_dest", "")
        source = rec.get("Source", "")

        parts.append('<tr data-dest="' + dest + '" data-prog="' + source + '">')
        parts.append("<td>" + str(rec_date) + "</td>")
        parts.append("<td>" + dest + "</td>")
        parts.append("<td>" + source + "</td>")

        for pfx in ["Y", "W", "J", "F"]:
            avail = rec.get(pfx + "Available", False)
            cost = safe_int(rec.get(pfx + "MileageCost", 0))
            if avail and cost > 0:
                parts.append('<td class="avail-cell">' + "{:,}".format(cost) + "</td>")
            else:
                parts.append('<td class="unavail-cell">&mdash;</td>')

        taxes = safe_float(rec.get("TotalTaxes", 0))
        tax_cur = rec.get("TaxesCurrency", "") or ""
        if taxes > 0:
            tax_display = "{:.0f}".format(taxes) + " " + str(tax_cur)
        else:
            tax_display = "&mdash;"
        parts.append("<td>" + tax_display + "</td>")

        is_direct = "No"
        for pfx in ["Y", "W", "J", "F"]:
            d = rec.get(pfx + "Direct", False)
            if d is True or str(d).lower() in ("true", "1"):
                is_direct = "Yes"
                break
        parts.append("<td>" + is_direct + "</td>")
        parts.append("</tr>")

    parts.append("</tbody></table></div>")

    # --- Program Comparison Cards ---
    parts.append("<h2>Program Comparison</h2>")
    parts.append('<div class="prog-cards">')

    sorted_progs = sorted(analysis["programs"].items(), key=lambda x: -len(x[1]["days"]))
    for prog_name, pa in sorted_progs:
        parts.append('<div class="prog-card">')
        parts.append('<div class="prog-name">' + prog_name + "</div>")

        parts.append('<div class="card-stat"><span class="stat-label">Days Available</span>')
        parts.append('<span class="stat-value">' + str(len(pa["days"])) + "</span></div>")

        parts.append('<div class="card-stat"><span class="stat-label">Records</span>')
        parts.append('<span class="stat-value">' + str(pa["record_count"]) + "</span></div>")

        parts.append('<div class="card-stat"><span class="stat-label">Destinations</span>')
        parts.append('<span class="stat-value">' + ", ".join(pa["destinations"]) + "</span></div>")

        for pfx, cname in [("Y", "Economy"), ("W", "Premium"), ("J", "Business"), ("F", "First")]:
            best = pa.get("best_" + pfx)
            worst = pa.get("worst_" + pfx)
            parts.append('<div class="card-stat"><span class="stat-label">' + cname + "</span>")
            if best is not None:
                if best == worst:
                    display = "{:,}".format(best)
                else:
                    display = "{:,}".format(best) + "\u2013" + "{:,}".format(worst)
                parts.append('<span class="stat-value good">' + display + "</span></div>")
            else:
                parts.append('<span class="stat-value">&mdash;</span></div>')

        parts.append("</div>")  # prog-card
    parts.append("</div>")  # prog-cards

    # --- Key Insights ---
    parts.append("<h2>Key Insights</h2>")
    parts.append('<ul class="insights-list">')
    for insight in analysis["insights"]:
        parts.append("<li>" + insight + "</li>")
    parts.append("</ul>")

    # --- JavaScript ---
    parts.append("<script>")
    parts.append(build_js())
    parts.append("</script>")

    # --- Footer ---
    parts.append('<div style="margin-top:40px; padding:15px 0; border-top:1px solid #333; color:#555; font-size:0.8em;">')
    parts.append("Generated by seats-award-search-by-date v1.0.0 &middot; Data from Seats.aero Partner API &middot; " + gen_time)
    parts.append("</div>")

    parts.append("</div>")  # container
    parts.append("</body></html>")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Venice.ai infographic generation
# ---------------------------------------------------------------------------

def generate_infographic(analysis, origin, destinations, start_date, end_date,
                         highlight_cabin, output_path, venice_key):
    """Generate a 4K infographic via Venice.ai API."""
    if not venice_key:
        print("WARNING: No Venice API key provided. Skipping infographic generation.")
        return False

    dest_str = " and ".join(destinations)
    cabin_name = cabin_display(cabin_prefix(highlight_cabin))

    prompt_parts = []
    prompt_parts.append("A stunning 4K travel infographic for award flights from " + origin + " to " + dest_str + ".")
    prompt_parts.append("Dark luxury theme with deep navy and black background, glowing cyan and orange accent lights.")
    prompt_parts.append("Show stylized airplane silhouettes, world map route lines, calendar grid pattern.")
    prompt_parts.append("Premium aviation aesthetic with bokeh light effects, metallic gold accents.")
    prompt_parts.append("Abstract data visualization elements, flowing lines connecting cities.")
    prompt_parts.append("Photorealistic quality, cinematic lighting, ultra detailed.")
    prompt_parts.append(cabin_name + " class focus with first class luxury ambiance.")
    prompt_text = " ".join(prompt_parts)

    print("\nGenerating 4K infographic via Venice.ai...")
    print("  Prompt: " + prompt_text[:120] + "...")

    try:
        url = "https://api.venice.ai/api/v1/image/generate"
        headers = {
            "Authorization": "Bearer " + venice_key,
            "Content-Type": "application/json"
        }
        payload = {
            "model": "nano-banana-2",
            "prompt": prompt_text,
            "negative_prompt": "text, words, letters, numbers, watermark, blurry, low quality, distorted",
            "resolution": "4K",
            "aspect_ratio": "16:9",
            "format": "png",
            "safe_mode": True,
            "return_binary": False
        }
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        images = data.get("images", [])
        if not images:
            print("  ERROR: No images returned from Venice.ai")
            return False
        image_b64 = images[0]
        with open(output_path, "wb") as fimg:
            fimg.write(base64.b64decode(image_b64))
        print("  Infographic saved: " + output_path)
        return True
    except Exception as e:
        print("  ERROR generating infographic: " + str(e))
        return False


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive day-by-day award flight availability search "
                    "with HTML dashboard and 4K infographic."
    )
    parser.add_argument("--origin", required=True,
                        help="Origin IATA airport code (e.g., SEA)")
    parser.add_argument("--destinations", required=True,
                        help="Comma-separated destination IATA codes (e.g., HND,NRT)")
    parser.add_argument("--start-date", required=True,
                        help="Start date YYYY-MM-DD")
    parser.add_argument("--end-date", required=True,
                        help="End date YYYY-MM-DD")
    parser.add_argument("--source", default=None,
                        help="Filter by mileage program (default: all programs)")
    parser.add_argument("--cabin", default="business",
                        choices=["economy", "premium", "business", "first"],
                        help="Cabin to highlight in reports (default: business). "
                             "Display only, NOT used as API filter.")
    parser.add_argument("--output-dir",
                        default="/a0/usr/workdir/award-search-results",
                        help="Output directory")
    parser.add_argument("--deploy", action="store_true", default=True,
                        help="Copy results to /a0/webui/public/ (default: True)")
    parser.add_argument("--no-deploy", action="store_true", default=False,
                        help="Do NOT copy results to /a0/webui/public/")
    parser.add_argument("--skip-infographic", action="store_true", default=False,
                        help="Skip Venice.ai 4K infographic generation")
    parser.add_argument("--api-key", default=None,
                        help="Override SEATS_AERO_API_KEY env var")
    parser.add_argument("--venice-key", default=None,
                        help="Override VENICE_API_KEY env var")

    args = parser.parse_args()

    # Resolve keys
    api_key = args.api_key or os.environ.get("SEATS_AERO_API_KEY", "")
    venice_key = args.venice_key or os.environ.get("VENICE_API_KEY", "")
    if not api_key:
        print("ERROR: No Seats.aero API key. Set SEATS_AERO_API_KEY or use --api-key.")
        sys.exit(1)

    destinations = [d.strip().upper() for d in args.destinations.split(",") if d.strip()]
    origin = args.origin.strip().upper()
    start_date = args.start_date
    end_date = args.end_date

    try:
        validate_date(start_date)
        validate_date(end_date)
    except Exception as e:
        print("ERROR: Invalid date - " + str(e))
        sys.exit(1)

    deploy = args.deploy and not args.no_deploy

    os.makedirs(args.output_dir, exist_ok=True)

    dates = date_range(start_date, end_date)
    total_calls = len(dates) * len(destinations)

    print("=" * 60)
    print("Award Flight Search by Date")
    print("=" * 60)
    print("Origin:       " + origin)
    print("Destinations: " + ", ".join(destinations))
    print("Date range:   " + start_date + " to " + end_date + " (" + str(len(dates)) + " days)")
    print("Source:       " + (args.source or "all programs"))
    print("Highlight:    " + args.cabin)
    print("API calls:    " + str(total_calls) + " (estimated)")
    print("=" * 60)
    print()

    api = SeatsAeroAPI(api_key=api_key)

    print("Collecting availability data...")
    records, errors = collect_availability(api, origin, destinations, dates, source=args.source)

    if not records:
        print("\nWARNING: No records found. HTML will be generated but mostly empty.")

    # Save combined JSON
    dests_slug = "-".join(destinations)
    json_filename = "award-search-" + origin + "-" + dests_slug + "-" + start_date + ".json"
    json_path = os.path.join(args.output_dir, json_filename)
    combined_data = {
        "metadata": {
            "origin": origin,
            "destinations": destinations,
            "start_date": start_date,
            "end_date": end_date,
            "source_filter": args.source,
            "highlight_cabin": args.cabin,
            "total_records": len(records),
            "total_errors": len(errors),
            "api_calls": total_calls,
            "generated": datetime.now().isoformat(),
        },
        "errors": errors,
        "data": records
    }
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(combined_data, jf, indent=2, default=str)
    print("\nJSON saved: " + json_path)

    print("Analyzing data...")
    analysis = analyze_data(records, destinations, dates, args.cabin)

    print("Generating HTML dashboard...")
    html_content = generate_html(records, analysis, origin, destinations, dates,
                                  start_date, end_date, args.cabin)
    html_filename = "award-search-" + origin + "-" + dests_slug + "-" + start_date + ".html"
    html_path = os.path.join(args.output_dir, html_filename)
    with open(html_path, "w", encoding="utf-8") as hf:
        hf.write(html_content)
    print("HTML saved: " + html_path)

    # Generate infographic
    infographic_path = None
    if not args.skip_infographic:
        infographic_filename = "award-search-" + origin + "-" + dests_slug + "-" + start_date + "-infographic.png"
        infographic_path = os.path.join(args.output_dir, infographic_filename)
        success = generate_infographic(
            analysis, origin, destinations, start_date, end_date,
            args.cabin, infographic_path, venice_key
        )
        if not success:
            infographic_path = None

    # Deploy to webui public
    deployed_paths = []
    if deploy:
        public_dir = "/a0/webui/public"
        os.makedirs(public_dir, exist_ok=True)

        dest_html = os.path.join(public_dir, html_filename)
        shutil.copy2(html_path, dest_html)
        deployed_paths.append(dest_html)
        print("\nDeployed HTML: " + dest_html)

        if infographic_path and os.path.exists(infographic_path):
            infographic_fn = os.path.basename(infographic_path)
            dest_img = os.path.join(public_dir, infographic_fn)
            shutil.copy2(infographic_path, dest_img)
            deployed_paths.append(dest_img)
            print("Deployed infographic: " + dest_img)
            print("  Web path: /public/" + infographic_fn)

    # Final summary
    print("\n" + "=" * 60)
    print("SEARCH COMPLETE")
    print("=" * 60)
    print("Total records:  " + str(len(records)))
    print("Total errors:   " + str(len(errors)))
    print("API calls used: " + str(total_calls))
    print("\nOutput files:")
    print("  JSON:        " + json_path)
    print("  HTML:        " + html_path)
    if infographic_path:
        print("  Infographic: " + infographic_path)
    if deployed_paths:
        print("\nDeployed to webui:")
        for dp in deployed_paths:
            print("  " + dp)
    print("=" * 60)


if __name__ == "__main__":
    main()
