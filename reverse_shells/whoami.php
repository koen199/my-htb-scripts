<?php
// Run the `whoami` shell command
$user = trim(shell_exec('whoami'));

// Display the result
echo "Linux user: " . htmlspecialchars($user);
?>