#!/usr/bin/env python3
import time

from playwright.sync_api import sync_playwright

LINKEDIN_JOBS_URL = "https://www.linkedin.com/jobs/search/"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()
        page.goto(LINKEDIN_JOBS_URL, wait_until="domcontentloaded", timeout=30000)
        print("LinkedIn jobs opened. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)


if __name__ == "__main__":
    main()
