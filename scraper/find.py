#!/usr/bin/env python3
import os
import threading
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
    try:
        resp = requests.get(f"{BRIDGE_URL}/keyword", timeout=60)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        print(f"Bridge is not running. Start it first: cd bridge && ./run.sh")
        raise SystemExit(1)
    data = resp.json()
    print(f"Keyword: {data['keyword']} — {data['rationale']}")
    return data["keyword"]


def score_job(title: str, about: str, link: str) -> dict | None:
    try:
        resp = requests.post(
            f"{BRIDGE_URL}/score",
            json={"title": title, "description": about, "link": link},
            timeout=180,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  [score failed: {e}]")
        return None


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

                # Collect job IDs and links now in DOM (stable across re-renders)
                job_cards = page.eval_on_selector_all(
                    "li[data-occludable-job-id]",
                    """els => els.map(el => ({
                        id: el.getAttribute('data-occludable-job-id'),
                        link: (el.querySelector('a.job-card-container__link') || {}).href || null
                    }))""",
                )
                print(f"\n--- Page {page_num} — {len(job_cards)} jobs ---")

                for i, job in enumerate(job_cards):
                    job_id = job["id"]
                    job_link = (
                        job["link"] or f"https://www.linkedin.com/jobs/view/{job_id}/"
                    )
                    try:
                        # Scroll card into view — forces LinkedIn to re-render it into DOM
                        card = page.locator(f"li[data-occludable-job-id='{job_id}']")
                        card.scroll_into_view_if_needed()
                        time.sleep(0.3)
                        card.click()

                        # Wait indefinitely for the loading skeleton to disappear, printing progress
                        wait_start = time.time()
                        while True:
                            try:
                                page.wait_for_selector(
                                    ".jobs-description__details [aria-busy='true']",
                                    state="hidden",
                                    timeout=5000,
                                )
                                break
                            except Exception:
                                """
                                TODO: Find the reason for this indefinite about section loading page,
                                This maybe an error from linkedin side
                                """
                                elapsed = int(time.time() - wait_start)
                                ans = input(
                                    f"\n  [{i + 1}/{len(job_cards)}] Loading {job_link} ({elapsed}s) — s + Enter to skip, Enter to keep waiting: "
                                )
                                if ans.strip().lower() == "s":
                                    raise Exception("Skipped by user")

                        title_el = page.query_selector("h1.t-24.t-bold")
                        about_el = page.query_selector("#job-details")

                        title = title_el.inner_text().strip() if title_el else "N/A"
                        about = about_el.inner_text().strip() if about_el else "N/A"

                        score = score_job(title, about, job_link)
                        score_line = ""
                        if score:
                            s = score.get("score", "?")
                            reason = score.get("reason", "")
                            color = "32" if s >= 7 else "33" if s >= 4 else "31"
                            score_line = f"\n\033[1;{color}mScore: {s}/10\033[0m — {reason}"

                        jobs.append({"title": title, "about": about, "link": job_link, "score": score})
                        print(
                            f"\n[{i + 1}/{len(job_cards)}] \033[1;32m{title}\033[0m\n\033[36m{job_link}\033[0m{score_line}"
                        )
                    except Exception as e:
                        print(f"\n[{i + 1}/{len(job_cards)}] Skipping {job_link}: {e}")
                        continue

                # Check for Next button
                next_btn = page.locator("button[aria-label='View next page']")
                if next_btn.count() == 0 or not next_btn.is_enabled():
                    print(f"\nNo more pages. Total scraped: {len(jobs)} jobs.")
                    break

                answer = input(f"\nGo to page {page_num + 1}? [Y/n]: ").strip().lower()
                if answer == "n":
                    print("Stopping.")
                    break

                next_btn.click()
                page_num += 1
                time.sleep(2)

            print(f"\nDone. Scraped {len(jobs)} jobs total.")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
