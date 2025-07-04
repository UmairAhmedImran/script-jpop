# Use async_playwright for async operations
from playwright.async_api import async_playwright
import os
import asyncio

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Using system environment variables only.")
    print("Install with: pip install python-dotenv")


async def extract_links(page):
    # Wait for the table to appear
    try:
        print("Waiting for the torrent table to be visible.")
        await page.wait_for_selector(
            "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//div[@id='ajax_torrents']//table[@class='torrent_table']",
            timeout=15000,
            state='visible'
        )
    except Exception as e:
        print(f"Error or timeout while waiting for the table: {e}")
        return []

    # Find all rows in the table
    tr_elements = await page.query_selector_all(
        "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//div[@id='ajax_torrents']//table[@class='torrent_table']//tbody//tr"
    )
    print(f"Total <tr> tags found: {len(tr_elements)}")

    download_links = []

    # Loop through each <tr> and find the download link, name, and size
    for index, tr in enumerate(tr_elements):
        try:
            # Find the download link within the current <tr>
            download_a_tag = await tr.query_selector("span a[title*='Download']")
            if download_a_tag:
                href = await download_a_tag.get_attribute('href')

                # Extract the name from a <td> that contains an <a> tag with title including "View Torrent"
                name_tag = await tr.query_selector("td a[title*='View Torrent']")
                name = await name_tag.inner_text() if name_tag else None

                # Extract the size from a <td> with class 'nobr' and no title attribute
                size_tag = await tr.query_selector("td.nobr:not([title])")
                size = await size_tag.inner_text() if size_tag else None

                download_links.append((href, name, size))
                print(
                    f"Found download link for torrent {index + 1}: {href}, Name: {name}, Size: {size}")
            else:
                print(f"No download link found for torrent {index + 1}.")
        except Exception as e:
            print(f"Error processing row {index + 1}: {e}")

    return download_links


async def check_and_navigate_next_page(page):
    try:
        # Check if the "next" button is available within a <strong> element
        next_button = await page.query_selector("//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//div[@id='ajax_torrents']//div[@class='linkbox']//strong[contains(text(), 'Next')]")
        if next_button:
            print("Navigating to the next page.")
            await next_button.click()  # Click the next button
            # Wait for the page to load fully
            await page.wait_for_load_state('networkidle')
            return True
        else:
            print("No more pages to navigate.")
            return False
    except Exception as e:
        print(f"Error navigating to next page: {e}")
        return False


async def process_torrents(page):
    all_download_links = []

    # Loop through torrent pages until there are no more pages
    while True:
        # Extract links on the current page
        download_links = await extract_links(page)
        all_download_links.extend(download_links)

        # Check if more pages exist and navigate
        if not await check_and_navigate_next_page(page):
            break

    # Write all download links to a file with a pipe delimiter
    with open('download_links.txt', 'w') as f:
        for link, name, size in all_download_links:
            f.writelines(f"{link}|{name}|{size}\n")

    return all_download_links


async def main():
    # Initialize the total link counter
    total_links_counter = 0

    async with async_playwright() as p:
        download_dir = "downloads"
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        browser = await p.chromium.launch(headless=False, args=[
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-extensions',
            '--disable-infobars',
            '--disable-browser-side-navigation',
            '--disable-features=VizDisplayCompositor',
            '--hide-scrollbars',
            '--window-size=1920,1080',
        ])

        # Launch the browser with download directory set
        browser = await p.chromium.launch(headless=False)
        # Accept downloads
        context = await browser.new_context(accept_downloads=True)
        # context.set_default_download_path(download_dir)  # Set download path

        page = await context.new_page()

        # Navigate to the login page
        await page.goto("https://jpopsuki.eu/login.php")

        # Get username and password from environment variables
        username = os.getenv("JPOPSUKI_USERNAME")
        password = os.getenv("JPOPSUKI_PASSWORD")

        if not username or not password:
            print(
                "Error: JPOPSUKI_USERNAME and JPOPSUKI_PASSWORD environment variables must be set")
            await browser.close()
            return

        # Log in by filling in the username and password fields
        await page.fill('input[name="username"]', username)
        await page.fill('input[name="password"]', password)
        await page.click('input[class="submit"]')

        # Wait for the page to load and check login
        try:
            await page.wait_for_selector('div#wrapper', timeout=300000)
            print("Login successful.")
        except Exception as e:
            print(f"Login failed: {e}")
            await browser.close()
            return

        # Retry mechanism for navigating to the advanced search page
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await page.goto("https://jpopsuki.eu/torrents.php?", timeout=60000)
                await page.wait_for_load_state('networkidle')
                print("Navigated to the basic search page successfully.")
                break
            except Exception as e:
                print(
                    f"Error loading the advanced search page (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    print("Retrying...")
                    await asyncio.sleep(2)
                else:
                    print("Max retries reached. Exiting.")
                    await browser.close()
                    return

        # Wait for the search link to appear and click it
        await page.wait_for_selector(
            "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//form[@id='torrents_filter']//b/center/a",
            timeout=60000)
        await page.click(
            "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//form[@id='torrents_filter']//b/center/a")

        # Delay for the page to load
        await asyncio.sleep(2)

        # Get search parameters from environment variables
        search_string = os.getenv("JPOPSUKI_SEARCH_STRING", "")
        tags_input = os.getenv("JPOPSUKI_TAGS", "")
        tags = [tag.strip() for tag in tags_input.split(
            ',') if tag.strip()] if tags_input else []

        # Get category selections from environment variables
        categories = os.getenv("JPOPSUKI_CATEGORIES", "")
        selected_categories = [cat.strip() for cat in categories.split(
            ',') if cat.strip()] if categories else []

        # Get order selection from environment variables
        order = os.getenv("JPOPSUKI_ORDER", "desc").strip().lower()

        print(f"Search parameters:")
        print(f"  Search string: '{search_string}'")
        print(f"  Tags: {tags}")
        print(f"  Categories: {selected_categories}")
        print(f"  Order: {order}")

        if search_string:
            await page.fill('input[name="searchstr"]', search_string)
        if tags:
            await page.fill('input[name="searchtags"]', ', '.join(tags))

        # Select categories
        for cat in selected_categories:
            cat_id = f"cat_{cat.strip()}"
            await page.check(f'input[id="{cat_id}"]')

        # Select order
        if order in ['asc', 'desc']:
            await page.select_option('select[name="order_way"]', order)

        # Submit the form
        await page.click("//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//form[@id='torrents_filter']//div[@id='search_box']//div[@class='filter_torrents']//div[@class='box pad']//div[@class='submit']//input[@type='submit']")

        # Process torrents and extract all download links
        all_download_links = await process_torrents(page)

        await browser.close()

# Run the async main function
asyncio.run(main())
