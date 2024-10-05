import time
from playwright.sync_api import sync_playwright


def process_table(page, total_links_counter):
    # Wait for the table to be visible after loading the page
    try:
        print("Waiting for the torrent table to be visible.")
        page.wait_for_selector(
            "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//div[@id='ajax_torrents']//table[@class='torrent_table']",
            timeout=15000,  # Increased timeout to 15 seconds
            state='visible'  # Ensure the element is visible
        )
    except Exception as e:
        print(f"Error or timeout while waiting for the table: {e}")
        return False  # Stop if there's an error or timeout

    # Fetch all <tr> elements within the table
    tr_elements = page.query_selector_all(
        "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//div[@id='ajax_torrents']//table[@class='torrent_table']//tr"
    )

    print(f"Total <tr> tags found: {len(tr_elements)}")
    # total_links_counter.append(len(tr_elements))

    # Loop over each row and check the 4th <td> and the 2nd <a> tag inside it
    for tr in tr_elements:
        try:
            # Get the 4th <td> in the row
            td_4th = tr.query_selector("td:nth-child(4)")
            if td_4th:
                # Find all <a> tags within the 4th <td>
                a_tags = td_4th.query_selector_all("a")
                if len(a_tags) >= 2:
                    # Get the 2nd <a> tag and extract its text content
                    second_a_tag_text = a_tags[1].inner_text()
                    print(f"Found name: {second_a_tag_text}")
                else:
                    print("No name: Less than 2 <a> tags found in the 4th <td>")
            else:
                print("No name: 4th <td> not found")
        except Exception as e:
            print(f"Error processing row: {e}")

    return len(tr_elements) > 0  # Return True if there are rows


def check_and_navigate_next_page(page):
    # Check if there's an <a> tag directly after a <strong> tag in the "linkbox" div
    next_link = page.query_selector(
        "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//div[@id='ajax_torrents']//div[@class='linkbox']//strong/following-sibling::a[1]"
    )

    if next_link:
        print("Clicking the next page link after <strong>.")
        next_link.click()  # Simulate a click on the <a> tag that comes after <strong>

        # Wait for new content (table rows) to load
        try:
            page.wait_for_selector(
                "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//div[@id='ajax_torrents']//table[@class='torrent_table']",
                timeout=10000  # Adjust timeout as needed
            )
            return True  # Successfully loaded the next page
        except Exception as e:
            print(
                f"Timeout or error occurred while waiting for the next page: {e}")
            return False  # Stop if there's a timeout or error
    else:
        print("No <a> tag found after <strong>. This is the last page.")
        return False  # No more pages to navigate, the process is complete


def main():
    # Initialize the total link counter
    total_links_counter = 0

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
            timeout=60000)
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

        # Fill in search parameters if provided
        if artist_name:
            page.fill('input[name="artistname"]', artist_name)
        if album_name:
            page.fill('input[name="torrentname"]', album_name)
        if remaster_title:
            page.fill('input[name="remastertitle"]', remaster_title)
        if tags:
            page.fill('input[name="searchtags"]', ', '.join(tags))

        # Submit the form
        page.click(
            "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//form[@id='torrents_filter']//div[@id='search_box']//div[@class='filter_torrents']//div[@class='box pad']//div[@class='submit']//input[@type='submit']",
            timeout=60000)

        # Process the search results table
        results_found = process_table(page, total_links_counter)
        print(results_found)
        # Keep checking for the next page link and processing until no more results
        while results_found:
            if check_and_navigate_next_page(page):
                results_found = process_table(page, total_links_counter)
            else:
                break

        print(f"Total number of valid links found: {total_links_counter}")

        # Close browser
        browser.close()


if __name__ == "__main__":
    main()
