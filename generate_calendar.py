import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from datetime import datetime, timedelta
import re
import os

URL = "https://ymcanyc.org/locations/prospect-park-ymca/schedules#swim"
OUTPUT_FILE = "docs/swim.ics"

def parse_time_range(start_end_str):
    start_str, end_str = start_end_str.split("-")
    start = datetime.strptime(start_str.strip(), "%I:%M %p")
    end = datetime.strptime(end_str.strip(), "%I:%M %p")
    return start.time(), end.time()

def fetch_swim_events():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    calendar = Calendar()

    # Each swim event is in a <div> with a classname and time
    for div in soup.find_all("div", class_=re.compile("internal-event-day")):
        class_name = div.find("span", class_="classname").text.strip()
        time_range = div.find("span", class_="time").text.strip()

        # Extract date from the class name: internal-event-day-DD-MM-YYYY
        date_match = re.search(r"internal-event-day-(\d{2})-(\d{2})-(\d{4})", div["class"][-1])
        if not date_match:
            continue
        day, month, year = map(int, date_match.groups())
        start_time, end_time = parse_time_range(time_range)

        start_dt = datetime(year, month, day, start_time.hour, start_time.minute)
        end_dt = datetime(year, month, day, end_time.hour, end_time.minute)

        e = Event()
        e.name = class_name
        e.begin = start_dt
        e.end = end_dt
        calendar.events.add(e)

    return calendar

if __name__ == "__main__":
    os.makedirs("docs", exist_ok=True)
    cal = fetch_swim_events()
    with open(OUTPUT_FILE, "w") as f:
        f.writelines(cal)
    print(f"✅ Calendar saved to {OUTPUT_FILE}")
