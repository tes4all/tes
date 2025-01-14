import unittest
from shopify.theme_updater import _get_theme_info


class TestMain(unittest.TestCase):
    def test_get_theme_info(self):
        theme_info = _get_theme_info()
        self.assertEqual(theme_info["name"], "theme_info")
        self.assertEqual(theme_info["theme_name"], "Impact")
        self.assertEqual(theme_info["theme_author"], "Maestrooo")
        self.assertEqual(theme_info["theme_version"], "6.4.1")
        self.assertEqual(
            theme_info["theme_documentation_url"], "https://support.maestrooo.com/"
        )
        self.assertEqual(
            theme_info["theme_support_url"],
            "https://support.maestrooo.com/article/203-contact-us",
        )
