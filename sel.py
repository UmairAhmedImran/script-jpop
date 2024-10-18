# Use async_playwright for async operations
from playwright.async_api import async_playwright
import os
import asyncio

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
    tr_elements = tr_elements[2:5]
    print(f"Total <tr> tags found: {len(tr_elements)}")

    download_links = []

    # Loop through each <tr> and find the download link
    for index, tr in enumerate(tr_elements):
        try:
            # Find the download link within the current <tr>
            download_a_tag = await tr.query_selector("span a[title*='Download']")
            if download_a_tag:
                href = await download_a_tag.get_attribute('href')
                download_links.append(href)
                print(f"Found download link for torrent {index + 1}: {href}")
            else:
                print(f"No download link found for torrent {index + 1}.")
        except Exception as e:
            print(f"Error processing row {index + 1}: {e}")

    return download_links

async def check_and_navigate_next_page(page):
    try:
        # Check if the "next" button is available
        next_button = await page.query_selector("//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//div[@id='ajax_torrents']//div[@class='linkbox']//a[@class='next']")
        if next_button:
            print("Navigating to the next page.")
            await next_button.click()  # Click the next button
            await page.wait_for_load_state('networkidle')  # Wait for the page to load fully
            return True
        else:
            print("No more pages to navigate.")
            return False
    except Exception as e:
        print(f"Error navigating to next page: {e}")
        return False

async def process_torrents(page):
    # Loop through torrent pages until there are no more pages
    while True:
        success = await extract_links(page)  # Download all links on the current page
        if not success or not await check_and_navigate_next_page(page):  # Check if more pages exist
            break



async def main():
    # Initialize the total link counter
    total_links_counter = 0

    async with async_playwright() as p:  # Use async_playwright instead of sync_playwright
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
        context = await browser.new_context(accept_downloads=True)  # Accept downloads
        # context.set_default_download_path(download_dir)  # Set download path

        page = await context.new_page()

        # Navigate to the login page
        await page.goto("https://jpopsuki.eu/login.php")

        # Get username and password from user input
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        # Log in by filling in the username and password fields
        await page.fill('input[name="username"]', username)
        await page.fill('input[name="password"]', password)
        await page.click('input[class="submit"]')

        # Wait for the page to load and check login
        try:
            await page.wait_for_selector('div#wrapper', timeout=300000)
            print("Login successful.")  # Confirm successful login
        except Exception as e:
            print(f"Login failed: {e}")
            await browser.close()
            return

        # Retry mechanism for navigating to the advanced search page
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await page.goto("https://jpopsuki.eu/torrents.php?action=advanced", timeout=60000)  # Increased timeout
                await page.wait_for_load_state('networkidle')  # Wait for the page to fully load
                print("Navigated to the advanced search page successfully.")
                break  # Exit the loop if successful
            except Exception as e:
                print(f"Error loading the advanced search page (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    print("Retrying...")
                    await asyncio.sleep(2)  # Optional delay before retrying
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
            await page.fill('input[name="artistname"]', artist_name)
        if album_name:
            await page.fill('input[name="torrentname"]', album_name)
        if remaster_title:
            await page.fill('input[name="remastertitle"]', remaster_title)
        if tags:
            await page.fill('input[name="searchtags"]', ', '.join(tags))

        # Submit the form
        await page.click("//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//form[@id='torrents_filter']//div[@id='search_box']//div[@class='filter_torrents']//div[@class='box pad']//div[@class='submit']//input[@type='submit']")

        await process_torrents(page)

        # Extract download links
        download_links = await extract_links(page)

        # Pass download links to Scrapy
        # This could be done by writing to a file, database, or directly calling a Scrapy function
        with open('download_links.txt', 'w') as f:
            for link in download_links:
                f.write(f"{link}\n")

        await browser.close()  # Ensure the browser closes after processing


# Run the async main function
asyncio.run(main())
