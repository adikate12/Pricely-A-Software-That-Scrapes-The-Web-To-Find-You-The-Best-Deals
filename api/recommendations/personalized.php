<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
require_once '../config.php';

$userId = isset($_GET['userId']) ? $_GET['userId'] : 'anonymous';

try {
    // For now, we'll return some sample data
    // In a real application, you would query your AI recommendation system here
    $recommendations = [
        [
            'id' => '1',
            'name' => 'Smartphone X',
            'price' => 999.99,
            'image' => 'images/products/smartphone-x.jpg'
        ],
        [
            'id' => '2',
            'name' => 'Wireless Earbuds Pro',
            'price' => 199.99,
            'image' => 'images/products/earbuds-pro.jpg'
        ],
        [
            'id' => '3',
            'name' => 'Smart Watch Series 5',
            'price' => 299.99,
            'image' => 'images/products/smart-watch.jpg'
        ],
        [
            'id' => '4',
            'name' => 'Laptop Pro',
            'price' => 1299.99,
            'image' => 'images/products/laptop-pro.jpg'
        ]
    ];

    echo json_encode($recommendations);
} catch(PDOException $e) {
    echo json_encode(['error' => 'Failed to fetch recommendations: ' . $e->getMessage()]);
}
?> 