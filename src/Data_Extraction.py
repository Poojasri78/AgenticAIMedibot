import requests
from bs4 import BeautifulSoup
import pdfkit
import os
import urllib.parse

url = "https://www.who.int/news-room/fact-sheets"

# Extract links using BeautifulSoup
try:
    # Set a user-agent to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)  # Fetch the HTML content.
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
except requests.exceptions.RequestException as e:
    print(f"Error fetching URL {url}: {e}")  # Handle request errors
    exit()

soup = BeautifulSoup(response.text, 'html.parser')  # Parse the HTML content.
links = []

# Find all 'a' (anchor) tags which typically contain links.
for link_tag in soup.find_all('a', href=True):  # Filter for tags with 'href' attribute.
    href = link_tag.get('href')  # Get the 'href' attribute value.
    
    # Filter for links that seem relevant to fact sheets
    if "fact-sheets/detail" in href and not href.startswith('#'):
        # Construct absolute URL if it's a relative path.
        if not href.startswith('http'):
            href = urllib.parse.urljoin(url, href)  # Resolve relative URLs.
        links.append(href)

# Remove duplicate links if any
links = list(set(links))
print(f"Found {len(links)} unique fact sheet links.")

# 3. Convert each link to a PDF
output_folder = "fact_sheets_pdfs"  # Create a directory for PDFs.
os.makedirs(output_folder, exist_ok=True)  # Create the folder if it doesn't exist.

# --- Configuration for pdfkit ---
# pdfkit is a wrapper for the wkhtmltopdf command-line tool.
# If it's installed elsewhere, you must point pdfkit to it.

path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

# When calling pdfkit
# pdfkit.from_url(link, filename, configuration=config)

# wkhtmltopdf is in the system PATH.

for link in links:
    try:
        # Get the path part of the URL (e.g., /news-room/fact-sheets/detail/anaemia)
        url_path = urllib.parse.urlparse(link).path
        
        # Extract the last part of the path as the filename slug 
        file_slug = os.path.basename(os.path.normpath(url_path)) # handles trailing slashes correctly
        
        # If the slug is empty for any reason, use a fallback name
        if not file_slug or file_slug == 'detail':
             # Create a fallback name from the full path to ensure uniqueness
            file_slug = url_path.strip('/').replace('/', '_')

        # Sanitize the filename to remove invalid characters if any
        safe_filename = "".join([c for c in file_slug if c.isalpha() or c.isdigit() or c in ('_','-')]).rstrip()
        
        # Create the final PDF filename
        pdf_filename = f"{safe_filename}.pdf"
        output_path = os.path.join(output_folder, pdf_filename)
        
        print(f"Converting {link} to {output_path}...")

        # Convert the URL to a PDF. Add 'configuration=config' if you defined it above.
        pdfkit.from_url(link, output_path, configuration=config)
        print(f"Successfully created {output_path}")

    except Exception as e:
        print(f"Could not convert {link}. Error: {e}")

print("\nPDF conversion process completed.")
