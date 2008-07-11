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

if (!array_key_exists('debug',$_GET)) {
	error_reporting(0);
}

$config['dbname'] = 'servers.db';
$config['table'] = 'servers';

$config['default-port'] = 8154;

define("PACKAGE","TSNet4 Metaserver");
define("VERSION","0.0.1-rc1");

# stampa l'header della pagina
function template_header($name='',$host='',$port='',$desc='',$ping='0') {
	print <<<EOT
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="it" lang="it">
<head>
EOT;

?>
<title><?php print PACKAGE." versione ".VERSION; ?></title>
</head>

<body bgcolor="green" style="color: white; font-family: Verdana,Arial;" link="white" alink="white" vlink="white">

<p align="center">
<font size="7">Lista server</font>
</p>

<div align="center">
<form method="get" action="<?php print $_SERVER['PHP_SELF']; ?>">
<b>Nome:</b> <input type="text" name="name" value="<?php print $name; ?>"/>
<b>Indirizzo:</b> <input type="text" name="host" value="<?php print $host; ?>"/>
<b>Porta:</b> <input type="text" size="5" name="port" value="<?php print $port; ?>"/>
<b>Descrizione:</b> <input type="text" name="desc"  value="<?php print $desc; ?>"/>
<b>Ping:</b> <input type="checkbox" name="ping" value="1" <?php if ($ping == '1') print "checked"; ?>/>
<input type="hidden" name="op" value="list"/>
<input type="submit" value="Filtra"/>
</form>
</div>

<hr/>

<?php
}

# stampa il footer della pagina
function template_footer() {
?>

</body>
</html>

<?php
}

function template_table_footer() {
?>

</tbody>

</table>

<?php
}

function template_table_header() {
?>

<table align="center" rules="groups" width="75%" border="2">

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

<?php
}

function template_no_results() {
?>
<p align="center">
<b>Nessun risultato.</b>
</p>

<?php
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
	desc	varchar(500) not null
	)");

	return $res;
}

# ritorna il valore della chiave se presente, altrimenti ''
function return_has_key($array,$key,$error='') {
	if (array_key_exists($key,$array)) return $array[$key];
	return $error;
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

	if ($host) $where .= " and host like '%$host%'";
	if ($port and is_numeric($port)) $where .= " and port = '".intval($port)."'";
	if ($name) $where .= " and name like '%$name%'";
	if ($desc) $where .= " and desc like '%$desc%'";

	$res = sqlite_query($db,"select * from $table $where");

	if (create_if_not_exists($db,$table)) return get_server_list($db,$table,$host,$port,$name,$desc);

	return sqlite_fetch_all($res);
}

# collegati al database
$db = sqlite_open("servers.db");

# dobbiamo fare qualcosa
if (array_key_exists('op',$_GET)) {

	if ($_GET['op'] == 'register') {

		$name = return_has_key($_GET,'name',null);
		$host = return_has_key($_GET,'host',null);
		$port = return_has_key($_GET,'port',null);

		if ($name == null or $host == null) {
			print 'EARGS';
			exit;
		}

		if ($port == null) {
			$port = $config['default-port'];
		}

		elseif (!is_numeric($port) or (intval($port) < 1 or intval($port) > 65536)) {
			print 'EPORT';
			exit;
		}

		$desc = return_has_key($_GET,'desc');
		print register_server($db,$config['table'],$host,$port,$name,$desc);
	}

	elseif ($_GET['op'] == 'list') {
		$name = return_has_key($_GET,'name',null);
		$host = return_has_key($_GET,'host',null);
		$port_s = return_has_key($_GET,'port',null);
		$port = intval($port_s);
		$ping = return_has_key($_GET,'ping',0);

		if (!is_numeric($port_s) or ($port < 1 or $port > 65536)) {
			$port_s = '';
			$port = 0;
		}

		$desc = return_has_key($_GET,'desc',null);

		template_header($name,$host,$port_s,$desc,$ping);

		$tot = get_server_list($db,$config['table'],$host,$port,$name,$desc);

		$count = count($tot);

		if ($count == 0) {
			template_no_results();

		} else {

			$count = 0;
			foreach ($tot as $val) {

				$r = true;
				if (return_has_key($_GET,'ping') == '1') {

					# testa il server per un secondo
					$sock = socket_create(AF_INET,SOCK_STREAM,SOL_TCP);
					socket_set_nonblock($sock);
					$r = socket_connect($sock,$val['host'],intval($val['port']));
					socket_set_block($sock);

					while ($r == false) {
						$tmp = null;
						$tim = array($sock);
						$r = socket_select($tmp,$tim,$tmp,1);
						if ($r > 0) {
							$r = true;
						} else {
							break;
						}
					}
				}

				if ($r) {
					if ($count == 0) template_table_header();

					template_entry($val['host'],$val['port'],$val['name'],$val['desc']);
					$count++;
				}
			}

			if ($count == 0) template_no_results();
			else template_table_footer();
		}

		template_footer();
	}
}

?>
