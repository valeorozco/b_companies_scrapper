import requests
from bs4 import BeautifulSoup
import openpyxl
import csv
import time

# Initialize the Excel document and add headers
def create_csv():
    with open("company_data.csv", mode="w", newline='', encoding='utf-16') as file:
        writer = csv.writer(file)
        # Writing the header row
        writer.writerow(["Company Name", "Email", "Code Naf"])

# Append data to Excel file
def save_to_csv(data):
    with open("company_data.csv", mode="a", newline='', encoding='utf-16') as file:
        writer = csv.writer(file)
        # Append the data (company information)
        writer.writerow(data)

# Scrape company information from the page
def scrape_company_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    try:
        company_name = soup.find("div", class_="field__label").text.strip()  
        company_name = clean_text(f"{company_name}") 
        print(company_name)
    except:
        company_name = "N/A"

    try:
        email = soup.find("div", class_="field field--name-field-email field--type-email field--label-hidden field__item").text.strip()
        email = clean_text(f"{email}") 
        print(email)
    except:
        email = "N/A"

    try:
        code_naf = soup.find("div", class_="field field--name-field-code-naf field--type-entity-reference field--label-inline").text.strip()
        code_naf = clean_text(f"{code_naf}")
        print(code_naf)
    except:
        code_naf = "N/A"

    return [company_name, email,code_naf]

def clean_text(text):
    return text.replace("\t", "").replace("\n", "")


def process_links(url):
    base_url = "https://www.les-scic.coop"  # The base URL to prepend
    while True:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the container with class="view-results"
        container = soup.find(class_="view-results")

        if container is None:
            print("No container found")
            return []

        hrefs = []
        # Find all 'a' tags with the class "link more-link" within this container
        links = container.find_all('a', class_="link more-link")

        for link in links:
            href = link.get('href')  # Get the href attribute
            
            # Check if href is valid, clean it, and ensure no duplicates
            if href and href not in hrefs:
                # Clean the href by stripping unnecessary whitespace
                clean_href = href.strip()
                # Add the base URL before the cleaned href
                full_url = base_url + clean_href
                # Append the fully constructed URL to the list
                hrefs.append(full_url)
        print(f"links found: {len(hrefs)}")
        return hrefs

def scrape_company(hrefs):
    for href in hrefs:
        company_data = scrape_company_info(href)
        save_to_csv(company_data)   
    return company_data


def scrape_site():
    create_csv()    
    page = 0 
    while True:
        base_url =f"https://www.les-scic.coop/l-annuaire?page={page}"
        print(base_url)
        try:
            sites = process_links(base_url)
            data = scrape_company(sites)
            page += 1
            False
        except:
            print("error when finding links") 
            page += 1
        if page == 25:
            break
    
        
# Start the scraping process
scrape_site()


