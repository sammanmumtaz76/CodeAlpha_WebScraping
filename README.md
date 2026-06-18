# Books to Scrape — Web Scraper

 **CodeAlpha Data Analytics Internship — Task 1: Web Scraping**

A professional Python web scraper that extracts data from [books.toscrape.com](https://books.toscrape.com) — scraping **1,000 books** across **50 categories** with full pagination support, logging, and a clean CSV output ready for EDA.


## Project Structure
CodeAlpha_WebScraping/
│
├── scraper.py           ← Main scraper script
├── requirements.txt     ← Python dependencies
├── README.md            ← Project documentation
│
└── data/
    ├── books_full.csv   ← Final scraped dataset (1000 rows)
    └── scraper.log      ← Auto-generated run log

## Dataset Overview

| Column | Type | Description |
|--------|------|-------------|
| `No.` | int | Serial number (1–1000) |
| `Title` | str | Full book title |
| `Category` | str | Genre / category name |
| `Price (£)` | float | Price in British Pounds |
| `Rating` | int | Star rating (1 = lowest, 5 = highest) |
| `Availability` | str | Stock status |

**Dataset Stats:**
- Total books: **1,000**
- Categories: **50**
- Price range: **£10.00 – £59.99**
- Ratings: **1 to 5 stars**
- Missing values: **0**

 **Note on Availability:** `books.toscrape.com` is a sandboxed practice website where all 1,000 listed books are marked "In stock" by design. The scraper is fully built to capture **both** `In stock` and `Out of stock` statuses using dual CSS class detection (`instock availability` and `outofstock availability`) — so it will work correctly on any real bookstore site with mixed stock data.

## How to Run

### 1. Clone the repository
bash
git clone https://github.com/YOUR_USERNAME/CodeAlpha_WebScraping.git
cd CodeAlpha_WebScraping

**Note:** The `data/books_full.csv` file is included in this repository so evaluators can view the dataset directly without running the scraper.

### 2. Install dependencies
bash
pip install -r requirements.txt

### 3. Run the scraper
bash
python scraper.py

### 4. Output
The scraped data is saved to `data/books_full.csv` automatically.

## Technical Features

| Feature | Detail |
|---------|--------|
| **Library** | `BeautifulSoup4` + `requests` |
| **Pagination** | Auto-follows all next-page links per category |
| **Encoding fix** | Forces UTF-8 so `£` symbol renders correctly |
| **Progress bar** | `tqdm` live progress while scraping |
| **Logging** | Saves timestamped log to `data/scraper.log` |
| **Error handling** | Handles timeouts, HTTP errors, connection failures |
| **Polite scraping** | 0.3s delay between requests |
| **Excel compatible** | UTF-8 BOM encoding so CSV opens correctly in Excel |
## Key Technical Decisions

**Why BeautifulSoup over Scrapy?**
BeautifulSoup is lightweight and perfect for a single-domain scraper like this. Scrapy would add unnecessary complexity for 50 categories.

**Why `utf-8-sig` encoding?**
Excel on Windows misreads plain `utf-8` and shows `£` as `Â£`. The BOM signature (`utf-8-sig`) fixes this automatically.

**Why `time.sleep(0.3)`?**
Ethical scraping — we avoid hammering the server with rapid requests.


## Next Steps (Task 2 — EDA)

This dataset will be used for Exploratory Data Analysis including:
- Price distribution across categories
- Rating vs Price correlation
- Top value-for-money books (custom Value Score metric)
- Category performance bubble chart

## Dependencies

requests==2.31.0
beautifulsoup4==4.12.3
lxml==5.2.1
pandas==2.2.2
tqdm==4.66.4

## Author

Samman Mumtaz
Data Analytics Intern CodeAlpha
# CodeAlpha_WebScraping
