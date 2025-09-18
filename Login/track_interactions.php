<?php
// Set headers for JSON response
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

// Enable error reporting but don't display errors
error_reporting(E_ALL);
ini_set('display_errors', 0);

// MongoDB connection
require_once 'mongodb_connection.php';

// Check if request method is POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

try {
    // Get the raw POST data
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);

    if (!$data) {
        throw new Exception('Invalid JSON data received');
    }

    // Validate required fields
    $requiredFields = ['user_id', 'action', 'product_id', 'timestamp'];
    foreach ($requiredFields as $field) {
        if (!isset($data[$field])) {
            throw new Exception("Missing required field: $field");
        }
    }

    // Get MongoDB collection
    $collection = get_collection('useractivities');

    // Prepare activity document
    $activity = [
        'userId' => $data['user_id'],
        'email' => $data['email'] ?? 'anonymous',
        'username' => $data['username'] ?? 'Anonymous User',
        'action' => $data['action'],
        'page' => $data['page'] ?? 'unknown',
        'timestamp' => new MongoDB\BSON\UTCDateTime(strtotime($data['timestamp']) * 1000),
        'metadata' => [
            'productId' => $data['product_id'],
            'productName' => $data['product_name'] ?? '',
            'brand' => $data['brand'] ?? '',
            'category' => $data['category'] ?? 'mobile',
            'price' => $data['price'] ?? 0,
            'source' => $data['source'] ?? 'unknown'
        ]
    ];

    // Insert activity into MongoDB
    $result = $collection->insertOne($activity);

    // Create logs directory if it doesn't exist
    $logsDir = __DIR__ . '/../logs';
    if (!file_exists($logsDir)) {
        mkdir($logsDir, 0777, true);
    }

    // Log the interaction
    $logFile = $logsDir . '/user_interactions.log';
    $logEntry = sprintf(
        "[%s] User: %s, Action: %s, Product: %s\n",
        $data['timestamp'],
        $data['user_id'],
        $data['action'],
        $data['product_id']
    );
    file_put_contents($logFile, $logEntry, FILE_APPEND);

    // Return success response
    echo json_encode([
        'status' => 'success',
        'message' => 'Interaction tracked successfully',
        'data' => $data
    ]);

} catch (Exception $e) {
    // Return error response
    http_response_code(400);
    echo json_encode([
        'status' => 'error',
        'message' => $e->getMessage()
    ]);
}
?>
