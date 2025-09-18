<?php
// Database credentials
$host = 'localhost';
$dbUsername = 'root';
$dbPassword = '';
$dbName = 'project';

// Create a connection
$conn = new mysqli($host, $dbUsername, $dbPassword, $dbName);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Don't close the connection here
// The connection will be closed in the files that use it
?>
