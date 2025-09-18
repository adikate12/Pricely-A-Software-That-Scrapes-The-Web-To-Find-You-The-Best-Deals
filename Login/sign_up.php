<?php
include 'connection.php';
session_start(); // Start the session
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Initialize message variables
$_SESSION['error'] = '';
$_SESSION['success'] = '';

// Check if form is submitted
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    // Check if it's a registration
    if (isset($_POST['register'])) {
        // Registration
        $username = $_POST['username'];
        $email = $_POST['email'];
        $password = $_POST['password']; // No hashing here

        // Prepare and bind for insertion
        $stmt = $conn->prepare("INSERT INTO login_data (username, email, password) VALUES (?, ?, ?)");
        if (!$stmt) {
            die("Prepare failed: " . $conn->error);
        }
        $stmt->bind_param("sss", $username, $email, $password); // Use plain password
        
        // Execute statement
        if ($stmt->execute()) {
            $_SESSION['success'] = "User registered successfully!";
        } else {
            $_SESSION['error'] = "Error: " . $stmt->error;
        }

        // Close the statement
        $stmt->close();
    } else {
        // Login
        $email = $_POST['email'];
        $password = $_POST['password'];
        
        // Prepare and bind
        $sql = "SELECT password FROM login_data WHERE email = ?";
        $stmt = $conn->prepare($sql);
        if (!$stmt) {
            die("Prepare failed: " . $conn->error);
        }
        $stmt->bind_param("s", $email);
        
        // Execute statement
        if (!$stmt->execute()) {
            die("Execute failed: " . $stmt->error);
        }
        $stmt->store_result();
        
        // Check if email exists
        if ($stmt->num_rows > 0) {
            // Bind result
            $stmt->bind_result($storedPassword);
            $stmt->fetch();
            
            // Check if the provided password matches the stored one
            if ($password === $storedPassword) { // Compare plain passwords
                echo "Login successful! Welcome, " . htmlspecialchars($email) . ".";
                // Optionally, redirect to a dashboard or home page
            } else {
                $_SESSION['error'] = "Invalid password.";
            }
        } else {
            $_SESSION['error'] = "No user found with that email.";
        }
        
        // Close the statement
        $stmt->close();
    }

    // Close the connection after all operations
    $conn->close();
    
    // Redirect back to the login page to display messages
    header("Location: login.html"); // Change to your login PHP page
    exit();
}
?>
