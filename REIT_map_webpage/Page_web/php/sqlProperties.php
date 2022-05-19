<?php
	// Connexion à la base de données "ex_1" se trouvant sur le serveur localhost. Nous nous y connectons avec l'identifiant "postgres", et nous entrons le mot de passe que nous avons créé au moment de l'initialisation de la BD PostgreSQL
	$db = pg_connect("host=localhost dbname= user=postgres password=");

/*  Nous allons rajouter des filtres si nécessaire pour former une requête sous la forme :
		SELECT id, ST_AsGeoJSON("geom", 6) as geom, address, city, province, country, url, 
		(SELECT name FROM reit WHERE id = id_reit) as name_reit,
		ARRAY(SELECT ta.id_sector FROM ta_sector_property ta WHERE ta.id_property = id) as sectors
		FROM property
		WHERE id_reit IN 
			(SELECT id_reit FROM property
			WHERE id_reit IN 
				(SELECT r.id FROM reit r, financial f 
					WHERE r.id = f.id_reit
					AND r.id = 1
					AND f.yield >= 5)
			AND id IN
				(SELECT id_property FROM ta_sector_property
				WHERE id_sector = 1)
			AND province = 'QC'
			GROUP BY id_reit
			HAVING COUNT(id) > 10)


	Cette requête nous retourne tous les points (dans "property", lignes 6 à 9) dont l'id_reit correspond au critères de filtration (lignes 11 à 22)
	Noter que la ligne 8 (ARRAY[...]) nous retourne tous les id_sector associé au id de property dans la table d'association ta_sector_property sous la forme "{1,2}" ou "{3}"
*/

	// Lignes 6 à 9
	$sql = 'SELECT id, ST_AsGeoJSON("geom", 6) as geom, address, city, province, country, url,';
	$sql .= ' (SELECT name FROM reit WHERE id = id_reit) as name_reit,';
	$sql .= ' ARRAY(SELECT ta.id_sector FROM ta_sector_property ta WHERE ta.id_property = id) as sectors';
	$sql .= ' FROM property';

	// Lignes 10 à 14
	$sql .= ' WHERE id_reit IN (SELECT id_reit FROM property WHERE id_reit IN';
	$sql .= ' (SELECT r.id FROM reit r, financial f WHERE r.id = f.id_reit';

	// Si filtration de "reit" ou "yield", on ajoute ces conditions
	if ($_GET['reit'] != 0 || $_GET['yield'] != 0) {

		// Ligne 15
		if ($_GET['reit'] != 0){
			$sql .= ' AND r.id = ' . $_GET['reit'];
		}

		// Ligne 16
		if ($_GET['yield'] != 0){
			$sql .= ' AND f.yield >= ' . $_GET['yield'];
		}

	}

	// On ferme la parenthèse de la 3ème sous-requête (ligne 16), fonctionne sans les conditions des lignes 15 et 16
	$sql .= ")";

	// Si filtration par secteur
	if ($_GET['sector'] != 0) {

		// Lignes 17 à 19
		$sql .= ' AND id in (SELECT id_property FROM ta_sector_property';
		$sql .= ' WHERE id_sector = ' . $_GET['sector'] . ')';
	} 

	// Si filtration par province
	if ($_GET['province'] != 'all') {

		// Ligne 20
		$sql .= " AND province = '" . $_GET['province'] . "'";
	} 
	

	// Clôture de la requêtes, lignes 21 et 22 (fonctionne même sans les conditions des lignes 17 à 20)
	$sql .= " GROUP BY id_reit HAVING COUNT(id) > " . $_GET['resultsMin'] . ")";
	

	// Exécution de la requête SQL
	$query = pg_exec($db, $sql);

	// Création d'une liste vide
	$features = [];
	// Démarrage d'une boucle pour passer à travers tous les résultats de la requête
	for ($i = 0; $i < pg_numrows($query); $i++) {

		$row = pg_fetch_assoc($query,$i);
		$geometry = $row['geom'] = json_decode($row['geom']);

		unset($row['geom']);
		// Nous reconstituons notre 'feature' sur le modèle GeoJSON
		$feature = ['type' => 'Feature', 'geometry' => $geometry, 'properties' => $row];
		array_push($features, $feature);
	};
	// Nous imbriquons nos entités dans une collection d'entités GeoJSON
	$featureCollection = ["type" => "FeatureCollection", "features" => $features];
	echo stripslashes(json_encode($featureCollection));
	pg_close($db);
?>