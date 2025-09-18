<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
require_once '../config.php';

try {
    // For now, we'll return some sample data
    // In a real application, you would query your database for popular items
    $recommendations = [
        [
            'id' => '5',
            'name' => 'Gaming Console X',
            'price' => 499.99,
            'image' => 'images/products/gaming-console.jpg'
        ],
        [
            'id' => '6',
            'name' => '4K Smart TV',
            'price' => 799.99,
            'image' => 'images/products/smart-tv.jpg'
        ],
        [
            'id' => '7',
            'name' => 'Wireless Keyboard',
            'price' => 89.99,
            'image' => 'images/products/keyboard.jpg'
        ],
        [
            'id' => '8',
            'name' => 'Bluetooth Speaker',
            'price' => 149.99,
            'image' => 'images/products/speaker.jpg'
        ]
    ];

    echo json_encode($recommendations);
} catch(PDOException $e) {
    echo json_encode(['error' => 'Failed to fetch popular items: ' . $e->getMessage()]);
}
?> 