<?php
header('Content-Type: application/json');

// Get user email from session
session_start();
$user_email = isset($_SESSION['email']) ? $_SESSION['email'] : null;

if (!$user_email) {
    echo json_encode(['error' => 'User not logged in']);
    exit();
}

// Execute Python script to get recommendations
$command = escapeshellcmd('python ../recommendation/test_enhanced_recommendations.py ' . escapeshellarg($user_email) . ' 2>&1');
$output = shell_exec($command);

if ($output === null) {
    echo json_encode(['error' => 'Failed to execute recommendation script']);
    exit();
}

// Log the raw output for debugging
error_log("Python script output: " . $output);

// Split output into lines
$lines = explode("\n", $output);

// Find the last line that contains JSON (the actual recommendations)
$recommendations_json = '';
foreach (array_reverse($lines) as $line) {
    if (strpos($line, '[') === 0 && strpos($line, ']') === strlen($line) - 1) {
        $recommendations_json = $line;
        break;
    }
}

if (empty($recommendations_json)) {
    echo json_encode(['error' => 'No recommendations found in script output']);
    exit();
}

// Parse the recommendations
$recommendations = json_decode($recommendations_json, true);

if (json_last_error() !== JSON_ERROR_NONE) {
    echo json_encode([
        'error' => 'Invalid JSON output from recommendation script',
        'details' => json_last_error_msg()
    ]);
    exit();
}

// If we got here, we have valid recommendations
echo json_encode($recommendations);
?> 