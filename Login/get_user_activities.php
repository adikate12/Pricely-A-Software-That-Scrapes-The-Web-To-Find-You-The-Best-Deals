<?php
require_once 'vendor/autoload.php';

// MongoDB connection
$mongoUri = "mongodb://localhost:27017";
$client = new MongoDB\Client($mongoUri);
$db = $client->pricely;
$collection = $db->useractivities;

// Function to get user activities
function getUserActivities($userId = null) {
    global $collection;
    
    $filter = [];
    if ($userId) {
        $filter = ['userId' => $userId];
    }
    
    $options = [
        'sort' => ['timestamp' => -1] // Sort by timestamp descending
    ];
    
    $cursor = $collection->find($filter, $options);
    return iterator_to_array($cursor);
}

// Get activities for all users or specific user
$userId = isset($_GET['user_id']) ? $_GET['user_id'] : null;
$activities = getUserActivities($userId);

// Display activities
echo "<h2>User Activities</h2>";
echo "<table border='1'>";
echo "<tr><th>User ID</th><th>Username</th><th>Action</th><th>Page</th><th>Timestamp</th><th>Metadata</th></tr>";

foreach ($activities as $activity) {
    echo "<tr>";
    echo "<td>" . htmlspecialchars($activity['userId']) . "</td>";
    echo "<td>" . htmlspecialchars($activity['username']) . "</td>";
    echo "<td>" . htmlspecialchars($activity['action']) . "</td>";
    echo "<td>" . htmlspecialchars($activity['page']) . "</td>";
    echo "<td>" . htmlspecialchars($activity['timestamp']) . "</td>";
    echo "<td>" . htmlspecialchars(json_encode($activity['metadata'])) . "</td>";
    echo "</tr>";
}

echo "</table>";
?> 