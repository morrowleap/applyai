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

            jobs = []
            page_num = 1

            while True:
                # Wait for the list to load
                page.wait_for_selector("li[data-occludable-job-id]", timeout=15000)

                # Scroll the left panel to load more cards (LinkedIn lazy-loads them)
                for _ in range(5):
                    page.evaluate("""
                        const list = document.querySelector('.jobs-search-results-list');
                        if (list) list.scrollTop += 2000;
                    """)
                    time.sleep(1)

                # Collect all job IDs now in DOM (stable across re-renders)
                job_ids = page.eval_on_selector_all(
                    "li[data-occludable-job-id]",
                    "els => els.map(el => el.getAttribute('data-occludable-job-id'))"
                )
                print(f"\n--- Page {page_num} — {len(job_ids)} jobs ---")

                for i, job_id in enumerate(job_ids):
                    try:
                        # Scroll card into view — forces LinkedIn to re-render it into DOM
                        card = page.locator(f"li[data-occludable-job-id='{job_id}']")
                        card.scroll_into_view_if_needed()
                        time.sleep(0.3)
                        card.click()

                        # Wait for the description content to fully render
                        page.wait_for_selector("#job-details p", timeout=10000)

                        title_el = page.query_selector("h1.t-24.t-bold")
                        about_el = page.query_selector("#job-details")

                        title = title_el.inner_text().strip() if title_el else "N/A"
                        about = about_el.inner_text().strip() if about_el else "N/A"

                        jobs.append({"title": title, "about": about})
                        print(f"\n[{i + 1}/{len(job_ids)}] {title}\n{about[:200]}...")
                    except Exception as e:
                        print(f"\n[{i + 1}/{len(job_ids)}] Skipping job {job_id}: {e}")
                        continue

                # Check for Next button
                next_btn = page.locator("button[aria-label='View next page']")
                if next_btn.count() == 0 or not next_btn.is_enabled():
                    print(f"\nNo more pages. Total scraped: {len(jobs)} jobs.")
                    break

                next_btn.click()
                page_num += 1
                time.sleep(2)

            print(f"\nDone. Scraped {len(jobs)} jobs total.")
            while True:
                time.sleep(1)
        except (KeyboardInterrupt):
            pass


if __name__ == "__main__":
    main()
