<?php
	// Connexion à la base de données "ex_1" se trouvant sur le serveur localhost. Nous nous y connectons avec l'identifiant "postgres", et nous entrons le mot de passe que nous avons créé au moment de l'initialisation de la BD PostgreSQL
	$db = pg_connect("host=localhost dbname= user=postgres password=");


/*  Nous allons former une requête sous la forme :
		SELECT DISTINCT *
		FROM reit r, financial f
		WHERE r.id = 1
		AND r.id = f.id_reit;

	Nous retourne toutes les information provenant de REIT (par id distinct) et celles associées dans la table "financial"
*/

	$sql = 'SELECT DISTINCT r.*, f.*, COUNT(p.id) as nb_property FROM reit r, financial f, property p';
	$sql .= ' WHERE r.id = ' . $_GET['reit_id'];
	$sql .= ' AND r.id = f.id_reit';
	$sql .= ' AND p.id_reit = r.id';
	$sql .= ' GROUP BY r.id, f.id_reit;';

	// Exécution de la requête SQL
	$query = pg_exec($db, $sql);

	$row = pg_fetch_assoc($query, 0);

	echo stripslashes(json_encode($row));
	pg_close($db);
?>