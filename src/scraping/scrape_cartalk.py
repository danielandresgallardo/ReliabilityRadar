import json
import time
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime

BASE_URL = "https://community.cartalk.com/c/general-discussion/6?page={}"
MAX_PAGES = 10

def extract_thread_id_from_url(url):
    parts = urlparse(url).path.strip("/").split("/")
    return parts[-1] if parts else None

def scrape_cartalk_general_discussion(max_pages=MAX_PAGES):
    threads = []

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        for page_num in tqdm(range(1, max_pages + 1), desc="Scraping forum pages"):
            url = BASE_URL.format(page_num)
            driver.get(url)
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            # Check and adjust selector if needed
            thread_links = soup.select("a.title.raw-link.raw-topic-link")

            for link in tqdm(thread_links, desc=f"Threads on page {page_num}", leave=False):
                thread_title = link.text.strip()
                thread_url = urljoin("https://community.cartalk.com", link.get("href"))
                thread_id = extract_thread_id_from_url(thread_url)

                # Visit thread page
                driver.get(thread_url)
                time.sleep(2)
                thread_soup = BeautifulSoup(driver.page_source, "html.parser")
                post_divs = thread_soup.select("article.boxed.onscreen-post")

                comments = []
                # Variables for original post info:
                orig_author = "Unknown"
                orig_score = 0
                orig_created_utc = None
                orig_body = ""

                for idx, post in enumerate(post_divs):
                    cooked = post.select_one("div.cooked")
                    if not cooked:
                        continue

                    post_text = cooked.get_text(separator="\n", strip=True)  # preserve line breaks better

                    # Extract author
                    author_tag = post.select_one("span.username a[data-user-card]")
                    author = author_tag.text.strip() if author_tag else "Unknown"

                    # Extract created_utc from data-time attribute in milliseconds
                    created_utc = None
                    date_span = post.select_one("a.post-date span[title][data-time]")
                    if date_span and date_span.has_attr("data-time"):
                        try:
                            created_utc = int(date_span["data-time"]) // 1000
                        except ValueError:
                            pass

                    # Extract score (likes count)
                    score = 0
                    like_count_btn = post.select_one("button.post-action-menu__like-count")
                    if like_count_btn:
                        try:
                            score = int(like_count_btn.text.strip())
                        except ValueError:
                            score = 0

                    post_data = {
                        "id": f"{thread_id}-comment-{idx}" if idx > 0 else thread_id,
                        "author": author,
                        "body": post_text,
                        "created_utc": created_utc,
                        "score": score
                    }

                    if idx == 0:
                        # This is the original post, save info directly in thread-level keys
                        orig_author = author
                        orig_score = score
                        orig_created_utc = created_utc
                        orig_body = post_text
                    else:
                        comments.append(post_data)

                threads.append({
                    "id": thread_id,
                    "title": thread_title,
                    "author": orig_author,
                    "url": thread_url,
                    "score": orig_score,
                    "created_utc": orig_created_utc,
                    "selftext": orig_body,
                    "comments": comments
                })

                time.sleep(1)  # polite delay

    finally:
        driver.quit()

    return threads

# Run and save
if __name__ == "__main__":
    data = scrape_cartalk_general_discussion()
    with open("cartalk_general_discussion.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Saved {len(data)} threads to cartalk_general_discussion.json")
