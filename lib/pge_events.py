#!/usr/bin/env python3
"""Check if today is a mass-event day at PGE Narodowy."""

import sys
from datetime import date

import requests
from bs4 import BeautifulSoup

URL = "https://www.pgenarodowy.pl/calendar/calendar-graphic.php?month={m:02d}&year={y}"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; pge-calendar-check/1.0)"}

PL_MONTHS = {
    1: "stycznia", 2: "lutego", 3: "marca", 4: "kwietnia",
    5: "maja", 6: "czerwca", 7: "lipca", 8: "sierpnia",
    9: "września", 10: "października", 11: "listopada", 12: "grudnia",
}


def pl_date(d: date) -> str:
    return f"{d.day:02d} {PL_MONTHS[d.month]} {d.year}"


def get_day_div(soup, d: date):
    anchor = soup.find("a", attrs={"data-currentdate": pl_date(d)})
    return anchor.find_parent("div", class_="calendar--day") if anchor else None


def check(d: date):
    r = requests.get(URL.format(m=d.month, y=d.year), headers=HEADERS, timeout=20)
    r.raise_for_status()
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")

    day = get_day_div(soup, d)
    if day is None:
        raise LookupError(f"Day {pl_date(d)} not found on the page")

    events, mass = [], []
    for a in day.select("a.calendar--day-event"):
        if "mobile_events" in a.get("class", []) or a.find_parent(class_="mobile_events"):
            continue  # skip duplicated mobile markup
        title_el = a.select_one(".calendar--event-title")
        time_el = a.select_one(".calendar--event-date")
        item = {
            "title": title_el.get_text(strip=True) if title_el else a.get_text(" ", strip=True),
            "time": time_el.get_text(strip=True) if time_el else "cały dzień",
            "mass": "mass-event" in a.get("class", []),
            "url": a.get("data-href", ""),
        }
        events.append(item)
        if item["mass"]:
            mass.append(item)

    return events, mass


def check_pge_events():
    d = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    try:
        events, mass = check(d)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    if mass == 'YES':
        return f'<h3>Wydarzenie na PGE Narodowym: {mass[0]["title"]}</h3>'
    else:
        return f'<h3>Brak wydarzeń na PGE Narodowym</h3>'
        
    # print(f"{d.isoformat()} — mass event: {'YES' if mass else 'no'}")
    # for e in events:
    #     tag = "[MASS] " if e["mass"] else "        "
    #     print(f"  {tag}{e['time']:<12} {e['title']}")
