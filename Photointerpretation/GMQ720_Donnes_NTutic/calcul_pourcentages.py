import pandas as pd
import numpy as np

annee = '1966'

db = pd.read_csv('troncons_' + annee + '.csv')

classes = { 
    'Arbres': 10,
    'Arbustaie': 8.2,
    'Herbacée': 5.8,
    'Coupe': 4.3,
    'Friche': 3,
    'Culture': 1.9,
    'Sol nu': 1.7,
    'Socle': 3.8,
    'Infrastructure': 1.9,
    'Eau': 0
}

total_area = db.agg({'AREA': ['sum']})['AREA'][0]

# 'NA', 'Arbres', 'Arbustaie', 'Herbacée', 'Coupe', 'Friche', 'Culture', 'Sol nu', 'Socle', 'Infrastructure', 'Eau'
db_out = pd.DataFrame([], columns=['class', 'area', 'proportion'])

for classe in classes.keys():
    db_out = db_out.append({'class': classe, 'area': 0, 'proportion': ''}, ignore_index=True)

for i, row in db.iterrows():
    if isinstance(row['Type'], float):
        classe = 'NA'
    else: 
        classe = row['Type'] 
    index = db_out[db_out['class'] == classe].index[0]
    db_out.at[index, 'area'] += row['AREA']


for i, row in db_out.iterrows():
    db_out.at[i, 'proportion'] = round(row['area'] * 100 / total_area, 1)


db_out.to_csv('proportions_' + annee + '.csv', index=False)

