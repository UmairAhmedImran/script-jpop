import time
from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--window-size=1920,1080',
            '--disable-extensions',
            '--disable-infobars',
            '--disable-browser-side-navigation',
            '--disable-features=VizDisplayCompositor',
            '--hide-scrollbars',
            '--single-process',
            '--disable-software-rasterizer'
        ])
        context = browser.new_context()
        page = context.new_page()

        # Navigate to the login page
        page.goto("https://jpopsuki.eu/login.php")

        # Get username and password from user input
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        # Log in by filling in the username and password fields
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        # Click the submit button
        page.click('input[class="submit"]')

        # Wait for the page to load and check login
        page.wait_for_selector('div#wrapper')

        # Navigate to the advanced search page
        try:
            page.goto(
                "https://jpopsuki.eu/torrents.php?action=advanced", timeout=60000)
        except Exception as e:
            print(f"Error loading the advanced search page: {e}")
            browser.close()
            return

        # Wait for the search link to appear and click it
        page.wait_for_selector(
            "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//form[@id='torrents_filter']//b/center/a",
            timeout=60000)  # Increase timeout
        page.click(
            "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//form[@id='torrents_filter']//b/center/a")

        # Delay for the page to load
        time.sleep(2)

        # Get search parameters from user input
        artist_name = input("Enter artist name (leave blank if not needed): ")
        album_name = input("Enter album name (leave blank if not needed): ")
        remaster_title = input(
            "Enter remaster title (leave blank if not needed): ")
        tags_input = input(
            "Enter tags separated by commas (leave blank if not needed): ")
        tags = tags_input.split(',') if tags_input else []

        # Debugging: Print the search parameters
        print(
            f"Searching for: Artist: {artist_name}, Album: {album_name}, Remaster: {remaster_title}, Tags: {', '.join(tags)}")

        # Fill in search parameters if provided
        if artist_name:
            page.fill('input[name="artistname"]', artist_name)

        if album_name:
            page.fill('input[name="torrentname"]', album_name)

        if remaster_title:
            page.fill('input[name="remastertitle"]', remaster_title)

        if tags:
            page.fill('input[name="searchtags"]', ', '.join(tags))

        # Submit the form with increased timeout for the click action
        page.click(
            "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//form[@id='torrents_filter']//div[@id='search_box']//div[@class='filter_torrents']//div[@class='box pad']//div[@class='submit']//input[@type='submit']",
            timeout=60000)  # Increase the timeout to 60 seconds

        # Wait for the results to load by checking for a specific element
        page.wait_for_selector(
            "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//div[@id='ajax_torrents']//table[@class='torrent_table']",
            timeout=10000)

        # Check for search results
        rows = page.query_selector_all(
            "//div[@id='ajax_torrents']//table[@class='torrent_table']//tbody/tr")

        # Start from the second row to skip the first one
        for result in rows[1:]:
            tds = result.query_selector_all('td')
            if len(tds) > 3:
                third_td = tds[3]
                a_tags = third_td.query_selector_all('a')
                if len(a_tags) > 1:
                    second_a_tag = a_tags[1]
                    href = second_a_tag.get_attribute('href')
                    if not 'torrent' in href:  # Ensure it's a torrent link
                        # Replace "report" with "torrent" and "reports" with "torrents" in the href
                        corrected_href = href.replace(
                            'report', 'torrent').replace('reports', 'torrents')
                        print(corrected_href)
                    else:
                        print("Not a torrent link:", href)
                else:
                    print("Not found: second <a> tag")
            else:
                print("Not found: third <td>")

        if rows:
            print(f"Found {len(rows)} results.")
        else:
            print("No results found.")

        # Close browser
        browser.close()


if __name__ == "__main__":
    main()
