#!/usr/bin/env python3
"""Generate an RSS 2.0 feed for Is It Christmas? (Dec 1 – Dec 25, Europe/London)."""

from __future__ import annotations

import argparse
from datetime import date, datetime, time
from email.utils import format_datetime
from pathlib import Path
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

ATOM_NS = "http://www.w3.org/2005/Atom"
DEFAULT_SITE_URL = "https://knowlesy.github.io/is-it-christmas/"
DEFAULT_TIMEZONE = "Europe/London"
PUBLISH_HOUR = 9
PUBLISH_MINUTE = 0


def parse_target_date(date_str: str | None, tz: ZoneInfo) -> date:
    """Return the target calendar date in the given timezone."""
    if date_str:
        return date.fromisoformat(date_str)
    return datetime.now(tz).date()


def active_days_for_date(target: date) -> list[date]:
    """Return the list of December dates (newest first) that should appear in the feed.

    - Jan 1 – Nov 30: empty list (no items until Dec 1).
    - Dec 1 – Dec 25: Dec 1 through target date (inclusive).
    - Dec 26 – Dec 31: Dec 1 through Dec 25 (no new items after Dec 25).
    """
    if target.month != 12:
        return []
    last_day = min(target.day, 25)
    return [date(target.year, 12, day) for day in range(last_day, 0, -1)]


def build_item_payload(day: date, site_url: str, tz: ZoneInfo) -> dict[str, str]:
    """Build title, description, link, guid, and RFC 2822 pubDate for a single December day."""
    is_christmas = day.month == 12 and day.day == 25
    answer = "YES" if is_christmas else "NO"
    formatted_day = f"{day.day} {day.strftime('%B %Y')}"

    if is_christmas:
        description = f"YES — Merry Christmas! ({formatted_day})"
    else:
        days_left = 25 - day.day
        day_word = "day" if days_left == 1 else "days"
        description = f"NO — {formatted_day}. {days_left} {day_word} until Christmas."

    pub_dt = datetime.combine(day, time(PUBLISH_HOUR, PUBLISH_MINUTE), tzinfo=tz)
    base_url = site_url.rstrip("/") + "/"

    return {
        "title": f"Is it Christmas? {answer}",
        "link": f"{base_url}?date={day.isoformat()}",
        "guid": f"is-it-christmas-{day.isoformat()}",
        "pubDate": format_datetime(pub_dt),
        "description": description,
    }


def generate_rss_xml(
    target: date,
    site_url: str = DEFAULT_SITE_URL,
    timezone_name: str = DEFAULT_TIMEZONE,
) -> str:
    """Generate a valid RSS 2.0 XML document for the given target date."""
    tz = ZoneInfo(timezone_name)
    base_url = site_url.rstrip("/") + "/"
    feed_url = f"{base_url}feed.xml"

    ET.register_namespace("atom", ATOM_NS)

    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = "Is it Christmas?"
    ET.SubElement(channel, "link").text = base_url
    ET.SubElement(channel, "description").text = (
        "Daily check from 1 December to 25 December (09:00 UK time) answering the only "
        "question that matters: Is it Christmas?"
    )
    ET.SubElement(channel, "language").text = "en-gb"
    ET.SubElement(channel, "ttl").text = "60"

    ET.SubElement(
        channel,
        f"{{{ATOM_NS}}}link",
        {
            "href": feed_url,
            "rel": "self",
            "type": "application/rss+xml",
        },
    )

    days = active_days_for_date(target)
    if days:
        last_build_dt = datetime.combine(days[0], time(PUBLISH_HOUR, PUBLISH_MINUTE), tzinfo=tz)
    else:
        last_build_dt = datetime.combine(target, time(PUBLISH_HOUR, PUBLISH_MINUTE), tzinfo=tz)

    ET.SubElement(channel, "lastBuildDate").text = format_datetime(last_build_dt)

    for day in days:
        payload = build_item_payload(day, base_url, tz)
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = payload["title"]
        ET.SubElement(item, "link").text = payload["link"]
        guid = ET.SubElement(item, "guid", {"isPermaLink": "false"})
        guid.text = payload["guid"]
        ET.SubElement(item, "pubDate").text = payload["pubDate"]
        ET.SubElement(item, "description").text = payload["description"]

    ET.indent(rss, space="  ")
    xml_body = ET.tostring(rss, encoding="unicode", xml_declaration=False)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_body + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate feed.xml for Is It Christmas? (Dec 1 – Dec 25, Europe/London)."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("feed.xml"),
        help="Path to write the generated RSS XML file (default: feed.xml).",
    )
    parser.add_argument(
        "--date",
        dest="date_str",
        default=None,
        help="Override target date in YYYY-MM-DD format (default: today in Europe/London).",
    )
    parser.add_argument(
        "--site-url",
        default=DEFAULT_SITE_URL,
        help=f"Base URL of the hosted site (default: {DEFAULT_SITE_URL}).",
    )
    parser.add_argument(
        "--timezone",
        default=DEFAULT_TIMEZONE,
        help=f"IANA timezone name (default: {DEFAULT_TIMEZONE}).",
    )
    args = parser.parse_args()

    tz = ZoneInfo(args.timezone)
    target = parse_target_date(args.date_str, tz)
    xml_output = generate_rss_xml(target=target, site_url=args.site_url, timezone_name=args.timezone)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(xml_output, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
