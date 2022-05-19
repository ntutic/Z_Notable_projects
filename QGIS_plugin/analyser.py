from qgis.core import Qgis, QgsMessageLog, QgsProject, QgsFeature, QgsGeometry, QgsDistanceArea, QgsVectorLayer, QgsField, QgsPointXY, QgsWkbTypes
from qgis.PyQt.QtCore import QVariant

# il s'agit d'un début de classe, on peut revoir l'ensemble des méthodes et surtout on doit en ajouter.
class Analyser:
 
    # il s'agit du contructeur, on peut passer des paramètres, si on le souhaite
    def __init__(self):
        '''
        Cette classe contient les méthodes de traitement des données. Celles-ci
        sont utilisées depuis la méthode "execute" de GMQ710Analyser (sauf
        getLayersNamesQgis() et getStreetTypes() qui ne sont invoqué qu'à
        l'initialisation.)
        '''

        # On déclare les variables qu'on utilisera à travers la classe
        self.layers = {}
        self.poi = {} 
        self.results = ''
        self.buffers = {}

        # Nous servira pour les calculs de distance
        self.qgs_distance = QgsDistanceArea()

    def getLayersNamesQgis(self):
        '''
        Retourne les noms des couches dans QGIS dans une liste.
        '''
        QgsMessageLog.logMessage("getLayersComboBox", 'GMQ710Analyser', level=Qgis.Info)

        # dictionnaire des couches
        layers_list = {}

        # on parcourt les couches du projet
        for l in QgsProject.instance().mapLayers().values():

            # on ajoute une couche au dictionnaire avec le nom de la couche
            layers_list[l.name()] = l


        # on retourne le nom des couches dans la liste
        return layers_list.keys()
        

    def getLayersQgis(self, dic):
        '''
        Récupère les couches de QGIS à partir d'un dictionaire avec le nom du widget en clé
        et en valeur la couche sélectionné par l'utilisateur.
        '''
        QgsMessageLog.logMessage("getLayersQgis", 'GMQ710Analyser', level=Qgis.Info)

        # On récupère 
        for key, value in dic.items():
            self.layers[key] = QgsProject.instance().mapLayersByName(value)[0]


    def sendInputs(self, inputs):
        '''
        Récupère les valeurs des champs entrés dans la boite de dialogue et valide
        qu'elles sont conformes, retourne une chaîne de caractère avec un message d'erreur
        (vide si valide).
        '''
        QgsMessageLog.logMessage("sendData", 'GMQ710Analyser', level=Qgis.Info)

        # On enregistre comme attribut de classe
        self.inputs = inputs

        # On initialise notre string de résultats que l'on veut vide entre chaque exécution
        self.results = ''
        
        # Contiendra les messages d'erreurs potentiels
        errors = ''

        # On itère sur les champs saisis
        for key, value in self.inputs.items():

            # Erreur si champs vide
            if not value:
                errors += 'Valeur(s) manquante(s) pour le champ "' + key + '".\n'

            else:
                # Errur si champs numérique ne l'est pas
                if key.split('_')[2][:3] == 'int':
                    if not value.isnumeric():
                        errors += 'Valeur doit être de type nombre entier pour le champ "' + key + '".\n'

        return errors


    def getStreetTypes(self):
        '''
        Mis dans une classe pour alléger GMQ710Analyser.py, la fonction retourne simplement une liste
        des champs uniques de types de rues dans la couche utilisée.
        '''
        QgsMessageLog.logMessage("getStreetTypes", 'GMQ710Analyser', level=Qgis.Info)
        types = ['allée',
                'autoroute',
                'avenue',
                'boulevard',
                'carré',
                'carrefour',
                'cercle',
                'chemin',
                'circuit',
                'côte',
                'cours',
                'crête',
                'croissant',
                'impasse',
                'jardin',
                'lane',
                'montée',
                'parc',
                'passage',
                'place',
                'pont',
                'pont-tunnel',
                'promenade',
                'rond-point',
                'route',
                'rue',
                'ruelle',
                'terrasse',
                'tunnel',
                'voie']
        
        return types

    def getGeocodes(self):
        '''
        Récupère les centroides des tronçons de rues correspondants aux adresses de départ et d'arrivée.
        '''
        QgsMessageLog.logMessage("getGeocodes", 'GMQ710Analyser', level=Qgis.Info)

        # Ce string contiendra les messages d'erreurs potentiels
        errors = ''

        # On assigne la couche a une variable moins verbose
        streets = self.layers['gmq_comboBox_strCoucheRoutier']

        # Ce dictionnaire contient les correspondances entre nos variables et les
        # noms des modules PyQt.
        adresses_widgets = {'depart': {'type': 'gmq_comboBox_strTypeDepart',
                               'numero': 'gmq_lineEdit_intDepart',
                               'nom' : 'gmq_lineEdit_strDepart'},
                    'arrive': {'type': 'gmq_comboBox_strTypeArrive',
                               'numero': 'gmq_lineEdit_intArrive',
                               'nom' : 'gmq_lineEdit_strArrive'}}

        # Ce dictionnaire contiendra les points qui seront utilisés pour trouver les stations
        # bixi (aux points de départ, d'arrivée et d'escales)
        self.stops_geom = {}

        # On itère sur les segments de route
        for feature in streets.getFeatures():

            # On itère sur les adresses de départ et d'arrivée
            for key, widget in adresses_widgets.items():
                
                # On valide, dans l'ordre, la correspondance du type, nom et numéro de rue
                if self.inputs[widget['type']].lower() == str(feature.attribute('TYP_VOIE')).lower():
                    if self.inputs[widget['nom']].lower() == str(feature.attribute('NOM_VOIE')).lower():
                        if int(self.inputs[widget['numero']]) >= int(feature.attribute('DEB_DRT')):
                            if int(self.inputs[widget['numero']]) <= int(feature.attribute('FIN_DRT')):
                                
                                # On retourne le centroide du segment (type LineString)
                                pointXY = feature.geometry().centroid().asPoint()

                                # On conserve la géométrie du point
                                self.stops_geom[key] = QgsGeometry.fromPointXY(pointXY)

        # Messages d'erreur si adresses introuvées (dictionnaire vide)
        if not self.stops_geom:
            errors += "Adresses de départ et d'arrivée non localisée\n"
        else:

            # Message d'erreur si une adresse introuvée
            for key, value in self.stops_geom.items():
                if not value:
                    errors += 'Adresse de "' + key + '" non localisée\n'

        # On crée une ligne entre les points d'arrivée et de départ si existant, conservé
        # dans le même dictionaire
        if not errors:
            points = [self.stops_geom['depart'].asPoint(), self.stops_geom['arrive'].asPoint()]
            self.stops_geom['track'] = QgsGeometry.fromPolylineXY(points)

        return errors



    def getBuffers(self):
        '''
        Crée les buffers des stations d'arrivée et de départ ainsi que du tracé,
        conserver en attribut (dictionnaire).
        '''

        # On itère sur le dictionaire
        for key, value in self.stops_geom.items():

            # On crée le buffer avec la bonne valeur selon le type
            if key == 'track':
                self.buffers[key] = self.stops_geom[key].buffer(int(self.inputs['gmq_lineEdit_intBufferItineraire']), 5)
            else:
                self.buffers[key] = self.stops_geom[key].buffer(int(self.inputs['gmq_lineEdit_intBufferAdresses']), 5)



    def getBixiStations(self):
        '''
        Récupère les stations bixi du trajet, d'abord celles d'arrivé et de départ, puis
        celles des escales. Les géométries et les noms des stations sont conservés dans le dictionaire
        self.stops
        '''

        # On utilisera ce string pour les erreurs
        errors = ''

        # On utilisera ce dictionaire pour conserver les stations bixis retenues
        self.stops = {'depart': {'geom': '', 'dist':'', 'nom': ''}, 'arrive': {'geom': '', 'dist':'', 'nom': ''}}

        # On parcours chaque station bixi
        for feat in self.layers['gmq_comboBox_strCoucheBixi'].getFeatures():

            # On vérifie pour les deux localisations
            for key in ['depart', 'arrive']:

                # On continue si la station interesecte notre buffer d'itinéraire et calcule la distance (en m)
                if feat.geometry().intersects(self.buffers[key]):
                    dist = self.qgs_distance.measureLine(self.stops_geom[key].asPoint(), feat.geometry().asPoint())
                    
                    # On assigne la station si c'est la première (pour pouvoir comparer)
                    if not self.stops[key]['dist']:
                        self.stops[key]['dist'] = dist
                        self.stops[key]['geom'] = feat.geometry()
                        self.stops[key]['nom'] = feat.attribute('name')

                    # On assigne la station si c'est la plus proche
                    elif self.stops[key]['dist'] > dist:
                        self.stops[key]['dist'] = dist
                        self.stops[key]['geom'] = feat.geometry()
                        self.stops[key]['nom'] = feat.attribute('name')

        # On retourne un message d'erreur si aucune station n'a été trouvé pour l'une des localisation et on annule l'exécution
        if not self.stops['depart']['geom']:
            errors += "Pas de station Bixi retrouvé à la distance souhaité pour l'adresse de départ, traitement annulé.\n" 
        else:
            self.results += "Station de départ : " + str(self.stops['depart']['nom']) + ' (à ' + str(int(self.stops['depart']['dist'])) + " m de l'adresse). \n"    
        
        if not self.stops['arrive']['geom']:
            errors += "Pas de station Bixi retrouvé à la distance souhaité pour l'adresse d'arrivée, traitement annulé.\n"
        else:
            self.results += "Station d'arrivée : " + str(self.stops['arrive']['nom']) + ' (à ' + str(int(self.stops['arrive']['dist'])) + " m de l'adresse). \n" 

        if errors:
            return errors

        ##############

        # À partir d'ici, on cherche les stations bixi sur l'itinéraire

        # Calcul de distance à vol d'oiseau entre les stations de départ et d'arrivée
        dist_tot = self.qgs_distance.measureLine(self.stops['depart']['geom'].asPoint(), self.stops['arrive']['geom'].asPoint())

        # Nombre d'arrêts à ajouter, retournera 1 escale par km de distance totale (si possible avec les stations)
        nb = int(dist_tot//1000)

        # On assigne les valeurs (x, y) de nos stations de départ et d'arrivé à des variables moins verbose
        x1 = float(self.stops['depart']['geom'].asPoint().x())
        y1 = float(self.stops['depart']['geom'].asPoint().y())
        x2 = float(self.stops['arrive']['geom'].asPoint().x())
        y2 = float(self.stops['arrive']['geom'].asPoint().y())

        # Pour chaque escale(s), on retourne un (des) point(s) de recherche disposé à distance équivalente
        # On trouvera alors la station bixi la plus près de chacun de ces points.
        # I.e., si 1 escale sera au centre du tracé, si 2 escales sera aux tiers, etc. 
        for i in range(nb):
            x = ((x2 - x1) / (nb + 1)) * (i + 1) + x1
            y = ((y2 - y1) / (nb + 1)) * (i + 1) + y1

            # Les valeurs (x, y) calculées sont assignées à un objet QgsGeometry dans le dictionnaire des points de recherche
            self.stops_geom['stop_' + str(i + 1)] = QgsGeometry.fromPointXY(QgsPointXY(x, y))

            # Un sous-dictionnaire est initialisé pour contenir les stations retenues
            self.stops['stop_' + str(i + 1)] = {'geom': '', 'dist':'', 'nom': ''}


        # On parcours les stations bixis pour chercher les plus près de chaque point d'arrêt
        for feat in self.layers['gmq_comboBox_strCoucheBixi'].getFeatures():

            # On ignore l'entité si utilisé par les points de départ ou d'arrivé
            if feat.attribute('name') in [self.stops['depart']['nom'], self.stops['arrive']['nom']]:
                continue

            # Cette boucle est un proxy pour les "stop_#" que l'on vient de créé
            for i in range(nb):
                
                # On poursuit seulement si la station intersecte au tampon de l'itinéraire
                if feat.geometry().intersects(self.buffers['track']):

                    # On forme le nom de la clé
                    key = 'stop_' + str(i + 1)
                    
                    # Distance en mètre entre le point de recherche et la station
                    dist = self.qgs_distance.measureLine(self.stops_geom[key].asPoint(), feat.geometry().asPoint())
                    
                    # On conserve la station si c'est la première (pour pouvoir comparer)
                    if not self.stops[key]['dist']:
                        self.stops[key] = {'geom': feat.geometry(),
                                           'nom': feat.attribute('name'),
                                           'dist': dist}

                    # Aussinon on conserve la station si c'est la plus proche
                    elif self.stops[key]['dist'] > dist:
                        self.stops[key] = {'geom': feat.geometry(),
                                           'nom': feat.attribute('name'),
                                           'dist': dist}

        # Contiendra les clés des stations finales, dans l'ordre
        self.stop_keys = []

        # On supprime les stations doublonnes *après* les avoir créés, dans l'ordre inverse.
        # Si une station est doublonne, il ne devrait pas y avoir d'autres stations plus approprié dans la couche
        # des stations (.. je crois? selon mes observations)
        for i in reversed(range(nb)):
            key = 'stop_' + str(i + 1)

            # La liste des noms contenus est recréé à chaque itération (tient compte des supressions)
            current = [v['nom'] for v in self.stops.values()]

            # Si le nom est présent deux fois ou plus, on supprime
            if current.count(self.stops[key]['nom']) > 1:
                del self.stops[key]
            
            # Sinon on l'ajoute à notre liste
            else:
                self.stop_keys = [key] + self.stop_keys

        # On ajoute les stations de départ et d'arrivé
        self.stop_keys = ['depart'] + self.stop_keys + ['arrive']

        # On va calculer la distance totale de l'itinéraire
        dist_track = 0

        # On itère sur les arrêts
        for i, stop in enumerate(self.stop_keys):
            
            # Sauf pour le premier (départ), on incrémente la distance totale avec la distance entre ce point 
            # et le précédant. 
            if i:
                prev_stop = self.stop_keys[i - 1]
                dist_track += self.qgs_distance.measureLine(self.stops[prev_stop]['geom'].asPoint(), self.stops[stop]['geom'].asPoint())

        # On ajoute la ligne pour la distance et un espacement avec la liste des points d'intérêts qui suvivera
        self.results += 'Distance totale passant par chaque arrêt : ' + str(int(dist_track)) + ' m.\n'
        self.results += '\n-----\n'



        return errors


    def getInterestLocations(self):
        '''
        Récupère les points d'intérêts présent à proximité (selon buffer) des arrêts bixi
        le long de l'itinéraire, enregistre ces informations dans le dictionnaire self.poi 
        '''
        QgsMessageLog.logMessage("getInterestLocations", 'GMQ710Analyser', level=Qgis.Info)

        # Ce dictionnaire contient les association entre les noms de modules des couches
        # avec les attributs (noms et champs) désirés.
        layers = {'gmq_comboBox_strCoucheRecreatif':
                    {'type': 'Installation récréative',
                     'nom': 'NOM',
                     'adresse': 'ARROND',
                     'stop': ''},
                'gmq_comboBox_strCoucheCulturel':
                    {'type': 'Lieu culturel',
                     'nom': 'Nom du lie',
                     'adresse': 'Adresse',
                     'stop': ''},
                'gmq_comboBox_strCouchePatrimoine':
                    {'type': 'Site patrimonial',
                     'nom': 'Nom',
                     'adresse': 'NA',
                     'stop': ''}
                }

        # Incrémenteur pour les points conservés
        count = 1 

        # On récupère la valeur de buffer
        buffer_size = self.inputs['gmq_lineEdit_intBufferItineraire']

        # On crée des buffers aux stations d'escale dans un dictionnaire
        buffers = {}
        for stop, stop_dic in self.stops.items():
            buffers[stop] = stop_dic['geom'].buffer(int(buffer_size), 5)

        # On itère sur les sous-dictionaires de couches (un par couche)
        for layer, dic in layers.items():

            # On itère sur les entités de la couche
            for feat in self.layers[layer].getFeatures():

                # On itère sur les clés des stations
                for stop in self.stops.keys():

                    # On continue si l'entité de la couche intersecte au buffer de la station
                    if feat.geometry().intersects(buffers[stop]):

                        # On récupère le nom
                        name = feat.attribute(dic['nom'])

                        # On valide qu'il s'agit d'un nouveau point d'intérêt en changeant "new_poi"
                        # si le nom est déjà présent dans le dictionnaire (mis en minuscules)
                        new_poi = True
                        for key, value in self.poi.items():
                            if value['nom'].lower() == name.lower():
                                new_poi = False

                        # Si pas une nouvelle entité, on passe au prochain
                        if not new_poi:
                            continue

                        # On convertit le polygone de site patrimonial en point (au centroide de l'intersection)
                        # pour pouvoir l'afficher dans la même couche de résultats
                        if layer == 'gmq_comboBox_strCouchePatrimoine':
                            geom = feat.geometry().intersection(buffers[stop]).centroid()
                        
                        # Aussion on conserve la géométrie telle qu'elle
                        else:
                            geom = feat.geometry()


                        # Sinon, on peuple un dictionnaire avec les attributs souhaités
                        key = 'point_' + str(count)
                        self.poi[key] = {}
                        self.poi[key]['geom'] = geom
                        self.poi[key]['type'] = dic['type']
                        self.poi[key]['nom'] = name
                        self.poi[key]['stop'] = stop

                        # Calcule la distance entre le point d'intérêt et la station bixi
                        self.poi[key]['dist'] = str(int(self.qgs_distance.measureLine(self.stops[stop]['geom'].asPoint(), geom.asPoint())))
                        
                        # Certaines couches n'ont pas de champs apparenté à l'adresse, assigne en fonction de cela
                        if dic['adresse'] != 'NA':
                            self.poi[key]['adresse'] = feat.attribute(dic['adresse'])
                        else:
                            self.poi[key]['adresse'] = 'NA'

                        # On incrémente le compteur
                        count += 1


        # On récupère les points retenus pour chaque escale pour l'impression des résultats
        # On itère sur les clés des stations d'escale
        for stop in self.stop_keys[1:-1]:

            # On introduit l'arrêt dans le résultat
            self.results += "\nPour l'arrêt " + stop[-1] + " (" + self.stops[stop]['nom'] + "), les points d'intérêts suivants ont été trouvés:\n"
            
            # Pour pouvoir afficher autre chose si pas de points trouvés
            no_poi = True

            # On itère sur les points d'intérêts 
            for poi, poi_dic in self.poi.items():

                # On ajoute la ligne aux résultats si pour la station correspondante
                if poi_dic['stop'] == stop:
                    self.results += poi_dic['type'] + ' : ' + poi_dic['nom'] + " (à " + poi_dic['dist'] + " m).\n"
                    no_poi = False

            # On imprime un message si pas de point d'intérêt
            if no_poi:
                self.results += "Aucun point d'intérêt pour cette station, essayer avec une plus grande zone tampon\n"


    def getResultLayers(self):
        '''
        Cette méthode produit les deux couches demandées en mémoire du projet QGIS.
        '''
        QgsMessageLog.logMessage("getInterestLocations", 'GMQ710Analyser', level=Qgis.Info)

        # On crée une couche QgsVectorLayer
        points = QgsVectorLayer("Point?crs=EPSG:32188","Points d'intérêts", "memory")

        # On récupère les champs de la couche dans un objet et on crée des nouveaux champs
        fields = points.dataProvider()
        fields.addAttributes([QgsField("type", QVariant.String), 
                              QgsField("nom", QVariant.String),
                              QgsField("adresse", QVariant.String)])

        # On met à jour les champs de la couche
        points.updateFields()

        # Pour chaque station, on crée une entité qu'on peuple d'une géométrie
        # et des champs nécessaires (dans l'ordre ci-haut), et on l'ajoute à la couche
        for stop, dic in self.stops.items():
            feat = QgsFeature()
            feat.setGeometry(dic['geom'])
            feat.setAttributes(['Station Bixi - Itinéraire', stop, dic['nom']])
            fields.addFeatures([feat])

        # On fait de même pour les points d'intérêts
        for poi, dic in self.poi.items():
            feat = QgsFeature()
            feat.setGeometry(dic['geom'])
            feat.setAttributes([dic['type'], dic['nom'], dic['adresse']])
            fields.addFeatures([feat])

        # On met à jour la couche et on l'ajoute à QGIS
        points.updateExtents()
        QgsProject.instance().addMapLayer(points)

        # On déclare la couche de ligne de façon similaire
        track = QgsVectorLayer("LineString?crs=EPSG:32188","Itinéraire Bixi", "memory")
        fields = track.dataProvider()

        # On créé une liste de points (dans l'ordre) utilisé pour former un LineString
        track_points = []
        for stop in self.stop_keys:
            track_points += [self.stops[stop]['geom'].asPoint()]
        geom = QgsGeometry.fromPolylineXY(track_points)

        # On ajoute l'unique entité à la couche, et la couche à QGIS
        feat = QgsFeature()
        feat.setGeometry(geom)
        fields.addFeatures([feat])
        track.updateExtents()
        QgsProject.instance().addMapLayer(track)
