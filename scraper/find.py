#!/usr/bin/env python3
import os
import time
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Error as PlaywrightError

load_dotenv()

BRIDGE_URL = "http://localhost:8080"
LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"
LINKEDIN_JOBS_BASE_URL = "https://www.linkedin.com/jobs/search/"


def fetch_keyword() -> str:
    resp = requests.get(f"{BRIDGE_URL}/keyword", timeout=60)
    resp.raise_for_status()
    data = resp.json()
    print(f"Keyword: {data['keyword']} — {data['rationale']}")
    return data["keyword"]


def main():
    email = os.environ["LINKEDIN_EMAIL"]
    password = os.environ["LINKEDIN_PASSWORD"]

    # Get keyword from bridge before opening browser
    keyword = fetch_keyword()
    jobs_url = LINKEDIN_JOBS_BASE_URL + "?" + urlencode({"keywords": keyword})

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
        try:
            page.goto(LINKEDIN_LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
            page.fill("#username", email)
            page.fill("#password", password)
            page.click("button[type='submit']")
            print("Logging in...")

            page.wait_for_url("**/feed/**", timeout=30000)
            print("Logged in. Opening jobs...")

            page.goto(jobs_url, wait_until="domcontentloaded", timeout=30000)
            print("LinkedIn jobs opened. Press Ctrl+C to exit.")
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, PlaywrightError):
            pass


if __name__ == "__main__":
    main()
