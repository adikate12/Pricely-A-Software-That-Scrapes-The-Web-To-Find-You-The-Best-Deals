<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
require_once '../config.php';

$userId = isset($_GET['userId']) ? $_GET['userId'] : 'anonymous';

try {
    // For now, we'll return some sample data
    // In a real application, you would query your database for recently viewed items
    $recommendations = [
        [
            'id' => '9',
            'name' => 'Smart Home Hub',
            'price' => 199.99,
            'image' => 'images/products/smart-hub.jpg'
        ],
        [
            'id' => '10',
            'name' => 'Fitness Tracker',
            'price' => 79.99,
            'image' => 'images/products/fitness-tracker.jpg'
        ],
        [
            'id' => '11',
            'name' => 'Wireless Mouse',
            'price' => 49.99,
            'image' => 'images/products/mouse.jpg'
        ],
        [
            'id' => '12',
            'name' => 'Portable SSD',
            'price' => 129.99,
            'image' => 'images/products/ssd.jpg'
        ]
    ];

    echo json_encode($recommendations);
} catch(PDOException $e) {
    echo json_encode(['error' => 'Failed to fetch recently viewed items: ' . $e->getMessage()]);
}
?> 