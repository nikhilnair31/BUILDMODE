import time
import random
from playwright.sync_api import sync_playwright

def clean_data(tweet_data):
    # print(f'tweet_data: {tweet_data}')

    full_text = tweet_data["legacy"]["full_text"]
    
    media = tweet_data["legacy"]["entities"]["media"]
        
    media_content_urls = [media_item["media_url_https"] for media_item in media] if media else "-"
    media_content_urls_str = ' | '.join(media_content_urls)
    
    return (full_text, media_content_urls_str)

def scrape_tweet(url: str) -> dict:
    _xhr_calls = []

    def intercept_response(response):
        if response.request.resource_type == "xhr":
            _xhr_calls.append(response)
        
        return response

    with sync_playwright() as pw:
        #TODO: Might need to rotate proxies eventually
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": random.randint(1280, 1920), "height": random.randint(720, 1080)},
            user_agent=f"Mozilla/5.0 (Windows NT {random.choice(['10.0', '6.1'])}; Win64; x64) AppleWebKit/537.36 "
                       f"(KHTML, like Gecko) Chrome/{random.randint(90, 100)}.0.{random.randint(3000, 4000)} Safari/537.36"
        )
        page = context.new_page()

        # enable background request intercepting:
        page.on("response", intercept_response)
        
        # Add a small random delay to mimic human browsing behavior
        delay = random.uniform(1, 3)
        print(f"Navigating to URL with {delay:.2f} seconds delay...")
        time.sleep(delay)

        # go to url and wait for the page to load
        page.goto(url)
        
        try:
            page.wait_for_selector("[data-testid='tweet']")

            # Wait a bit more to mimic human scrolling behavior
            page.mouse.wheel(0, random.randint(300, 500))
            time.sleep(random.uniform(0.5, 2))

            # Filter XHR calls for tweet data
            tweet_calls = [f for f in _xhr_calls if "TweetResultByRestId" in f.url]
            for xhr in tweet_calls:
                data = xhr.json()
                result = data['data']['tweetResult']['result']
                clean_result = clean_data(result)
                return clean_result
        finally:
            browser.close()

if __name__ == "__main__":
    print(scrape_tweet("https://x.com/emmettshine/status/1849458044830089470"))