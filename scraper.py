"""
╔══════════════════════════════════════════════════════════════╗
║         Books to Scrape — Professional Web Scraper           ║
║         CodeAlpha Data Analytics Internship — Task 1         ║
╚══════════════════════════════════════════════════════════════╝

Website  : https://books.toscrape.com
Author   : Samman
Date     : 2025
Libraries: requests, beautifulsoup4, lxml, pandas, tqdm
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import logging
from datetime import datetime
from tqdm import tqdm


# ══════════════════════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════════════════════
BASE_URL    = "https://books.toscrape.com/"
OUTPUT_DIR  = "data"
OUTPUT_CSV  = os.path.join(OUTPUT_DIR, "books_full.csv")
LOG_FILE    = os.path.join(OUTPUT_DIR, "scraper.log")
DELAY       = 0.3          # seconds between requests (be polite)
TIMEOUT     = 10           # request timeout in seconds

RATING_MAP  = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ══════════════════════════════════════════════════════════════
#  LOGGING SETUP
# ══════════════════════════════════════════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════

def get_soup(url: str) -> BeautifulSoup | None:
    """
    Fetch a URL and return a BeautifulSoup object.
    Returns None if the request fails.
    """
    headers = {"User-Agent": "Mozilla/5.0 (BookScraper/3.0; CodeAlpha Internship)"}
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        response.encoding = "utf-8"   # force UTF-8 so £ never becomes 'Â£'
        return BeautifulSoup(response.text, "lxml")
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection failed: {url}")
    except requests.exceptions.Timeout:
        logger.error(f"Request timed out: {url}")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error {e.response.status_code}: {url}")
    return None


def clean_price(raw: str) -> float:
    """
    Strip currency symbols and return a clean float.
    Handles both '£12.99' and corrupted 'Â£12.99' formats.
    """
    cleaned = raw.encode("ascii", errors="ignore").decode()
    cleaned = "".join(c for c in cleaned if c.isdigit() or c == ".")
    return float(cleaned) if cleaned else 0.0


def parse_availability(article) -> str:
    """
    Robustly extract availability status from a book article tag.
    books.toscrape.com uses two possible CSS classes:
      - 'instock availability'   → In stock
      - 'outofstock availability' → Out of stock
    We try both, then fall back to plain text search.
    """
    # Try 'In stock' class first
    tag = article.find("p", class_="instock availability")
    if tag:
        return "In stock"

    # Try 'Out of stock' class
    tag = article.find("p", class_="outofstock availability")
    if tag:
        return "Out of stock"

    # Generic fallback — grab any availability paragraph
    tag = article.find("p", class_="availability")
    if tag:
        return tag.text.strip()

    return "Unknown"


def parse_book(article, category: str) -> dict:
    """
    Extract all fields from one <article class='product_pod'> tag.
    Handles both 'In stock' and 'Out of stock' books correctly.
    Returns a dictionary with 5 fields per book.
    """
    title    = article.h3.a["title"]
    price    = article.find("p", class_="price_color").text.strip()
    rating   = RATING_MAP.get(article.p["class"][1], 0)
    avail    = parse_availability(article)

    return {
        "Title"       : title,
        "Category"    : category,
        "Price (£)"   : clean_price(price),
        "Rating"      : rating,
        "Availability": avail,
    }


def get_total_pages(soup: BeautifulSoup) -> int:
    """Return the total number of pages for a category."""
    pager = soup.find("li", class_="current")
    if pager:
        # Text format: "Page 1 of 3"
        text = pager.text.strip()
        return int(text.split("of")[-1].strip())
    return 1


def scrape_category(cat_name: str, cat_url: str) -> list:
    """
    Scrape every paginated page of one category.
    Returns a list of book dictionaries.
    """
    books    = []
    page_url = cat_url
    page_num = 1

    while page_url:
        soup = get_soup(page_url)
        if soup is None:
            logger.warning(f"Skipping page {page_num} of '{cat_name}' — failed to fetch.")
            break

        articles = soup.find_all("article", class_="product_pod")
        for article in articles:
            books.append(parse_book(article, cat_name))

        # ── Follow pagination ────────────────────────────
        next_btn = soup.find("li", class_="next")
        if next_btn:
            next_href = next_btn.a["href"]
            base      = page_url.rsplit("/", 1)[0]
            page_url  = f"{base}/{next_href}"
            page_num += 1
        else:
            page_url = None

        time.sleep(DELAY)

    return books


def get_categories(home_soup: BeautifulSoup) -> list[tuple]:
    """
    Parse the left-side nav to get all category names and URLs.
    Returns list of (name, url) tuples.
    """
    nav = home_soup.find("ul", class_="nav-list").find("ul")
    return [
        (li.a.text.strip(), BASE_URL + li.a["href"])
        for li in nav.find_all("li")
    ]


def save_csv(df: pd.DataFrame, path: str) -> None:
    """Save DataFrame to CSV with UTF-8 BOM (Excel-compatible)."""
    df.to_csv(
        path,
        index=True,
        index_label="No.",
        encoding="utf-8-sig",   # BOM makes Excel open £ correctly
    )
    size_kb = os.path.getsize(path) / 1024
    logger.info(f"CSV saved → {os.path.abspath(path)}  ({size_kb:.1f} KB)")


def print_summary(df: pd.DataFrame, start_time: datetime) -> None:
    """Print a formatted summary of the scraped dataset."""
    elapsed = (datetime.now() - start_time).seconds
    sep = "═" * 60

    print(f"\n{sep}")
    print("  📊  SCRAPING SUMMARY")
    print(sep)
    print(f"  Total books scraped : {len(df):,}")
    print(f"  Categories covered  : {df['Category'].nunique()}")
    print(f"  Price range (£)     : {df['Price (£)'].min():.2f}  →  {df['Price (£)'].max():.2f}")
    print(f"  Average price (£)   : {df['Price (£)'].mean():.2f}")
    print(f"  Average rating      : {df['Rating'].mean():.2f} / 5")
    print(f"  Missing values      : {df.isnull().sum().sum()}")
    print(f"  Time taken          : {elapsed}s")
    print(f"  Output file         : {os.path.abspath(OUTPUT_CSV)}")
    print()
    print("  📦  Availability Breakdown:")
    for status, count in df["Availability"].value_counts().items():
        pct = count / len(df) * 100
        print(f"      {status:<20} {count:>4} books  ({pct:.1f}%)")
    print(sep)

    print("\n  📌  Top 5 Categories by Book Count:")
    top5 = df["Category"].value_counts().head(5)
    for cat, cnt in top5.items():
        print(f"      {cat:<30} {cnt} books")

    print("\n  💰  Top 5 Most Expensive Categories (avg price):")
    top5_price = df.groupby("Category")["Price (£)"].mean().sort_values(ascending=False).head(5)
    for cat, price in top5_price.items():
        print(f"      {cat:<30} £{price:.2f}")

    print(f"\n  ✅  Dataset is ready for EDA (Task 2)!")
    print(f"{sep}\n")


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════
def main():
    start_time = datetime.now()

    print("\n" + "═" * 60)
    print("   📚  Books to Scrape — Professional Web Scraper")
    print("   🔧  CodeAlpha Data Analytics Internship — Task 1")
    print("═" * 60 + "\n")

    # ── Step 1: Fetch homepage & category list ────────────
    logger.info("Fetching homepage and category list...")
    home = get_soup(BASE_URL)
    if home is None:
        logger.critical("Cannot reach books.toscrape.com. Check your internet connection.")
        return

    categories = get_categories(home)
    logger.info(f"Found {len(categories)} categories to scrape.\n")

    # ── Step 2: Scrape all categories with progress bar ──
    all_books = []

    with tqdm(categories, desc="Scraping categories", unit="cat",
              bar_format="{l_bar}{bar:30}{r_bar}") as pbar:
        for cat_name, cat_url in pbar:
            pbar.set_postfix({"current": cat_name[:20]})
            cat_books = scrape_category(cat_name, cat_url)
            all_books.extend(cat_books)
            logger.info(f"  ✔  {cat_name:<30} → {len(cat_books)} books")

    # ── Step 3: Build & clean DataFrame ──────────────────
    logger.info("\nBuilding DataFrame...")
    df = pd.DataFrame(all_books)
    df.index = df.index + 1      # start row numbers at 1
    df["Rating_Stars"] = df["Rating"].map({1:"⭐", 2:"⭐⭐", 3:"⭐⭐⭐", 4:"⭐⭐⭐⭐", 5:"⭐⭐⭐⭐⭐"})

    # ── Step 4: Save CSV ──────────────────────────────────
    save_csv(df.drop(columns=["Rating_Stars"]), OUTPUT_CSV)

    # ── Step 5: Print summary ─────────────────────────────
    print_summary(df, start_time)

    # ── Step 6: Quick preview ─────────────────────────────
    print("  Preview (first 5 rows):\n")
    print(df[["Title", "Category", "Price (£)", "Rating", "Availability"]].head().to_string())
    print()


if __name__ == "__main__":
    main()
