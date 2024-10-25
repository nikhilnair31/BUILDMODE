from playwright.sync_api import sync_playwright

def clean_data(tweet_data):
    print(f'tweet_data: {tweet_data}')

    full_text = tweet_data["legacy"]["full_text"]
    
    media = tweet_data["legacy"]["entities"]["media"]
        
    media_content_urls = [media_item["media_url_https"] for media_item in media] if media else "-"
    media_content_urls_str = ' | '.join(media_content_urls)
    
    return (full_text, media_content_urls_str)

def scrape_tweet(url: str) -> dict:
    _xhr_calls = []

    def intercept_response(response):
        """capture all background requests and save them"""
        # we can extract details from background requests
        if response.request.resource_type == "xhr":
            _xhr_calls.append(response)
        return response

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # enable background request intercepting:
        page.on("response", intercept_response)
        # go to url and wait for the page to load
        page.goto(url)
        page.wait_for_selector("[data-testid='tweet']")

        # find all tweet background requests:
        tweet_calls = [f for f in _xhr_calls if "TweetResultByRestId" in f.url]
        for xhr in tweet_calls:
            data = xhr.json()
            result = data['data']['tweetResult']['result']
            clean_result = clean_data(result)
            return clean_result

if __name__ == "__main__":
    print(scrape_tweet("https://x.com/emmettshine/status/1849458044830089470"))