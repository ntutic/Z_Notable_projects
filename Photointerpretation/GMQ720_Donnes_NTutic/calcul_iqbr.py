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



troncons = db.groupby('troncon_fid').agg({'AREA': ['sum']})

db['proportion'] = ''
db['ponderation'] = ''

for i, row in db.iterrows():
    if not classes[row['Type']]:
        troncons.at[row['troncon_fid']] = troncons.loc[row['troncon_fid']][0] - row['AREA']

for i, row in db.iterrows():
    db.at[i, 'proportion'] = row['AREA']* 100 / troncons.loc[row['troncon_fid']][0]
    db.at[i, 'ponderation'] = row['AREA']* 100 / troncons.loc[row['troncon_fid']][0] * classes[row['Type']]

resultats = db.groupby('troncon_fid').agg({'ponderation': ['sum']}) / 10
resultats['troncon_fid'] = resultats.index
resultats.to_csv('results_' + annee + '.csv', index=False)

