<?php

$config = array(
  'DB_HOST' => 'localhost',
  'DB_USERNAME' => 'mngr',
  'DB_PASSWORD' => '',
  'DB_DATABASE' => 'users'
);

$conn = mysqli_connect($config['DB_HOST'], $config['DB_USERNAME'], $config['DB_PASSWORD'], $config['DB_DATABASE']);

if (mysqli_connect_errno($conn)) {
  echo "Failed connecting. " . mysqli_connect_error() . "<br/>";
}