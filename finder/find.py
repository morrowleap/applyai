#!/usr/bin/env python3
import argparse
import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
from rich.console import Console
from rich.table import Table

from scorer import score_job

console = Console()


def dismiss_modal(page) -> None:
    """Close the LinkedIn sign-in modal if present."""
    try:
        close_btn = page.query_selector("button.modal__dismiss, button[aria-label='Dismiss'], button.sign-in-modal__outlet-btn--close, [data-tracking-control-name='public_jobs_contextual-sign-in-modal_modal_dismiss']")
        if close_btn:
            close_btn.click()
            time.sleep(0.5)
            return
        # Fallback: press Escape
        page.keyboard.press("Escape")
        time.sleep(0.5)
    except Exception:
        pass


def scrape_jobs(query: str, location: str, limit: int) -> list[dict]:
    url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location={location}&f_TPR=r86400"
    jobs = []

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
        console.print(f"[cyan]Opening LinkedIn jobs search...[/cyan]")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)

        # Dismiss any login modal on initial load
        dismiss_modal(page)

        # Scroll to load more results
        for _ in range(max(1, limit // 10)):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
            dismiss_modal(page)

        # Collect job cards
        cards = page.query_selector_all("div.base-card")
        console.print(f"[cyan]Found {len(cards)} job cards, processing up to {limit}...[/cyan]")

        for card in cards[:limit]:
            try:
                title_el = card.query_selector("h3.base-search-card__title")
                company_el = card.query_selector("h4.base-search-card__subtitle")
                location_el = card.query_selector("span.job-search-card__location")
                link_el = card.query_selector("a.base-card__full-link")

                title = title_el.inner_text().strip() if title_el else "Unknown"
                company = company_el.inner_text().strip() if company_el else "Unknown"
                location_text = location_el.inner_text().strip() if location_el else "Unknown"
                job_url = link_el.get_attribute("href") if link_el else ""

                # Click card to load description in right panel
                description = ""
                try:
                    card.click()
                    time.sleep(1.5)
                    dismiss_modal(page)
                    desc_el = page.query_selector("div.description__text")
                    if not desc_el:
                        desc_el = page.query_selector("div.show-more-less-html__markup")
                    if desc_el:
                        description = desc_el.inner_text().strip()
                except PWTimeoutError:
                    pass
                except Exception:
                    pass

                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location_text,
                    "url": job_url,
                    "description": description,
                })
            except Exception as e:
                console.print(f"[yellow]Skipping card: {e}[/yellow]")
                continue

        browser.close()

    return jobs


def main():
    parser = argparse.ArgumentParser(description="Find and score LinkedIn jobs")
    parser.add_argument("--query", default="java backend engineer", help="Job search query")
    parser.add_argument("--location", default="remote", help="Job location")
    parser.add_argument("--limit", type=int, default=25, help="Max jobs to process")
    args = parser.parse_args()

    console.print(f"[bold green]Job Finder[/bold green] — query: [bold]{args.query}[/bold], location: [bold]{args.location}[/bold], limit: {args.limit}")

    jobs = scrape_jobs(args.query, args.location, args.limit)

    if not jobs:
        console.print("[red]No jobs found.[/red]")
        sys.exit(1)

    console.print(f"\n[cyan]Scoring {len(jobs)} jobs via bridge...[/cyan]")
    results = []
    for i, job in enumerate(jobs, 1):
        console.print(f"  [{i}/{len(jobs)}] Scoring: {job['title']} @ {job['company']}...")
        scored = score_job(job["title"], job["company"], job["description"])
        results.append({**job, **scored})

    results.sort(key=lambda x: x.get("score", 0), reverse=True)

    # Print table
    table = Table(title="Job Matches (ranked by score)", show_lines=True)
    table.add_column("#", style="dim", width=3)
    table.add_column("Score", style="bold green", width=6)
    table.add_column("Title", style="bold", max_width=30)
    table.add_column("Company", max_width=20)
    table.add_column("Location", max_width=15)
    table.add_column("Reason", max_width=40)
    table.add_column("URL", max_width=50)

    for i, r in enumerate(results, 1):
        score_val = r.get("score", 0)
        color = "green" if score_val >= 7 else ("yellow" if score_val >= 4 else "red")
        table.add_row(
            str(i),
            f"[{color}]{score_val}[/{color}]",
            r["title"],
            r["company"],
            r["location"],
            r.get("reason", ""),
            r["url"][:60] if r["url"] else "",
        )

    console.print(table)

    # Save to jobs.json
    out_path = Path(__file__).parent / "jobs.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    console.print(f"\n[green]Saved {len(results)} jobs to {out_path}[/green]")
    console.print("\n[bold]Top pick URL:[/bold]")
    if results:
        console.print(f"  {results[0]['url']}")
        console.print(f"\nTo apply: [cyan]cd ../applier && ./run.sh \"{results[0]['url']}\"[/cyan]")


if __name__ == "__main__":
    main()


claude --resume 580b5384-f92e-4969-9dcd-6312bcc14039 
claude --resume 580b5384-f92e-4969-9dcd-6312bcc14039