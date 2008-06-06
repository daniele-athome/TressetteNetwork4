<?php
# Metaserver PHP script
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#
#    TressetteNetwork4 - copyright (C) daniele_athome
#
#    TressetteNetwork4 is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    TressetteNetwork4 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with TressetteNetwork4; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

$config['dbname'] = 'servers.db';
$config['table'] = 'servers';

# stampa l'header della pagina
function template_header() {
	print <<<EOT
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="it" lang="it">
<head>
<title>TressetteNetwork4 Metaserver</title>
</head>

<body bgcolor="green" style="color: white; font-family: Verdana,Arial;" link="white" alink="white" vlink="white">

<p align="center">
<font size="7">Lista server</font>
</p>

<div align="center">
<form method="get" action="{$_SERVER['PHP_SELF']}">
<b>Nome:</b> <input type="text" name="name"/>
<b>Indirizzo:</b> <input type="text" name="host"/>
<b>Porta:</b> <input type="text" size="5" name="port"/>
<b>Descrizione:</b> <input type="text" name="desc"/>
<input type="hidden" name="op" value="list"/>
<input type="submit" value="Filtra"/>
</form>
</div>

<hr/>

<table align="center" rules="groups" width="75%" border="2">


EOT;
}

# stampa il footer della pagina
function template_footer() {
	print <<<EOT
</tbody>

</table>

</body>
</html>

EOT;
}

function template_table_header() {
	print <<<EOT
<thead>

<!-- table header -->
<tr align="center" bgcolor="#aa0000">
<td><b>Nome</b></td>
<td><b>Indirizzo</b></td>
<td width="5%"><b>Porta</b></td>
<td><b>Descrizione</b></td>
</tr>

</thead>

<tbody>

EOT;
}

function template_entry($host,$port,$name,$desc) {
	print <<<EOT
<tr align="center">
<td>$name</td>
<td><a href="tsnet4://$host:$port">$host</a></td>
<td>$port</td>
<td>$desc</td>
</tr>

EOT;
}

# crea la tabella per i server registrati
function create_table($db,$name) {
	$res = sqlite_exec($db,"create table $name (
	id		integer autoincrement primary key,
	host	varchar(100) not null,
	port	integer(5) not null,
	name	varchar(255) not null,
	desc	varchar(500)
	)");

	return $res;
}

# ritorna il valore della chiave se presente, altrimenti ''
function return_has_key($array,$key,$null=false) {
	if (array_key_exists($key,$array)) return $array[$key];
	if ($null) return null;
	return '';
}

# crea la tabella se c'e' stato l'errore "table not exists (1)"
function create_if_not_exists($db,$table) {
	if (sqlite_last_error($db) == 1) {
		create_table($db,$table);
		return true;
	}
	return false;
}

# registra il server nel database
function register_server($db,$table,$host,$port,$name,$desc) {

	$res = sqlite_query($db,"select id from $table where host='$host' and port='$port'");

	if (create_if_not_exists($db,$table)) return register_server($db,$table,$host,$port,$name,$desc);

	if (sqlite_has_more($res)) return 'EALREADY';

	if (sqlite_exec($db,"insert into servers values(null,'$host','$port','$name','$desc')"))
		return 'OK';

	return 'EREGISTER';
}

# ritorna il resultset filtrato della lista dei server
# se un filtro e' null non verra' incluso nelle condizioni di ricerca
function get_server_list($db,$table,$host=null,$port=null,$name=null,$desc=null) {
	$where = "where id > 0";

	if ($host != null) $where .= " and host like '%$host%'";
	if ($port != null and is_numeric($port)) $where .= " and port = '".intval($port)."'";
	if ($name != null) $where .= " and name like '%$name%'";
	if ($desc != null) $where .= " and desc like '%$desc%'";

	$res = sqlite_query($db,"select * from $table $where");

	if (create_if_not_exists($db,$table)) return get_server_list($db,$table,$host,$port,$name,$desc);

	return sqlite_fetch_all($res);
}

# collegati al database
$db = sqlite_open("servers.db");

# dobbiamo fare qualcosa
if (array_key_exists('op',$_GET)) {

	if ($_GET['op'] == 'register') {

		$name = return_has_key($_GET,'name');
		$host = return_has_key($_GET,'host');
		$port = intval(return_has_key($_GET,'port'));
		$desc = return_has_key($_GET,'desc');
		print register_server($db,$config['table'],$host,$port,$name,$desc);
	}

	elseif ($_GET['op'] == 'list') {
		template_header();
		template_table_header();
		$name = return_has_key($_GET,'name',true);
		$host = return_has_key($_GET,'host',true);
		$port = intval(return_has_key($_GET,'port'),true);
		$desc = return_has_key($_GET,'desc',true);
		$tot = get_server_list($db,$config['table'],$host,$port,$name,$desc);
		foreach ($tot as $val) {
			template_entry($val['host'],$val['port'],$val['name'],$val['desc']);
		}
		template_footer();
	}
}

?>
