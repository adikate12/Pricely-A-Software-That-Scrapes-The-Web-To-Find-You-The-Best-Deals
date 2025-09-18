<?php
// test-activity.php - Test script to verify activity tracking

// Include the track_interactions.php script
include 'track_interactions.php';

// Create a test activity
$testActivity = [
    'userId' => 'test_user',
    'username' => 'Test User',
    'action' => 'test_action',
    'page' => '/test-page',
    'sessionId' => 'test_session_' . time(),
    'metadata' => [
        'test' => true,
        'timestamp' => date('Y-m-d H:i:s')
    ]
];

// Convert to JSON
$jsonData = json_encode($testActivity);

// Set up cURL request to the Node.js server
$nodeServerUrl = 'http://localhost:3000/api/activity-tracker/track';
$ch = curl_init($nodeServerUrl);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_POSTFIELDS, $jsonData);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'Content-Length: ' . strlen($jsonData)
]);

// Execute the request
$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

// Output the result
echo "<h1>Activity Tracking Test</h1>";
echo "<p>Test activity data:</p>";
echo "<pre>" . htmlspecialchars($jsonData) . "</pre>";
echo "<p>Response from Node.js server (HTTP Code: $httpCode):</p>";
echo "<pre>" . htmlspecialchars($response) . "</pre>";

// Check for errors
if (curl_errno($ch)) {
    echo "<p>Error: " . curl_error($ch) . "</p>";
}

// Close cURL session
curl_close($ch);
?> 