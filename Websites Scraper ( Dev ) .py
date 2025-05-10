import requests
import json
from bs4 import BeautifulSoup
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

# Read websites from file, one per line, strip whitespace, skip empty lines
with open("websites.txt", "r", encoding="utf-8") as file:
    websites = [line.strip() for line in file if line.strip()]

text_tags = [
    "p", "h1", "h2", "h3", "h4", "h5", "h6", "span", "div", "a", "b", "strong", "i", "em", "u", "s", "mark", "small",
    "sub", "sup", "del", "ins", "abbr", "cite", "code", "samp", "kbd", "var", "pre", "q", "blockquote", "dfn", "time",
    "bdi", "bdo", "label", "button", "output", "legend", "summary", "caption", "td", "th", "li", "dt", "dd",
    "figcaption", "ruby", "rt", "rp", "address", "option", "optgroup", "meter", "progress"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://example.com"
}

def scrape_url(url):
    try:
        with requests.Session() as session:
            session.headers.update(headers)
            resp = session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'html.parser')
            elements = soup.find_all(text_tags)
            text_chunks = [el.get_text(strip=True) for el in elements if el.get_text(strip=True)]
            print(f"Scraped: {url}")
            return url, ' '.join(text_chunks)
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        traceback.print_exc()
        return url, ""

web_dic = {}

# Adjust max_workers as needed (5-20 is typical; too high may get you blocked)
max_workers = min(20, len(websites))

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    future_to_url = {executor.submit(scrape_url, url): url for url in websites}
    for future in as_completed(future_to_url):
        url, text = future.result()
        web_dic[url] = text

# Save to JSON file
with open("web_db.txt", "w", encoding="utf-8") as file:
    json.dump(web_dic, file, ensure_ascii=False, indent=2)
