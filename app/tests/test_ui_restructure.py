"""
Unit Tests for Nano Pro Complete UI/UX Restructure (v14)
"""

import unittest
from app.ui.dashboard import get_dashboard_html

class TestUIRestructure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = get_dashboard_html()

    def test_app_shell_and_layout_containers(self):
        self.assertIn('<div id="app-shell" class="app-shell">', self.html)
        self.assertIn('<aside id="sidebar" class="app-sidebar">', self.html)
        self.assertIn('<header class="global-header workspace-topbar">', self.html)
        self.assertIn('<main id="main-content-viewport" class="main-content-viewport">', self.html)
        self.assertIn('<div id="right-panel">', self.html)

    def test_sidebar_groups_and_features(self):
        self.assertIn('id="sidebarCollapseBtn"', self.html)
        self.assertIn('id="sidebarSearchInput"', self.html)
        self.assertIn('id="navGroup-home"', self.html)
        self.assertIn('id="navGroup-core"', self.html)
        self.assertIn('id="navGroup-data"', self.html)
        self.assertIn('id="navGroup-career"', self.html)
        self.assertIn('id="navGroup-automation"', self.html)
        self.assertIn('id="navGroup-discover"', self.html)
        self.assertIn('id="navGroup-studios"', self.html)
        self.assertIn('id="navGroup-services"', self.html)
        self.assertIn('toggleNavGroup(this)', self.html)
        self.assertIn('filterSidebarViews', self.html)

    def test_all_46_views_preserved(self):
        expected_views = [
            'dashboard', 'sql_video', 'python_video', 'image_agent', 'coding_agent',
            'research_agent', 'telegram_agent', 'assistant', 'ai_office', 'backups',
            'logs', 'settings', 'ai_manager', 'voice_assistant', 'free_apis',
            'github_explorer', 'research_library', 'live_discovery', 'models_hub',
            'agent_control', 'approvals', 'data_engineer', 'data_analyst', 'data_science',
            'file_converter', 'cyber_lab', 'research_knowledge', 'document_studio',
            'automation_scheduler', 'news_center', 'entertainment_center', 'book_reader',
            'cloud_trends', 'communication', 'app_launcher', 'shopping_services',
            'media_discovery', 'monitoring', 'task_history', 'amazon_tracker',
            'career_hub', 'learning_hub', 'startup_recovery', 'discovery_dashboard',
            'storage_dashboard', 'vault'
        ]
        self.assertEqual(len(expected_views), 46)
        for view_id in expected_views:
            self.assertIn(f'id="view-{view_id}"', self.html, f"Missing view container: view-{view_id}")

    def test_panoramic_stage_placement(self):
        # Verify stage is inside view-dashboard, NOT before it
        stage_pos = self.html.find('id="lavishCommandStage"')
        dash_pos = self.html.find('id="view-dashboard"')
        self.assertNotEqual(stage_pos, -1, "lavishCommandStage must exist")
        self.assertNotEqual(dash_pos, -1, "view-dashboard must exist")
        self.assertGreater(stage_pos, dash_pos, "lavishCommandStage must be inside view-dashboard")

    def test_global_header_controls(self):
        self.assertIn('id="sidebarToggleBtn"', self.html)
        self.assertIn('id="breadcrumbCurrent"', self.html)
        self.assertIn('id="topbarModeBadge"', self.html)
        self.assertIn('id="studioStatusPill"', self.html)
        self.assertIn('id="aiManagerSymbolWrapper"', self.html)
        self.assertIn('id="themeToggleBtn"', self.html)
        self.assertIn('id="telemetryToggleBtn"', self.html)
        self.assertIn('openCommandPalette()', self.html)

    def test_command_palette_modal(self):
        self.assertIn('id="commandPaletteModal"', self.html)
        self.assertIn('id="commandPaletteInput"', self.html)
        self.assertIn('id="commandPaletteResults"', self.html)
        self.assertIn('handleCommandPaletteKey', self.html)

    def test_design_system_and_theme_tokens(self):
        self.assertIn('[data-theme="dark"]', self.html)
        self.assertIn('[data-theme="light"]', self.html)
        self.assertIn('--bg-base', self.html)
        self.assertIn('--bg-sidebar', self.html)
        self.assertIn('--bg-card', self.html)
        self.assertIn('--border-highlight', self.html)
        self.assertIn('initTheme()', self.html)
        self.assertIn('toggleTheme()', self.html)

    def test_responsive_media_queries(self):
        self.assertIn('@media (max-width: 1400px)', self.html)
        self.assertIn('@media (max-width: 1024px)', self.html)
        self.assertIn('@media (max-width: 768px)', self.html)

if __name__ == "__main__":
    unittest.main()
