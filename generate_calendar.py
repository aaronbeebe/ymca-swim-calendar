import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime, timedelta
import re
import os

BASE_URL = "https://prospect-park-ymca.virtuagym.com/classes/week/{date_str}?event_type=1206&embedded=1&pref_club=42693"
OUTPUT_FILE = "docs/swim.ics"

calendar = Calendar()

# Loop over 4 weeks ahead
for week_offset in range(4):
    start_date = datetime.today() + timedelta(weeks=week_offset)
    date_str = start_date.strftime("%Y-%m-%d")
    url = BASE_URL.format(date_str=date_str)

    print(f"Fetching: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    for div in soup.find_all("div", class_=re.compile(r"internal-event-day-\d{2}-\d{2}-\d{4}")):
        full_class_string = " ".join(div.get("class", []))
        date_match = re.search(r"internal-event-day-(\d{2})-(\d{2})-(\d{4})", full_class_string)

        if not date_match:
            continue
        day, month, year = date_match.groups()
        event_date = f"{year}-{month}-{day}"

        name_tag = div.find("span", class_="classname")
        time_tag = div.find("span", class_="time")
        if not name_tag or not time_tag:
            continue

        name = name_tag.get_text(strip=True)
        time_range = time_tag.get_text(strip=True)

        try:
            start_time_str, end_time_str = [t.strip() for t in time_range.split("-")]
            start_dt = datetime.strptime(f"{event_date} {start_time_str}", "%Y-%m-%d %I:%M %p")
            end_dt = datetime.strptime(f"{event_date} {end_time_str}", "%Y-%m-%d %I:%M %p")
        except ValueError:
            continue  # Skip malformed times

        e = Event()
        e.name = name
        e.begin = start_dt
        e.end = end_dt
        calendar.events.add(e)

# Ensure output folder exists
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# Write to .ics
with open(OUTPUT_FILE, "w") as f:
    f.writelines(calendar)

print(f"✅ Saved {len(calendar.events)} events to {OUTPUT_FILE}")
