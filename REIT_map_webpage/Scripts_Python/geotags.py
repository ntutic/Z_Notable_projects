from geopy.geocoders import GoogleV3, Nominatim
from geopy.exc import GeocoderUnavailable
import pandas as pd

db = pd.read_excel('data/reits2.xls')


# Geocodage Google
if False:
    with open('config.txt', 'r') as f:
        geoloc_ggl = GoogleV3(api_key=f.readline(), domain='maps.google.ca') 
    db['lat_ggl'] = 'NA'
    db['lng_ggl'] = 'NA'
    db['address_ggl'] = 'NA'


# Geocodage OpenStreetMap
if True:
    geoloc_osm = Nominatim(user_agent="geopy")
    db['lat_osm'] = 'NA'
    db['lng_osm'] = 'NA'
    db['address_osm'] = 'NA'

    for i, row in db.iterrows():
        address = row['address'] + ', Canada'

        geo_osm = geoloc_osm.geocode(address)
        if geo_osm:
            db.at[i, 'lat_osm'] = geo_osm.latitude
            db.at[i, 'lng_osm'] = geo_osm.longitude
            db.at[i, 'address_osm'] = geo_osm.address
            print('OpenStreetMap: ' + geo_osm.address)


    db.to_csv('data/reits_geo.csv', enconding='UTF8')
    db.to_excel('data/reits_geo2.xls')