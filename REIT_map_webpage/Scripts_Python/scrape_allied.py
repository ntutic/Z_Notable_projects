import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://www.alliedreit.com/city/'
pages = ['toronto', 'montreal', 'calgary', 'vancouver', 'ottawa', 'edmonton', 'kitchener']

db = pd.DataFrame([], columns=['address', 'ville', 'sector', 'href', 'reit'])

for page in pages:
    html = requests.get(url + page)
    soup = BeautifulSoup(html.content, features='html.parser')


    # Trouver les éléments parents
    listings = soup.find_all('div', {'class': 'property-listing__header'})
    for listing in listings:
        address = listing.find('div', {'class': 'property__name'}).find('h3').find('a').text.strip()
        href = listing.find('div', {'class': 'property__name'}).find('h3').find('a')['href']
        ville = listing.find('div', {'class': 'property__name'}).find('p').text.strip()

        if listing.find('div', {'class': 'property__office-gla'}).find('p').find('span').text.strip() != '0 sq ft' and listing.find('div', {'class': 'property__retail-gla'}).find('p').find('span').text.strip() != '0 sq ft':
            sector = 'Retail, Office'
        elif listing.find('div', {'class': 'property__office-gla'}).find('p').find('span').text.strip() != '0 sq ft':
            sector = 'Office'
        elif listing.find('div', {'class': 'property__retail-gla'}).find('p').find('span').text.strip() != '0 sq ft':
            sector = 'Retail'
        else:
            sector = 'wtf'

        db = db.append({'address': address, 'ville': ville, 'sector': sector, 'href': href, 'reit': 'Allied REIT'}, ignore_index=True)


db.to_csv('data/allied.csv')