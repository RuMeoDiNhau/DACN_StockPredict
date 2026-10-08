import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestDashboardUiContract(unittest.TestCase):
    def setUp(self):
        self.index = (ROOT / "frontend" / "index.html").read_text(encoding="utf-8")
        self.script = (ROOT / "frontend" / "assets" / "js" / "app.js").read_text(encoding="utf-8")
        self.styles = (ROOT / "frontend" / "assets" / "css" / "style.css").read_text(encoding="utf-8")

    def test_dashboard_pins_echarts_and_has_required_regions(self):
        self.assertIn("echarts@5.5.1", self.index)
        for element_id in ("symbol-form", "dashboard-symbol", "chart", "symbols-list", "ohlcv-table", "toggle-table"):
            self.assertIn(f'id="{element_id}"', self.index)

    def test_chart_has_lifecycle_resize_and_fallback(self):
        self.assertIn("window.echarts", self.script)
        self.assertIn("ResizeObserver", self.script)
        self.assertIn("disposeDashboardChart", self.script)
        self.assertIn("Không tải được thư viện biểu đồ", self.script)

    def test_dashboard_has_responsive_design_tokens_and_no_framework(self):
        self.assertIn("--color-primary", self.styles)
        self.assertIn("@media (max-width: 760px)", self.styles)
        self.assertNotIn("react", self.index.lower())
        self.assertNotIn("vue", self.index.lower())


if __name__ == "__main__":
    unittest.main()
