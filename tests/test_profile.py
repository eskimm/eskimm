import json
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class ProfileTests(unittest.TestCase):
    def test_sidebar_identity(self):
        path = ROOT / "profile.json"
        self.assertTrue(path.is_file(), "profile.json is missing")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(set(data), {"name", "bio", "blog", "company", "location"})
        self.assertEqual(data["name"], "Alan Redzepagic")
        self.assertEqual(data["blog"], "https://alanred.me")
        self.assertEqual(data["company"], "Forever Labs")
        self.assertEqual(data["location"], "New York")
        self.assertIn("CTO at Forever Labs", data["bio"])
        self.assertLessEqual(len(data["bio"]), 160)

    def test_readme_public_story(self):
        path = ROOT / "README.md"
        self.assertTrue(path.is_file(), "README.md is missing")
        text = path.read_text(encoding="utf-8")
        self.assertEqual(re.findall(r"^# .+$", text, re.M), ["# Alan Redzepagic"])
        self.assertEqual(re.findall(r"^## .+$", text, re.M), [
            "## Cloud architecture",
            "## DevOps & self-hosting",
            "## AI systems",
            "## Writing",
            "## Get in touch",
        ])
        self.assertTrue(200 <= len(text.split()) <= 450)
        self.assertIn("assets/profile-banner.svg", text)
        for required in ("AWS", "Vercel", "DevOps", "self-hosting", "CI/CD", "CDK"):
            self.assertIn(required, text)
        for obsolete in ("Everyrealm", "neonARKade", "Duel", "Vue", "Nuxt", "WordPress"):
            self.assertNotIn(obsolete, text)
        allowed = {
            "https://alanred.me",
            "https://alanred.me/articles/ai-sovereignty-when-assistance-becomes-dependence",
            "https://alanred.me/articles/managing-the-whole-forest",
            "https://x.com/allanred",
            "https://www.linkedin.com/in/alanredzepagic",
        }
        links = set(re.findall(r"\]\((https?://[^)]+|mailto:[^)]+)\)", text))
        self.assertEqual(links, allowed)
        self.assertNotIn("mailto:", text)
        self.assertNotRegex(text, r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
        self.assertNotRegex(text, r"(?i)<(?:script|iframe|table|style)\b")
        self.assertNotRegex(text, r"(?i)shields\.io|github-readme-stats|streak-stats|visitor-badge")
        self.assertNotIn("https://github.com/", text)
        self.assertNotIn("vercel.app", text)

    def test_banner_is_accessible_and_self_contained(self):
        path = ROOT / "assets/profile-banner.svg"
        self.assertTrue(path.is_file(), "profile-banner.svg is missing")
        self.assertLess(path.stat().st_size, 50000)
        raw = path.read_text(encoding="utf-8")
        root = ET.fromstring(raw)
        ns = {"s": "http://www.w3.org/2000/svg"}
        self.assertEqual(root.attrib.get("viewBox"), "0 0 1200 300")
        self.assertEqual(root.attrib.get("role"), "img")
        self.assertEqual(root.attrib.get("aria-labelledby"), "title desc")
        title = root.find("s:title", ns)
        desc = root.find("s:desc", ns)
        self.assertIsNotNone(title)
        self.assertIsNotNone(desc)
        assert title is not None and desc is not None
        self.assertEqual(title.attrib.get("id"), "title")
        self.assertEqual(desc.attrib.get("id"), "desc")
        self.assertTrue(title.text)
        self.assertTrue(desc.text)
        for element in root.iter():
            tag = element.tag.rsplit("}", 1)[-1]
            self.assertNotIn(tag, {"script", "foreignObject", "image", "animate", "animateTransform"})
            for attribute in element.attrib:
                local = attribute.rsplit("}", 1)[-1].lower()
                self.assertFalse(local.startswith("on"))
                self.assertNotIn(local, {"href", "src"})
        self.assertNotRegex(raw, r"@import|url\(")
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("![Alan Redzepagic — Discover. Develop. Deploy.]", text)


if __name__ == "__main__":
    unittest.main()
