<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

// Get product ID from request
$productId = isset($_GET['id']) ? $_GET['id'] : null;

if (!$productId) {
    echo json_encode(['error' => 'Product ID is required']);
    exit;
}

// Function to find product by ID
function findProductById($productId) {
    $products = [];
    
    // Read Croma products
    $cromaProducts = json_decode(file_get_contents('../Croma/croma_mobiles_2.json'), true);
    if ($cromaProducts) {
        $products = array_merge($products, $cromaProducts);
    }
    
    // Read Amazon products if available
    if (file_exists('../Amazon/amazon_mobiles.json')) {
        $amazonProducts = json_decode(file_get_contents('../Amazon/amazon_mobiles.json'), true);
        if ($amazonProducts) {
            $products = array_merge($products, $amazonProducts);
        }
    }
    
    // Read Flipkart products if available
    if (file_exists('../Flipkart/flipkart_mobiles.json')) {
        $flipkartProducts = json_decode(file_get_contents('../Flipkart/flipkart_mobiles.json'), true);
        if ($flipkartProducts) {
            $products = array_merge($products, $flipkartProducts);
        }
    }
    
    // Find product by ID
    foreach ($products as $product) {
        if (md5($product['Product Link']) === $productId) {
            return $product;
        }
    }
    
    return null;
}

try {
    $product = findProductById($productId);
    
    if (!$product) {
        echo json_encode(['error' => 'Product not found']);
        exit;
    }
    
    // Extract price and convert to float
    $price = floatval(preg_replace('/[^0-9.]/', '', $product['Price']));
    
    // Format product details
    $formattedProduct = [
        'id' => $productId,
        'name' => $product['Product Name'],
        'price' => $price,
        'price_formatted' => '₹' . number_format($price, 2),
        'image' => $product['Image Link'],
        'link' => $product['Product Link'],
        'brand' => $product['Brand'] ?? 'Unknown',
        'source' => $product['Source'] ?? 'Unknown',
        'storage' => $product['Storage'] ?? null,
        'ram' => $product['RAM'] ?? null
    ];
    
    echo json_encode($formattedProduct);
} catch(Exception $e) {
    echo json_encode(['error' => $e->getMessage()]);
}
?> 