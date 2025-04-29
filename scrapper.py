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
        writer.writerow(["Company Name", "Creation Year", "Société à mission Year", "Activité", "Raison d'Être", "Objectifs"])

# Append data to Excel file
def save_to_csv(data):
    with open("company_data.csv", mode="a", newline='', encoding='utf-16') as file:
        writer = csv.writer(file)
        # Append the data (company information)
        writer.writerow(data)
    print("csv_saved")

# Scrape company information from the page
def scrape_company_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    try:
        stripped_ur = url.rstrip('/')
        company_name = clean_text(stripped_ur.split('/')[-1])
    except:
        return None  # Return None if the segment is not found
    try:
        text = soup.find("div", {"data-id": "a6b6d0e"}).find("div", class_="jet-listing-dynamic-field__content").text.strip()
        parts = text.split()  # Split by spaces
        creation_year = parts[-1]    
        creation_year = clean_text(f"{creation_year}") 
    except:
        creation_year = "N/A"

    try:
        text = soup.find("div", {"data-id": "e19b280"}).find("div", class_="jet-listing-dynamic-field__content").text.strip()
        parts = text.split()  # Split by spaces
        societe_mission_year = parts[-1]
        societe_mission_year = clean_text(f"{societe_mission_year}") 
    except:
        societe_mission_year = "N/A"

    try:
        activite = soup.find("div", {"data-id": "6b21817"}).find("div", class_="jet-listing-dynamic-field__content").text.strip()
        activite = clean_text(f"{activite}")
    except:
        activite = "N/A"

    try:
        raison_etre = soup.find("div", {"data-id": "9da37c5"}).find("div", class_="jet-listing-dynamic-field__content").text.strip()
        raison_etre = clean_text(f"{raison_etre}")
    except:
        raison_etre = "N/A"

    try:
        objectifs = soup.find("div", {"data-id": "548b109"}).find("div", class_="jet-listing-dynamic-field__content").text.strip()
        objectifs = clean_text(f"{objectifs}")
    except:
        objectifs = "N/A"
    return [company_name, creation_year, societe_mission_year, activite, raison_etre, objectifs]

def clean_text(text):
    return text.replace("\t", "").replace("\n", "")

# Process a single letter's company list
def process_links(url):#letter
    while True:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        #Find the container with class="jet-listing-grid__items"
        container = soup.find(class_="jet-listing-grid__items")
        hrefs = []
        # Find all 'a' tags within this container
        links = container.find_all('a')
        #Extract the href attribute from each 'a' tag
        for link in links:
            href = link.get('href')  # Get the href attribute       
            # Append the href to the list
            if href not in hrefs:  # Check if href is already in the list
                hrefs.append(href)
        print(f"links found,{len(hrefs)}")
        return hrefs

def scrape_company(hrefs):
    for href in hrefs:
        company_data = scrape_company_info(href)
        save_to_csv(company_data)   
    return company_data


def scrape_site():
    create_csv()
    
    page = 0 
    alphabet = [chr(i) for i in range(ord('A'), ord('Z')+1)]
    for letter in alphabet:
       while True:
            base_url =f"https://www.observatoiredessocietesamission.com/societes-a-mission-referencees/?jsf=jet-engine&alphabet={letter}&pagenum={page}"
            print(base_url)
            try:
                sites = process_links(base_url)
                data = scrape_company(sites)
                page += 1
                False
            except:
                print("error when finding links")
                page = 0 
                break
    
        
# Start the scraping process
scrape_site()



