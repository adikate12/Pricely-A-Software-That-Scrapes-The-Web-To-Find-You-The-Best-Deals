<?php
header('Content-Type: application/json');

// Get user email from session
session_start();
$user_email = isset($_SESSION['email']) ? $_SESSION['email'] : null;

if (!$user_email) {
    echo json_encode(['error' => 'User not logged in']);
    exit();
}

// Get POST data
$data = json_decode(file_get_contents('php://input'), true);
$product_id = $data['productId'] ?? null;
$action = $data['action'] ?? null;

if (!$product_id || !$action) {
    echo json_encode(['error' => 'Missing required data']);
    exit();
}

// Connect to MongoDB
require_once '../Login/connection.php';

// Create activity document
$activity = [
    'userId' => $user_email,
    'action' => $action,
    'metadata' => [
        'productId' => $product_id,
        'timestamp' => new MongoDB\BSON\UTCDateTime()
    ]
];

// Insert activity into MongoDB
try {
    $result = $db->useractivities->insertOne($activity);
    echo json_encode(['success' => true, 'message' => 'Activity tracked successfully']);
} catch (Exception $e) {
    echo json_encode(['error' => 'Failed to track activity: ' . $e->getMessage()]);
}
?> 