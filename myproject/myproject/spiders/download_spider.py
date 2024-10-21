import scrapy
import os

class DownloadSpider(scrapy.Spider):
    name = 'download_spider'

    def start_requests(self):
        # Define the base URL
        base_url = 'https://jpopsuki.eu/'  # Replace with the actual base URL

        # Get the absolute path to the download_links.txt file
        file_path = os.path.join(os.path.dirname(__file__), '../../../download_links.txt')
        
        # Read the download links from the file
        with open(file_path, 'r') as f:
            links = f.readlines()

        previous_name = None
        for line in links:
            link, name, size = line.strip().split('|')
            full_url = base_url + link

            # Use the previous name if the current name is empty
            if not name:
                name = previous_name
            else:
                previous_name = name

            yield scrapy.Request(url=full_url, callback=self.download_file, cb_kwargs={'name': name, 'size': size})

    def download_file(self, response, name, size):
        # Generate a unique file name using the name and size
        file_name = f"{name}_{size}.torrent"

        # Ensure the downloads directory exists
        os.makedirs('downloads', exist_ok=True)

        # Save the file to the 'downloads' directory
        file_path = os.path.join('downloads', file_name)
        self.logger.info(f"Saving file {file_path}")
        with open(file_path, 'wb') as f:
            f.write(response.body)
