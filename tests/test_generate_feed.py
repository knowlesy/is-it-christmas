#!/usr/bin/env python3
"""Unit tests for the Is It Christmas? RSS feed generator."""

from __future__ import annotations

from datetime import date
import unittest
import xml.etree.ElementTree as ET

from scripts.generate_feed import ATOM_NS, active_days_for_date, generate_rss_xml


class GenerateFeedTests(unittest.TestCase):
    def parse_feed(self, target: date) -> ET.Element:
        xml_str = generate_rss_xml(target)
        return ET.fromstring(xml_str)

    def test_before_december_has_zero_items(self) -> None:
        for d in (date(2026, 1, 1), date(2026, 6, 15), date(2026, 11, 24), date(2026, 11, 30)):
            root = self.parse_feed(d)
            channel = root.find("channel")
            self.assertIsNotNone(channel)
            items = channel.findall("item")
            self.assertEqual(items, [], f"Expected 0 items on {d.isoformat()}")
            atom_link = channel.find(f"{{{ATOM_NS}}}link")
            self.assertIsNotNone(atom_link)
            self.assertEqual(atom_link.attrib.get("rel"), "self")

    def test_dec_1_starts_with_no(self) -> None:
        root = self.parse_feed(date(2026, 12, 1))
        items = root.findall("channel/item")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].findtext("title"), "Is it Christmas? NO")
        self.assertEqual(items[0].findtext("guid"), "is-it-christmas-2026-12-01")
        self.assertIn("24 days until Christmas", items[0].findtext("description") or "")
        self.assertIn("09:00:00 +0000", items[0].findtext("pubDate") or "")

    def test_dec_24_has_24_no_items(self) -> None:
        root = self.parse_feed(date(2026, 12, 24))
        items = root.findall("channel/item")
        self.assertEqual(len(items), 24)
        self.assertEqual(items[0].findtext("guid"), "is-it-christmas-2026-12-24")
        self.assertEqual(items[0].findtext("title"), "Is it Christmas? NO")
        self.assertIn("1 day until Christmas", items[0].findtext("description") or "")
        self.assertEqual(items[-1].findtext("guid"), "is-it-christmas-2026-12-01")

    def test_dec_25_is_yes_and_has_25_items(self) -> None:
        root = self.parse_feed(date(2026, 12, 25))
        items = root.findall("channel/item")
        self.assertEqual(len(items), 25)
        self.assertEqual(items[0].findtext("title"), "Is it Christmas? YES")
        self.assertEqual(items[0].findtext("guid"), "is-it-christmas-2026-12-25")
        self.assertIn("Merry Christmas", items[0].findtext("description") or "")
        for item in items[1:]:
            self.assertEqual(item.findtext("title"), "Is it Christmas? NO")

    def test_after_dec_25_stops_adding_items(self) -> None:
        dec_25_xml = generate_rss_xml(date(2026, 12, 25))
        dec_26_xml = generate_rss_xml(date(2026, 12, 26))
        dec_31_xml = generate_rss_xml(date(2026, 12, 31))
        self.assertEqual(dec_25_xml, dec_26_xml)
        self.assertEqual(dec_25_xml, dec_31_xml)

    def test_new_year_resets_feed(self) -> None:
        self.assertEqual(active_days_for_date(date(2027, 1, 1)), [])


if __name__ == "__main__":
    unittest.main()
