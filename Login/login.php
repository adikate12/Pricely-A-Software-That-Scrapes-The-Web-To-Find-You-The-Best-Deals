<?php
include 'connection.php';  // Use the connection file instead of creating new connection

// Handle form submission
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $email = $_POST['email'];
    $password = $_POST['password'];
    $action = $_POST['action'];

    if ($action == "register") {
        // Registration process
        $username = $_POST['username'];  // Get username from form
        
        // Check if email already exists
        $check_sql = "SELECT * FROM login_data WHERE email = ?";
        $check_stmt = $conn->prepare($check_sql);
        $check_stmt->bind_param("s", $email);
        $check_stmt->execute();
        $result = $check_stmt->get_result();
        
        if ($result->num_rows > 0) {
            // Email already exists, redirect to invalid.html
            header("Location: invalid.html");
            exit();
        } else {
            // Insert new user with username
            $sql = "INSERT INTO login_data (username, email, password) VALUES (?, ?, ?)";
            $stmt = $conn->prepare($sql);
            $stmt->bind_param("sss", $username, $email, $password);
            
            if ($stmt->execute()) {
                // Registration successful, redirect to login.html
                header("Location: login.html");
                exit();
            } else {
                // Registration failed, redirect to invalid.html
                header("Location: invalid.html");
            exit();
        }
        }
    } 
    else if ($action == "login") {
        // Login process
        $sql = "SELECT * FROM login_data WHERE email = ?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("s", $email);
        $stmt->execute();
        $result = $stmt->get_result();
        
        if ($result->num_rows > 0) {
            $user = $result->fetch_assoc();
            if ($password === $user['password']) {
                // Login successful, start session and redirect to home page
                session_start();
                $_SESSION['email'] = $email;
                $_SESSION['username'] = $user['username'];  // Store username in session
                
                // Create a temporary HTML file to set sessionStorage
                $tempHtml = <<<HTML
<!DOCTYPE html>
<html>
<head>
    <title>Redirecting...</title>
    <script>
        // Store user info in sessionStorage
        sessionStorage.setItem('user_email', '$email');
        sessionStorage.setItem('user_name', '{$user['username']}');
        
        // Redirect to home page
        window.location.href = '../Home/index.html';
    </script>
</head>
<body>
    <p>Redirecting to home page...</p>
</body>
</html>
HTML;
                
                // Output the temporary HTML
                echo $tempHtml;
                exit();
            } else {
                // Invalid password, redirect to invalid.html
                header("Location: invalid.html");
                exit();
            }   
        } else {
            // User not found, redirect to invalid.html
            header("Location: invalid.html");
            exit();
        }
    }
}

$conn->close();
?> 






