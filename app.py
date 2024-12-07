from flask import Flask, render_template, request, redirect, url_for
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


# Function to scrape data from the main page
def scrape_opportunity_track():
    url = "https://opportunitytrack.in/internships/"
    response = requests.get(url)

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    job_postings = soup.find_all('article', class_='eael-grid-post eael-post-grid-column')

    job_list = []
    for posting in job_postings:
        title = posting.find('h2', class_='eael-entry-title').text.strip()
        link = posting.find('a', class_='eael-grid-post-link')['href']
        meta_info = posting.find('div', class_='eael-entry-meta').text.strip()

        # Categorization
        category = "Internship"
        if "remote" in meta_info.lower():
            category = "Remote Internship"
        elif "onsite" in meta_info.lower():
            category = "Onsite Internship"

        job_data = {
            'title': title,
            'link': link,
            'meta_info': meta_info,
            'category': category
        }
        job_list.append(job_data)
    return job_list


# Function to scrape the details of a specific job page
def scrape_job_details(link):
    try:
        response = requests.get(link)
        if response.status_code != 200:
            return {"error": f"Failed to fetch page: {response.status_code}"}

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract job details
        title = soup.find('h1', class_='entry-title').text.strip() if soup.find('h1', class_='entry-title') else "Not available"
        published_date = soup.find('span', class_='published').text.strip() if soup.find('span', class_='published') else "Not available"
        description = soup.find('div', class_='entry-content clear').find('p').text.strip() if soup.find('div', class_='entry-content clear') else "Not available"

        # Extract responsibilities
        responsibilities = []
        if soup.find('ol', class_='wp-block-list'):
            responsibilities_items = soup.find('ol', class_='wp-block-list').find_all('li')
            responsibilities = [item.text.strip() for item in responsibilities_items]

        # Extract requirements
        requirements = []
        requirements_section = soup.find('strong', text='Requirements')
        if requirements_section and requirements_section.find_next('ol'):
            requirements_items = requirements_section.find_next('ol').find_all('li')
            requirements = [item.text.strip() for item in requirements_items]

        # Extract perks
        perks = "Not available"
        perks_section = soup.find('strong', text='Perks')
        if perks_section and perks_section.find_next('p'):
            perks = perks_section.find_next('p').text.strip()

        # Extract location
        location = "Not available"
        location_section = soup.find('strong', text='Locations')
        if location_section and location_section.find_next('p'):
            location = location_section.find_next('p').text.strip()

        apply_link = "Not available"
        apply_section = soup.find('a', href=True, string="click here")
        if apply_section:
            apply_link = apply_section['href']

            # Extract image URL
            image_url = "Not available"
            image_section = soup.find('div', class_='post-thumb-img-content post-thumb')
            if image_section and image_section.find('img'):
                image_url = image_section.find('img')['src']
                print(image_url)


        # Prepare a dictionary to return
        job_details = {
            "image_url": image_url  ,
            "title": title,
            "published_date": published_date,
            "description": description,
            "responsibilities": responsibilities if responsibilities else "Not available",
            "requirements": requirements if requirements else "Not available",
            "perks": perks,
            "location": location,
            "link": apply_link,
        }
        print(job_details)

        return job_details
    except Exception as e:
        return {"error": str(e)}


@app.route('/')
def home():
    jobs = scrape_opportunity_track()  # Assuming this function exists
    return render_template('index.html', jobs=jobs)


# About route
@app.route('/about')
def about():
    return render_template('about.html')  # Render the About page


# Details route
@app.route('/details')
def details():
    link = request.args.get('link')
    if not link:
        return "No link provided!", 400

    job_details = scrape_job_details(link)  # Assuming this function exists
    if "error" in job_details:
        return render_template('error.html', error=job_details["error"])

    return render_template('details.html', details=job_details)


if __name__ == '__main__':
    app.run(debug=True)
