# JPopsuki Torrent Scraper and Downloader

A Python-based automation tool for searching and downloading torrents from JPopsuki.eu, a private Japanese music tracker. This project consists of two main components: a web scraper using Playwright and a torrent downloader using Scrapy.

## Features

- **Automated Login**: Securely log into JPopsuki using your credentials
- **Advanced Search**: Search torrents with customizable parameters:
  - Search strings
  - Tags
  - Categories (1-10)
  - Sort order (ascending/descending)
- **Multi-page Scraping**: Automatically navigate through multiple pages of search results
- **Data Extraction**: Extract torrent download links, names, and file sizes
- **Batch Download**: Download multiple .torrent files automatically
- **Organized Storage**: Save downloaded files with descriptive names in a dedicated directory

## Project Structure

```
script-jpop/
├── sel.py                          # Main scraper script using Playwright
├── requirements.txt                # Python dependencies
├── myproject/                      # Scrapy project for downloading torrents
│   ├── scrapy.cfg                  # Scrapy configuration
│   └── myproject/
│       ├── __init__.py
│       ├── items.py                # Scrapy items (unused)
│       ├── middlewares.py          # Scrapy middlewares (unused)
│       ├── pipelines.py            # Scrapy pipelines (unused)
│       ├── settings.py             # Scrapy settings
│       └── spiders/
│           ├── __init__.py
│           └── download_spider.py  # Spider for downloading torrent files
├── downloads/                      # Directory for downloaded .torrent files (created automatically)
└── download_links.txt              # Generated file containing torrent information
```

## Prerequisites

- Python 3.7+
- Valid JPopsuki.eu account
- Chrome/Chromium browser (for Playwright)

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install additional dependencies:**
   ```bash
   # Install Playwright
   pip install playwright scrapy
   
   # Install Playwright browsers
   playwright install chromium
   ```

## Usage

### Step 1: Scrape Torrent Information

Run the main scraper script:

```bash
python sel.py
```

The script will prompt you for:
- **Username**: Your JPopsuki username
- **Password**: Your JPopsuki password
- **Search string**: Keywords to search for (optional)
- **Tags**: Comma-separated tags (optional)
- **Categories**: Category numbers 1-10, comma-separated (e.g., "1,3,5")
- **Sort order**: "asc" for ascending or "desc" for descending

The script will:
1. Log into JPopsuki
2. Navigate to the advanced search page
3. Apply your search criteria
4. Scrape all matching torrents across multiple pages
5. Save results to `download_links.txt`

### Step 2: Download Torrent Files

Navigate to the Scrapy project directory and run the download spider:

```bash
cd myproject
scrapy crawl download_spider
```

This will:
1. Read the torrent links from `download_links.txt`
2. Download each .torrent file
3. Save files to the `downloads/` directory with descriptive names

## Output Files

- **`download_links.txt`**: Contains torrent information in pipe-delimited format:
  ```
  download_link|torrent_name|file_size
  ```
- **`downloads/`**: Directory containing downloaded .torrent files named as:
  ```
  {torrent_name}_{file_size}.torrent
  ```

## Configuration

### Scrapy Settings

You can modify the Scrapy settings in `myproject/myproject/settings.py`:
- Adjust download delays
- Configure concurrent requests
- Enable/disable robots.txt compliance
- Set custom user agents

### Browser Settings

The Playwright browser can be configured in `sel.py`:
- Change `headless=False` to `headless=True` for headless operation
- Modify browser arguments for different behavior
- Adjust timeouts and wait conditions

## Important Notes

⚠️ **Legal and Ethical Considerations:**
- This tool is for educational purposes only
- Ensure you have permission to access JPopsuki.eu
- Respect the site's terms of service and rate limits
- Only download content you have the legal right to access

⚠️ **Security:**
- Your credentials are entered interactively and not stored
- Consider using environment variables for credentials in production
- Be cautious when sharing or committing code with credentials

## Troubleshooting

### Common Issues

1. **Login Failed**: 
   - Verify your credentials
   - Check if JPopsuki is accessible
   - Ensure your account is in good standing

2. **Timeout Errors**:
   - Increase timeout values in the script
   - Check your internet connection
   - Verify JPopsuki site availability

3. **No Torrents Found**:
   - Adjust your search criteria
   - Check if the categories exist
   - Verify the search terms are correct

4. **Download Failures**:
   - Ensure the `downloads/` directory is writable
   - Check if the torrent links are still valid
   - Verify Scrapy is properly configured

## Dependencies

- `playwright`: Web automation and scraping
- `scrapy`: Web crawling and downloading framework
- `asyncio`: Asynchronous programming support

## License

This project is for educational purposes only. Please respect JPopsuki.eu's terms of service and applicable laws regarding torrent downloading in your jurisdiction.

## Contributing

This is a personal automation tool. If you have suggestions or improvements, feel free to fork the repository and make your own modifications.
