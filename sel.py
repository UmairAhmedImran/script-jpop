# # Use async_playwright for async operations
# from playwright.async_api import async_playwright
# import asyncio  # Ensure you have this import
# import time
# from playwright.async_api import async_playwright
# import os
# import asyncio


# def process_table(page, total_links_counter):
#     # Wait for the table to be visible after loading the page
#     try:
#         print("Waiting for the torrent table to be visible.")
#         page.wait_for_selector(
#             "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//div[@id='ajax_torrents']//table[@class='torrent_table']",
#             timeout=15000,  # Increased timeout to 15 seconds
#             state='visible'  # Ensure the element is visible
#         )
#     except Exception as e:
#         print(f"Error or timeout while waiting for the table: {e}")
#         return []  # Return empty list if there's an error or timeout

#     # Fetch all <tr> elements within the table
#     tr_elements = page.query_selector_all(
#         "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//div[@id='ajax_torrents']//table[@class='torrent_table']//tr"
#     )

#     print(f"Total <tr> tags found: {len(tr_elements)}")

#     torrents = []  # List to hold torrent details

#     # Loop over each row and check for both "View Torrent" and "Download" links
#     for tr in tr_elements:
#         try:
#             # Locate <a> tags inside the row that have "View Torrent" in their title
#             view_torrent_a_tag = tr.query_selector("a[title*='View Torrent']")
#             view_torrent_text = view_torrent_a_tag.inner_text(
#             ) if view_torrent_a_tag else "No 'View Torrent' link found"

#             # Get the 4th <td> in the row and look for a <span> containing an <a> tag with "Download" in the title
#             td_4th = tr.query_selector("td:nth-child(4)")
#             download_text = "No 'Download' link found"
#             if td_4th:
#                 download_a_tag = td_4th.query_selector(
#                     "span a[title*='Download']")
#                 if download_a_tag:
#                     download_text = download_a_tag.inner_text()

#             # If no download link is found in the 4th <td>, check the first <td>
#             if download_text == "No 'Download' link found":
#                 td_1st = tr.query_selector("td:nth-child(1)")
#                 if td_1st:
#                     download_a_tag = td_1st.query_selector(
#                         "span a[title*='Download']")
#                     if download_a_tag:
#                         download_text = download_a_tag.inner_text()

#             # Get the size from the <td> with class 'nobr'
#             size_element = tr.query_selector("td.nobr")
#             size_text = size_element.inner_text() if size_element else "Size not found"

#             # Append the details to the torrents list
#             torrents.append({
#                 'name': view_torrent_text,
#                 'download_link': download_a_tag.get_attribute('href') if download_a_tag else None,
#                 'size': size_text
#             })

#             # Print combined info
#             print(
#                 f"View Torrent: {view_torrent_text}, Download: {download_text}, Size: {size_text}")

#         except Exception as e:
#             print(f"Error processing row: {e}")

#     return torrents  # Return the list of torrents


# async def download(page, total_links_counter, download_dir="downloads"):
#     if not os.path.exists(download_dir):
#         os.makedirs(download_dir)  # Create directory if it doesn't exist

#     # Fetch the torrents from process_table
#     torrents = process_table(page, total_links_counter)

#     # Wait for the download and rename the file
#     def handle_download(download, name, size):
#         # Wait for the download to complete
#         download_path = download.path()
#         if download_path:
#             file_extension = os.path.splitext(download.suggested_filename())[
#                 1]  # Get the file extension
#             new_filename = f"{name}_{size}{file_extension}"  # Rename format
#             # Full path to renamed file
#             new_filepath = os.path.join(download_dir, new_filename)
#             os.rename(download_path, new_filepath)  # Rename the file
#             print(f"Downloaded and renamed file: {new_filepath}")

#     # Function to initiate the download process for each link
#     for torrent in torrents:
#         name, size, download_link = torrent['name'], torrent['size'], torrent['download_link']

#         if download_link:  # Check if the download link exists
#             # Set up the event listener for the download
#             with page.expect_download() as download_info:
#                 # Click on the download link
#                 await page.goto(download_link)  # Navigate to the download link

#             download = download_info.value  # Download object

#             # Handle and rename the download
#             handle_download(download, name, size)

#     print("All downloads completed.")


# def check_and_navigate_next_page(page):
#     # Check if there's an <a> tag directly after a <strong> tag in the "linkbox" div
#     next_link = page.query_selector(
#         "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//div[@id='ajax_torrents']//div[@class='linkbox']//strong/following-sibling::a[1]"
#     )

#     if next_link:
#         print("Clicking the next page link after <strong>.")
#         next_link.click()  # Simulate a click on the <a> tag that comes after <strong>

#         # Wait for new content (table rows) to load
#         try:
#             page.wait_for_selector(
#                 "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//div[@id='ajax_torrents']//table[@class='torrent_table']",
#                 timeout=10000  # Adjust timeout as needed
#             )
#             return True  # Successfully loaded the next page
#         except Exception as e:
#             print(
#                 f"Timeout or error occurred while waiting for the next page: {e}")
#             return False  # Stop if there's a timeout or error
#     else:
#         print("No <a> tag found after <strong>. This is the last page.")
#         return False  # No more pages to navigate, the process is complete


# async def main():
#     # Initialize the total link counter
#     total_links_counter = 0

#     async with async_playwright() as p:  # Use async_playwright instead of sync_playwright
#         browser = await p.chromium.launch(headless=True, args=[
#             '--no-sandbox',
#             '--disable-dev-shm-usage',
#             '--disable-gpu',
#             '--window-size=1920,1080',
#             '--disable-extensions',
#             '--disable-infobars',
#             '--disable-browser-side-navigation',
#             '--disable-features=VizDisplayCompositor',
#             '--hide-scrollbars',
#             '--single-process',
#             '--disable-software-rasterizer'
#         ])
#         context = await browser.new_context()
#         page = await context.new_page()

#         # Navigate to the login page
#         await page.goto("https://jpopsuki.eu/login.php")

#         # Get username and password from user input
#         username = input("Enter your username: ")
#         password = input("Enter your password: ")

#         # Log in by filling in the username and password fields
#         await page.fill('input[name="username"]', username)
#         await page.fill('input[name="password"]', password)
#         await page.click('input[class="submit"]')

#         # Wait for the page to load and check login
#         await page.wait_for_selector('div#wrapper')

#         # Navigate to the advanced search page
#         try:
#             await page.goto(
#                 "https://jpopsuki.eu/torrents.php?action=advanced", timeout=60000)
#         except Exception as e:
#             print(f"Error loading the advanced search page: {e}")
#             await browser.close()
#             return

#         # Wait for the search link to appear and click it
#         await page.wait_for_selector(
#             "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//form[@id='torrents_filter']//b/center/a",
#             timeout=60000)
#         await page.click(
#             "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//form[@id='torrents_filter']//b/center/a")

#         # Delay for the page to load
#         await asyncio.sleep(2)

#         # Get search parameters from user input
#         artist_name = input("Enter artist name (leave blank if not needed): ")
#         album_name = input("Enter album name (leave blank if not needed): ")
#         remaster_title = input(
#             "Enter remaster title (leave blank if not needed): ")
#         tags_input = input(
#             "Enter tags separated by commas (leave blank if not needed): ")
#         tags = tags_input.split(',') if tags_input else []

#         # Fill in search parameters if provided
#         if artist_name:
#             await page.fill('input[name="artistname"]', artist_name)
#         if album_name:
#             await page.fill('input[name="torrentname"]', album_name)
#         if remaster_title:
#             await page.fill('input[name="remastertitle"]', remaster_title)
#         if tags:
#             await page.fill('input[name="searchtags"]', ', '.join(tags))

#         # Submit the form
#         await page.click(
#             "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//form[@id='torrents_filter']//div[@id='search_box']//div[@class='filter_torrents']//div[@class='box pad']//div[@class='submit']//input[@type='submit']",
#             timeout=60000)

#         # Process the search results table
#         results_found = process_table(page, total_links_counter)
#         print(results_found)

#         # Keep checking for the next page link and processing until no more results
#         while results_found:
#             if check_and_navigate_next_page(page):
#                 results_found = process_table(page, total_links_counter)
#             else:
#                 break

#         print(f"Total number of valid links found: {total_links_counter}")

#         # Close browser
#         await browser.close()


# if __name__ == "__main__":
#     asyncio.run(main())
# Use async_playwright for async operations
from playwright.async_api import async_playwright
import os
import asyncio


async def process_table(page, total_links_counter):
    # Wait for the table to be visible after loading the page
    try:
        print("Waiting for the torrent table to be visible.")
        await page.wait_for_selector(
            "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//div[@id='ajax_torrents']//table[@class='torrent_table']",
            timeout=15000,  # Increased timeout to 15 seconds
            state='visible'  # Ensure the element is visible
        )
    except Exception as e:
        print(f"Error or timeout while waiting for the table: {e}")
        return []  # Return empty list if there's an error or timeout

    # Fetch all <tr> elements within the table
    tr_elements = await page.query_selector_all(
        "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//div[@id='ajax_torrents']//table[@class='torrent_table']//tr"
    )

    print(f"Total <tr> tags found: {len(tr_elements)}")

    torrents = []  # List to hold torrent details

    # Loop over each row and check for both "View Torrent" and "Download" links
    for tr in tr_elements:
        try:
            # Locate <a> tags inside the row that have "View Torrent" in their title
            view_torrent_a_tag = await tr.query_selector("a[title*='View Torrent']")
            view_torrent_text = await view_torrent_a_tag.inner_text() if view_torrent_a_tag else "No 'View Torrent' link found"

            # Get the 4th <td> in the row and look for a <span> containing an <a> tag with "Download" in the title
            td_4th = await tr.query_selector("td:nth-child(4)")
            download_text = "No 'Download' link found"
            if td_4th:
                download_a_tag = await td_4th.query_selector("span a[title*='Download']")
                if download_a_tag:
                    download_text = await download_a_tag.inner_text()

            # If no download link is found in the 4th <td>, check the first <td>
            if download_text == "No 'Download' link found":
                td_1st = await tr.query_selector("td:nth-child(1)")
                if td_1st:
                    download_a_tag = await td_1st.query_selector("span a[title*='Download']")
                    if download_a_tag:
                        download_text = await download_a_tag.inner_text()

            # Get the size from the <td> with class 'nobr'
            size_element = await tr.query_selector("td.nobr")
            size_text = await size_element.inner_text() if size_element else "Size not found"

            # Append the details to the torrents list
            torrents.append({
                'name': view_torrent_text,
                'download_link': await download_a_tag.get_attribute('href') if download_a_tag else None,
                'size': size_text
            })

            # Print combined info
            print(
                f"View Torrent: {view_torrent_text}, Download: {download_text}, Size: {size_text}")

        except Exception as e:
            print(f"Error processing row: {e}")

    return torrents  # Return the list of torrents


async def download(page, total_links_counter, download_dir="downloads"):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)  # Create directory if it doesn't exist

    # Fetch the torrents from process_table
    torrents = await process_table(page, total_links_counter)

    # Function to handle the download and rename the file
    async def handle_download(download, name, size):
        # Wait for the download to complete
        download_path = await download.path()
        if download_path:
            file_extension = os.path.splitext(download.suggested_filename())[
                1]  # Get the file extension
            new_filename = f"{name}_{size}{file_extension}"  # Rename format
            # Full path to renamed file
            new_filepath = os.path.join(download_dir, new_filename)
            os.rename(download_path, new_filepath)  # Rename the file
            print(f"Downloaded and renamed file: {new_filepath}")

    # Function to initiate the download process for each link
    for torrent in torrents:
        name, size, download_link = torrent['name'], torrent['size'], torrent['download_link']

        if download_link:  # Check if the download link exists
            # Set up the event listener for the download
            download_info = await page.expect_download()  # Await the download expectation
            await page.goto(download_link)  # Navigate to the download link
            download = await download_info.value  # Get the download object

            # Handle and rename the download
            await handle_download(download, name, size)

    print("All downloads completed.")


async def check_and_navigate_next_page(page):
    # Check if there's an <a> tag directly after a <strong> tag in the "linkbox" div
    next_link = await page.query_selector(
        "//body[@id='torrents']//div[@id='wrapper']//div[@id='content']//div[@id='ajax_torrents']//div[@class='linkbox']//strong/following-sibling::a[1]"
    )

    if next_link:
        print("Clicking the next page link after <strong>.")
        await next_link.click()  # Simulate a click on the <a> tag that comes after <strong>

        # Wait for new content (table rows) to load
        try:
            await page.wait_for_selector(
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


async def main():
    # Initialize the total link counter
    total_links_counter = 0

    async with async_playwright() as p:  # Use async_playwright instead of sync_playwright
        browser = await p.chromium.launch(headless=True, args=[
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
        context = await browser.new_context()
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
        await page.wait_for_selector('div#wrapper')

        # Navigate to the advanced search page
        try:
            await page.goto("https://jpopsuki.eu/torrents.php?action=advanced", timeout=60000)
        except Exception as e:
            print(f"Error loading the advanced search page: {e}")
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

        # Loop to process the torrent pages
        while True:
            await download(page, total_links_counter)

            # Check and navigate to the next page
            if not await check_and_navigate_next_page(page):
                break  # Exit the loop if there are no more pages

        await browser.close()  # Ensure the browser closes after processing


# Run the async main function
asyncio.run(main())
