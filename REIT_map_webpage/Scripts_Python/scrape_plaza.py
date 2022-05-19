import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

url = 'https://plaza.ca/plaza-properties/?format=retail-property'
page_nb = 1

db = pd.DataFrame([], columns=['address', 'ville', 'sector', 'href', 'name', 'reit'])

html = requests.get(url)
soup = BeautifulSoup(html.content, features='html.parser')

# Trouver les éléments parents
listings = soup.find_all('tr', {'data-abc': True})
for listing in listings:
    name = listing.find('td', {'data-title': 'Property:'}).text.strip()
    href = listing.find('a', {'href': True})['href']
    ville = listing.find('td', {'data-title': 'City:'}).text.strip()
    sector = listing.find('td', {'data-title': 'Format:'}).text.strip()

    property_html = requests.get(href)

    # On valide que chaque page est bien chargé comme on devra en parcourir pas mal
    if property_html.status_code == 200:
        property_soup = BeautifulSoup(property_html.content, features='html.parser')
        
        elements = property_soup.find_all('a', {'target': '_blank'})
        for element in elements:
            if element.find('i', {'class': 'fa-map-marker'}): # Évité l'ambiguité avec un autre "target _blank"
                address = element.text.strip()
                break

    else:
        a = input('oups') # Stoppage lors de l'execution pour débugger

    time.sleep(3) # Pour éviter de surcharger leur serveur

    db = db.append({'address': address, 'ville': ville, 'sector': sector, 'href': href, 'name': name, 'reit': 'Plaza REIT'}, ignore_index=True)



db.to_csv('data/plaza.csv')
