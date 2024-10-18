import scrapy
import os
import hashlib

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
        for link in links:
            full_url = base_url + link.strip()
            yield scrapy.Request(url=full_url, callback=self.download_file)

    def download_file(self, response):
        # Generate a unique file name using a hash
        file_hash = hashlib.md5(response.url.encode()).hexdigest()
        file_name = f"{file_hash}.torrent"

        # Ensure the downloads directory exists
        os.makedirs('downloads', exist_ok=True)

        # Save the file to the 'downloads' directory
        file_path = os.path.join('downloads', file_name)
        self.logger.info(f"Saving file {file_path}")
        with open(file_path, 'wb') as f:
            f.write(response.body)
