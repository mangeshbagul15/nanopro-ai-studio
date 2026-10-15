import unittest
from bs4 import BeautifulSoup
import re

class TestAll46ViewsAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('app/ui/dashboard.py', 'r', encoding='utf-8') as f:
            cls.dashboard_content = f.read()
        cls.soup = BeautifulSoup(cls.dashboard_content, 'html.parser')
        
        idx_script = cls.dashboard_content.find('<script>')
        cls.html_part = cls.dashboard_content[:idx_script]
        cls.script_part = cls.dashboard_content[idx_script:]

    def test_total_views_count(self):
        views = self.soup.find_all('div', class_='workspace-view')
        self.assertEqual(len(views), 46, f"Expected exactly 46 views, found {len(views)}")

    def test_all_views_inside_main_viewport(self):
        viewport = self.soup.find('main', id='main-content-viewport')
        self.assertIsNotNone(viewport, "main-content-viewport not found in HTML!")
        vp_views = viewport.find_all('div', class_='workspace-view')
        self.assertEqual(len(vp_views), 46, f"Expected all 46 views inside main-content-viewport, found {len(vp_views)}")

    def test_no_empty_views(self):
        viewport = self.soup.find('main', id='main-content-viewport')
        for v in viewport.find_all('div', class_='workspace-view'):
            view_id = v.get('id')
            children = v.find_all()
            self.assertGreater(len(children), 0, f"View {view_id} is completely empty!")
            text_content = v.get_text(strip=True)
            self.assertGreater(len(text_content), 10, f"View {view_id} has insufficient text content!")

    def test_sidebar_nav_items_map_to_views(self):
        nav_items = self.soup.find_all(class_='nav-item')
        self.assertGreaterEqual(len(nav_items), 45, f"Expected at least 45 nav items, found {len(nav_items)}")
        
        all_view_ids = {v.get('id') for v in self.soup.find_all('div', class_='workspace-view')}
        
        for item in nav_items:
            onclick = item.get('onclick', '')
            match = re.search(r"switchView\(['\"]([^'\"]+)['\"]\)", onclick)
            if match:
                target_view = 'view-' + match.group(1)
                self.assertIn(target_view, all_view_ids, f"Nav item {item.get_text(strip=True)} points to non-existent view {target_view}")

    def test_no_missing_javascript_functions_called_in_html(self):
        pattern = r'on(?:click|change|input|submit|keydown|keyup)=[\"\']([^\"\']+)[\"\']'
        handlers = re.findall(pattern, self.html_part)

        called_functions = set()
        for h in handlers:
            fns = re.findall(r'([a-zA-Z0-9_]+)\s*\(', h)
            for fn in fns:
                if fn not in ['getElementById', 'getAttribute', 'preventDefault', 'stopPropagation', 'alert', 'confirm', 'prompt', 'if', 'trim', 'toLowerCase']:
                    called_functions.add(fn)

        missing_in_script = []
        for fn in sorted(called_functions):
            if not re.search(r'(?:async\s+)?function\s+' + fn + r'\s*\(', self.script_part):
                missing_in_script.append(fn)

        self.assertEqual(len(missing_in_script), 0, f"Missing JS function implementations: {missing_in_script}")

if __name__ == '__main__':
    unittest.main()
