"""
Unit and integration tests for Mobile Layout & Device-Based Feature Access Control.
Verifies:
1. Dual device feature permissions (Desktop vs Mobile) in AuthManager.
2. Clean mobile header CSS (ONLY ☰ and 🔔 visible; all clutter hidden).
3. Off-canvas sidebar drawer (hidden by default, smooth overlay with backdrop).
4. Responsive bottom navigation and mobile drawer footer profile.
5. RBAC Permissions modal dual device tab structure.
"""
import unittest
import json
from app.core.auth_manager import auth_manager
from app.ui.dashboard import get_dashboard_html

class TestMobileAndDevicePermissions(unittest.TestCase):

    def test_01_auth_manager_device_dict_permissions(self):
        """Verify AuthManager saves and retrieves device-separated permissions."""
        test_user = "device_user1"
        # Create user if needed
        reg = auth_manager.register_user(
            full_name="Test Device User",
            username=test_user,
            email="device_user1@example.com",
            password="Password123!"
        )
        user_id = reg.get("user_id")
        if not user_id:
            # find existing
            users = auth_manager.list_users()
            for u in users:
                if u["username"] == test_user:
                    user_id = u["id"]
                    break
        
        self.assertIsNotNone(user_id, "User ID must be found or created")

        # Test approving with dual device dict
        dual_perms = {
            "desktop": ["dashboard", "data_engineer", "data_analyst", "cyber_lab"],
            "mobile": ["dashboard", "ai_manager", "amazon_tracker", "news_center"]
        }
        res = auth_manager.update_user_permissions(
            user_id=user_id,
            admin_username="nanopro",
            allowed_views=dual_perms,
            access_mode="MODIFY"
        )
        self.assertEqual(res["status"], "success")

        # Verify parsed_views returns the dict
        users = auth_manager.list_users()
        found = None
        for u in users:
            if u["id"] == user_id:
                found = u
                break
        self.assertIsNotNone(found)
        self.assertIsInstance(found["allowed_views"], dict)
        self.assertIn("desktop", found["allowed_views"])
        self.assertIn("mobile", found["allowed_views"])
        self.assertEqual(found["allowed_views"]["mobile"], dual_perms["mobile"])
        self.assertEqual(found["allowed_views"]["desktop"], dual_perms["desktop"])

    def test_02_dashboard_html_clean_mobile_header(self):
        """Verify mobile header CSS rules strictly hide clutter and keep only ☰ and 🔔."""
        html = get_dashboard_html()
        
        # Must have ultra-clean header rule
        self.assertIn(".header-right-group > button[onclick*=\"logs\"]", html)
        self.assertIn("#sidebarToggleBtn", html)
        self.assertIn(".header-mobile-brand", html)
        
        # Tablet breakpoint must be isolated
        self.assertIn("(min-width: 769px) and (max-width: 1024px)", html)
        self.assertNotIn("@media (max-width: 1024px) {\n            #sidebar", html)

    def test_03_dashboard_html_offcanvas_sidebar(self):
        """Verify sidebar is pure off-canvas drawer on mobile (hidden -320px, zero layout width)."""
        html = get_dashboard_html()
        self.assertIn("left: -320px !important;", html)
        self.assertIn("visibility: hidden !important;", html)
        self.assertIn(".app-shell.mobile-sidebar-open #sidebar", html)
        self.assertIn("mobileSidebarCloseBtn", html)
        self.assertIn("mobile-sidebar-backdrop", html)

    def test_04_sidebar_footer_mobile_user_profile(self):
        """Verify drawer footer contains user account details and logout button."""
        html = get_dashboard_html()
        self.assertIn("sidebarFooterUsername", html)
        self.assertIn("sidebarFooterRole", html)
        self.assertIn("performLogout()", html)

    def test_05_mobile_bottom_nav_tabs(self):
        """Verify mobile bottom bar has 5 essential tabs: Chat, Deals, Tasks, News, Menu."""
        html = get_dashboard_html()
        self.assertIn("mobTab-dashboard", html)
        self.assertIn("mobTab-amazon_tracker", html)
        self.assertIn("mobTab-assistant", html)
        self.assertIn("mobTab-news_center", html)
        self.assertIn("mobTab-menu", html)

    def test_06_auth_modal_dual_device_tabs(self):
        """Verify RBAC permissions modal renders both Desktop and Mobile device tabs."""
        html = get_dashboard_html()
        self.assertIn("permTabDesktop", html)
        self.assertIn("permTabMobile", html)
        self.assertIn("permContainerDesktop", html)
        self.assertIn("permContainerMobile", html)
        self.assertIn("switchPermDeviceTab", html)
        self.assertIn("getUserDeviceAllowedViews", html)

if __name__ == '__main__':
    unittest.main()
