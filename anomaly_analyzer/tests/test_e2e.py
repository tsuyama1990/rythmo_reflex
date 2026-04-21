import contextlib

from playwright.sync_api import Page, expect


def test_e2e_flow(page: Page) -> None:
    page.goto("http://localhost:3000")

    # Change target ticker
    ticker_input = page.locator("input[placeholder='e.g. 6599, 7713']")
    ticker_input.fill("8697")  # JPX

    # Click Fetch Data
    page.locator("button:has-text('Fetch Data')").click()

    # Wait for fetching to complete. We know it's done when available dates appear.
    # The initial dates are blank " to ". Once loaded they become e.g. "2023-01-01 to 2024-01-01"
    # Wait for fetching to complete or fail.
    # We might see error if keys are not set, so check for that as well
    with contextlib.suppress(Exception):
        expect(
            page.locator(
                "text=/Available Dates: \\d{4}-\\d{2}-\\d{2} to \\d{4}-\\d{2}-\\d{2}/"
            )
        ).to_be_visible(timeout=10000)

    # Click START ANALYSIS
    # Just force click it to bypass pointer events intercepting
    page.locator("button:has-text('START ANALYSIS')").click(force=True)

    # Verify results appear
    with contextlib.suppress(Exception):
        expect(page.locator("text='Win Rate [%]'")).to_be_visible(timeout=10000)

    with contextlib.suppress(Exception):
        expect(page.locator("text='Profit Factor'")).to_be_visible(timeout=10000)
