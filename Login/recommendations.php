<?php
// Ensure we're outputting JSON
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

// Enable error reporting but don't display errors
error_reporting(E_ALL);
ini_set('display_errors', 0);

// Function to get products based on user preferences
function getProductsForUser($userId) {
    try {
        // Use full path to Python and the script
        $pythonPath = "C:\\Users\\dell\\AppData\\Local\\Programs\\Python\\Python312\\python.exe";
        $scriptPath = __DIR__ . "/../recommendation/test_enhanced_recommendations.py";
        
        if (!file_exists($pythonPath)) {
            throw new Exception("Python executable not found at: " . $pythonPath);
        }
        
        if (!file_exists($scriptPath)) {
            throw new Exception("Recommendation script not found at: " . $scriptPath);
        }
        
        // Get user email from session or request
        $email = isset($_SESSION['email']) ? $_SESSION['email'] : 
                (isset($_GET['email']) ? $_GET['email'] : 'anonymous');
        
        // Ensure user ID and email are properly escaped
        $userId = escapeshellarg($userId);
        $email = escapeshellarg($email);
        $command = escapeshellarg($pythonPath) . " " . escapeshellarg($scriptPath) . " " . $email;
        error_log("Executing command: " . $command);
        
        $output = shell_exec($command);
        
        if ($output === null) {
            error_log("Python script returned null output for user: " . $email);
            return getBasicRecommendations($email);
        }
        
        // Log the raw output for debugging
        error_log("Python script output: " . $output);
        
        $recommendations = json_decode($output, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            error_log("Invalid JSON output from Python script for user: " . $email);
            return getBasicRecommendations($email);
        }
        
        if (empty($recommendations)) {
            error_log("No recommendations returned from Python script for user: " . $email);
            return getBasicRecommendations($email);
        }
        
        // Log successful recommendations
        error_log("Successfully retrieved " . count($recommendations) . " recommendations for user: " . $email);
        
        return $recommendations;
    } catch (Exception $e) {
        error_log("Error in getProductsForUser: " . $e->getMessage());
        error_log("Stack trace: " . $e->getTraceAsString());
        return getBasicRecommendations($email ?? 'anonymous');
    }
}

function getBasicRecommendations($email = 'anonymous') {
    try {
    $products = [];
        $seenProducts = []; // Track seen products by name and brand
        $brandCounts = []; // Track number of products per brand
        
        // Get a unique seed based on email
        $seed = crc32($email);
        srand($seed);
        
        // Read products from Croma
        $cromaProducts = json_decode(file_get_contents(__DIR__ . '/../Croma/croma_mobiles_2.json'), true);
    if ($cromaProducts) {
            // Shuffle products to get different recommendations for different users
            shuffle($cromaProducts);
            foreach ($cromaProducts as $product) {
                $brand = extractBrand($product['Product Name']);
                $key = $product['Product Name'] . '_Croma';
                
                // Limit to 2 products per brand
                if (!isset($seenProducts[$key]) && (!isset($brandCounts[$brand]) || $brandCounts[$brand] < 2)) {
                    $seenProducts[$key] = true;
                    $price = extractPrice($product['Price']);
                    if ($price > 0) {
                        $products[] = [
                            'id' => md5($product['Product Link']),
                            'name' => $product['Product Name'],
                            'brand' => $brand,
                            'price' => $price,
                            'source' => 'Croma',
                            'image_url' => $product['Image Link'],
                            'product_url' => $product['Product Link']
                        ];
                        $brandCounts[$brand] = ($brandCounts[$brand] ?? 0) + 1;
                    }
                }
            }
        }
        
        // Read products from Amazon
        $amazonProducts = json_decode(file_get_contents(__DIR__ . '/../Amazon/amazon_products.json'), true);
        if ($amazonProducts) {
            // Shuffle products to get different recommendations for different users
            shuffle($amazonProducts);
            foreach ($amazonProducts as $product) {
                $brand = extractBrand($product['Product Name']);
                $key = $product['Product Name'] . '_Amazon';
                
                // Limit to 2 products per brand
                if (!isset($seenProducts[$key]) && (!isset($brandCounts[$brand]) || $brandCounts[$brand] < 2)) {
                    $seenProducts[$key] = true;
                    $price = extractPrice($product['Price']);
                    if ($price > 0) {
                        $products[] = [
                            'id' => md5($product['Product Link']),
                            'name' => $product['Product Name'],
                            'brand' => $brand,
                            'price' => $price,
                            'source' => 'Amazon',
                            'image_url' => $product['Image URL'],
                            'product_url' => $product['Product Link']
                        ];
                        $brandCounts[$brand] = ($brandCounts[$brand] ?? 0) + 1;
                    }
                }
            }
        }
        
        // Read products from Flipkart
        $flipkartProducts = json_decode(file_get_contents(__DIR__ . '/../Home/flipkart_mobiles_2.json'), true);
        if ($flipkartProducts) {
            // Shuffle products to get different recommendations for different users
            shuffle($flipkartProducts);
            foreach ($flipkartProducts as $product) {
                $brand = extractBrand($product['Product Name']);
                $key = $product['Product Name'] . '_Flipkart';
                
                // Limit to 2 products per brand
                if (!isset($seenProducts[$key]) && (!isset($brandCounts[$brand]) || $brandCounts[$brand] < 2)) {
                    $seenProducts[$key] = true;
                    $price = extractPrice($product['Price']);
                    if ($price > 0) {
                        $products[] = [
                            'id' => md5($product['Product Link']),
                            'name' => $product['Product Name'],
                            'brand' => $brand,
                            'price' => $price,
                            'source' => 'Flipkart',
                            'image_url' => $product['Image URL'],
                            'product_url' => $product['Product Link']
                        ];
                        $brandCounts[$brand] = ($brandCounts[$brand] ?? 0) + 1;
                    }
                }
            }
        }
        
        // Sort products by price and brand diversity
        usort($products, function($a, $b) {
            // First sort by brand count (to prioritize less represented brands)
            $brandCompare = ($a['brand'] === $b['brand']) ? 0 : 1;
            if ($brandCompare !== 0) {
                return $brandCompare;
            }
            // Then sort by price (ascending)
            return $a['price'] - $b['price'];
        });
        
        // Return top 5 unique products
        return array_slice($products, 0, 5);
    } catch (Exception $e) {
        error_log("Error in getBasicRecommendations: " . $e->getMessage());
        return [];
    }
}

// Helper function to extract brand from product name
function extractBrand($productName) {
    $commonBrands = ['Nothing', 'vivo', 'OPPO', 'Samsung', 'Xiaomi', 'Realme', 'iQOO', 'OnePlus', 'Motorola', 'Apple', 'Redmi', 'POCO', 'Infinix', 'Google'];
    foreach ($commonBrands as $brand) {
        if (stripos($productName, $brand) === 0) {
            return $brand;
        }
    }
    return 'Unknown';
}

// Helper function to extract price from string
function extractPrice($priceStr) {
    if (empty($priceStr)) return 0;
    // Remove currency symbol and commas
    $price = preg_replace('/[^0-9.]/', '', $priceStr);
    return floatval($price);
}

try {
    // Get user ID and email from session or request
    session_start();
    $userId = isset($_SESSION['user_id']) ? $_SESSION['user_id'] : 'anonymous';
    $email = isset($_SESSION['email']) ? $_SESSION['email'] : 
            (isset($_GET['email']) ? $_GET['email'] : 'anonymous');
    
    // Get recommendations for the user
    $recommendations = getProductsForUser($userId);
    
    // Format the recommendations to match the expected structure
    $formattedRecommendations = array_map(function($product) {
        return [
            'id' => $product['id'],
            'name' => trim($product['name']),
            'price' => $product['price'],
            'image' => $product['image_url'],
            'link' => $product['product_url'],
            'price_formatted' => '₹' . number_format($product['price'], 2),
            'brand' => $product['brand'],
            'source' => $product['source']
        ];
    }, $recommendations);
    
    // Limit to 5 recommendations
    $formattedRecommendations = array_slice($formattedRecommendations, 0, 5);
    
    echo json_encode($formattedRecommendations);
} catch (Exception $e) {
    error_log("Error in recommendations.php: " . $e->getMessage());
    echo json_encode([]);
}
?> 