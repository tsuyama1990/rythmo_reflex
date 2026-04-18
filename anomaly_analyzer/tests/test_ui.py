from playwright.sync_api import Page, expect


# @pytest.mark.skip(reason="Needs local reflex server running to test UI") # type: ignore[untyped-decorator]
def test_app_loads(page: Page) -> None:
    page.goto("http://localhost:3000")

    # Check title
    expect(page.locator("h1").first).to_contain_text("Japan Stock Anomaly Analyzer")

    # Check inputs exist
    expect(page.locator("input[placeholder='e.g. 6599, 7713']")).to_be_visible()

    # Check buttons exist
    expect(page.locator("button:has-text('Fetch Data')")).to_be_visible()
    expect(page.locator("button:has-text('START ANALYSIS')")).to_be_visible()
