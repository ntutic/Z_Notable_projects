import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://www.btbreit.com/real-estate-portfolio/page/'
page_nb = 1

db = pd.DataFrame([], columns=['address', 'ville', 'sector', 'href', 'reit'])

while True:
    html = requests.get(url + str(page_nb))
    soup = BeautifulSoup(html.content, features='html.parser')

    # Élément indiquant qu'on a atteint la fin (page invalide)
    if soup.find('div', {'class': 'wpsight-listings-sc'}).text.strip() == 'Sorry, but no listing matches your search criteria.':
        db.to_csv('data/btb.csv')
        break

    # Trouver les éléments parents
    listings = soup.find_all('div', {'class': 'listing_column_inner'})
    for listing in listings:
        address = listing.find('h3', {'class': 'entry-title'}).find('a').text.strip()
        href = listing.find('h3', {'class': 'entry-title'}).find('a')['href']
        ville = listing.find('h5', {'class': 'listing_location'}).text.strip()
        sector = listing.find('h5', {'class': 'listing_type'}).text.strip()
        db = db.append({'address': address, 'ville': ville, 'sector': sector, 'href': href, 'reit': 'BTB REIT'}, ignore_index=True)

    page_nb += 1
