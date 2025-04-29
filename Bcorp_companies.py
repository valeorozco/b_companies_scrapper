import requests
from bs4 import BeautifulSoup
import openpyxl
import csv
import time
import re

# Initialize the Excel document and add headers
def create_csv():
    with open("b_companies_1.csv", mode="w", newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Writing the header row
        writer.writerow(['name','certification_date','industry','operates_in','website','total_score','governance',
'g_mission','g_ethics','workers','w_financial','w_health','w_career','w_engagement','community','c_diveristy','c_economic','c_civic','c_supply','environment','e_management','e_air','e_water','e_land','customers','c_stewardship', 'previous_certificates'])

# Append data to Excel file
def save_to_csv(data):
    try:
        with open("b_companies_1.csv", mode="a", newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(data)
            print("writer csv used")
    except Exception as e:
        print(f"An error occurred: {e}")

# Scrape company information from the page
def scrape_company_info(url):
    response = requests.get(url)

    if response.status_code == 404:
        return 
    soup = BeautifulSoup(response.content, "html.parser")
    try:
        company_div = soup.find("div", class_="flex w-full justify-center my-8")
        # Check if the div was found
        if company_div is not None:
            company_name = company_div.find("h1")  # Find the <h1> inside the div
            company_name = clean_text(company_name.text)  # Clean and extract text
    except Exception as e:
       print(f"An error occurred: {e}")
    
    try:
        total_score = soup.find("text", class_="text-4xl").text.strip() 
        total_score = clean_text(f"{total_score}") if total_score else "N/A"
    except Exception as e:
       print(f"An error occurred: {e}")

    try:
    # Locate the <span> with class "font-serif" inside the <p> tag
        certification_date_div = soup.find("span", string="Certified Since").find_next("div", class_="opacity-60")
        certification_date = certification_date_div.get_text(strip=True) if certification_date_div else "N/A"
    except Exception as e:
        print(f"An error occurred: {e}")
    
    try:
        # Extract "Industry"
        website_div = soup.find("span", string="Website").find_next("div", class_="opacity-60")
        website = website_div.get_text(strip=True) if website_div else "N/A"
 
        # Extract "Industry"
        industry_div = soup.find("span", string="Industry").find_next("div", class_="opacity-60")
        industry = industry_div.get_text(strip=True) if industry_div else "N/A"
     
        # Extract "Operates In"
        operates_in_div = soup.find("span", string="Operates In").find_next("div", class_="opacity-60")
        operates_in = operates_in_div.get_text(strip=True) if operates_in_div else "N/A"
      
        categories_scores = find_scores(url)
        governance, workers, community, environment, customers = get_category_scores(categories_scores)  
        sub_categories_scores = {}
        sub_categories = ["Mission & Engagement","Ethics & Transparency","Financial Security","Health, Wellness, & Safety","Career Development","Engagement & Satisfaction","Diversity, Equity, & Inclusion","Economic Impact","Civic Engagement & Giving","Supply Chain Management","Environmental Management","Air & Climate","Water","Land & Life","Customer Stewardship"]
       
        for category in sub_categories:
             score = find_sub_groups(soup, category)
             # Assign the score to the category in the dictionary
             sub_categories_scores[category] = score
        [mission_engagement,ethics_transparency,financial_security,health_wellness_safety,career_development,engagement_satisfaction,
        diversity_equity_inclusion,economic_impact,civic_engagement_giving,supply_chain_management,environmental_management,
        air_climate,water,land_life,customer_stewardship] = get_subgroup_scores(sub_categories_scores)
    except Exception as e:
       print(f"An error occurred: {e}")

    previous_certificates = previous_certifications(response)
      
    return [company_name,certification_date,industry, operates_in, website,total_score,governance,mission_engagement,ethics_transparency,workers,financial_security,health_wellness_safety,career_development,engagement_satisfaction,
community,diversity_equity_inclusion,economic_impact,civic_engagement_giving,supply_chain_management,environment, environmental_management,
        air_climate,water,land_life, customers,customer_stewardship, previous_certificates]

def previous_certifications(response):
    soup = BeautifulSoup(response.content, "html.parser")
    try:
    # Find the main container
        certifications_div = soup.find("div", class_="flex flex-col space-y-4")
        # Initialize the list for previous certifications
        previous_certifications = []
        
        # Check if the container is found
        if certifications_div:
            # Extract all the nested <div> elements within the main container
            for div in certifications_div.find_all("div", class_="flex w-full space-x-12"):
                # Extract the text from the <span> elements
                year_score_text = div.find_all("span")
                year = year_score_text[0].text.strip() if len(year_score_text) > 0 else "N/A"
                score = year_score_text[1].text.strip() if len(year_score_text) > 1 else "N/A"
                # Append a tuple of (year, score) to the list
                previous_certifications.append((year, score))
                print(f"{previous_certifications}")
        else:
            # If no container found, add "N/A"
            previous_certifications.append(("N/A", "N/A"))
            print("Previous Certifications:")
            print(f"{year}: {score}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return previous_certifications

def find_scores(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    # Find all div elements with class "px-2 pt-6"
    divs = soup.find_all("div", class_="px-2 pt-6")

    # Initialize a dictionary to store the results
    results = {}
    # Loop through each div and extract the category and its score
    for count, div in enumerate(divs):
        try:
            # Extract the <h3> content
            h3_content = div.find("h3").get_text(strip=True)
            # Use regex to separate the category name and the numeric value
            category_match = re.match(r"([A-Za-z\s]+)(\d+(\.\d+)?)", h3_content)
            if category_match:
                category = category_match.group(1).strip()  # Extract the category name
                score = category_match.group(2)  # Extract the numeric value
                # Save the result in the dictionary
                results[category] = score 
            if count >4:
                break
        except Exception as e:
            print(f"An error occurred: {e}")
    
    return results

def get_category_scores(results):
    # Use dictionary unpacking to get individual variables
    governance = results.get('Governance', 'N/A')
    workers = results.get('Workers', 'N/A')
    community = results.get('Community', 'N/A')
    environment = results.get('Environment', 'N/A')
    customers = results.get('Customers', 'N/A')

    # Return them as a tuple
    return governance, workers, community, environment, customers
def find_sub_groups(soup,category_name):
    
        # Locate the span containing the category name
        category_span = soup.find("span", string=category_name)
        # Ensure the category span is found
        if category_span:
            # Find the parent div and then locate the next sibling div that has the score
            category_div = category_span.find_parent("div", class_="flex px-4")
            score_span = category_div.find("span", class_="font-bold") if category_div else None
            # Extract the score, or return "N/A"
            return score_span.get_text(strip=True) if score_span else "N/A"
        else:
            return "N/A"
def get_subgroup_scores(results_sub):

# Extracting values from results_sub based on the categories you mentioned
    mission_engagement = results_sub.get("Mission & Engagement", "N/A")
    ethics_transparency = results_sub.get("Ethics & Transparency", "N/A")
    financial_security = results_sub.get("Financial Security", "N/A")
    health_wellness_safety = results_sub.get("Health, Wellness, & Safety", "N/A")
    career_development = results_sub.get("Career Development", "N/A")
    engagement_satisfaction = results_sub.get("Engagement & Satisfaction", "N/A")
    diversity_equity_inclusion = results_sub.get("Diversity, Equity, & Inclusion", "N/A")
    economic_impact = results_sub.get("Economic Impact", "N/A")
    civic_engagement_giving = results_sub.get("Civic Engagement & Giving", "N/A")
    supply_chain_management = results_sub.get("Supply Chain Management", "N/A")
    environmental_management = results_sub.get("Environmental Management", "N/A")
    air_climate = results_sub.get("Air & Climate", "N/A")
    water = results_sub.get("Water", "N/A")
    land_life = results_sub.get("Land & Life", "N/A")
    customer_stewardship = results_sub.get("Customer Stewardship", "N/A")

    # Return them as a tuple
    return [mission_engagement,ethics_transparency,financial_security,health_wellness_safety,career_development,engagement_satisfaction,
            diversity_equity_inclusion,economic_impact,civic_engagement_giving,supply_chain_management,environmental_management,
            air_climate,water,land_life,customer_stewardship]

def clean_text(text):
    return text.replace("\t", "").replace("\n", "")


def process_links(url):
    
    while True:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the container 
        container = soup.find(class_="card-list")

        if container is None:
            print("No container found in process_links")
            return []

        hrefs = []
        # Find all 'a' tags with the class within this container
        links = container.find_all('a', class_="card-bcorp-member__link")
        for link in links:
            href = link.get('href')  # Get the href attribute
            if href == "https://www.bcorporation.net/en-us/find-a-b-corp/":
                continue
            # Check if href is valid, clean it, and ensure no duplicates
            if href and 'https://www.bcorporation.net' in href and href not in hrefs:
                 # Clean the href by stripping unnecessary whitespace
                clean_href = href.strip()
                hrefs.append(clean_href)
        print(f"links found: {len(hrefs)}")
        return hrefs

def scrape_company(hrefs):
    try:
        for val,href in enumerate(hrefs):
            company_data = scrape_company_info(href)
            save_to_csv(company_data)   
            print("saved in csv")
    except:
            val =+1
    return company_data


def scrape_site():
    create_csv()    
    page = 0 
    while True:
        base_url = f"https://bcorporation.fr/la-communaute-b-corp/decouvrir-la-communaute-francaise-des-entreprises-b-corp/?_paged={page}&_sort=title_asc"
        try:
            sites = process_links(base_url)
            data = scrape_company(sites)
            page += 1
            False
        except:
            print("error when finding links") 
            page += 1
        if page == 43:
            break
    
        
# Start the scraping process
scrape_site()


