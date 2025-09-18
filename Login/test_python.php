<?php
header('Content-Type: text/plain');

// Test Python version with full path
$pythonPath = "C:\\Users\\dell\\AppData\\Local\\Programs\\Python\\Python312\\python.exe";
$pythonVersion = shell_exec(escapeshellarg($pythonPath) . " --version");
echo "Python Version: " . $pythonVersion . "\n\n";

// Test Python script execution
$testScript = "print('Hello from Python')";
$tempFile = tempnam(sys_get_temp_dir(), 'test_');
file_put_contents($tempFile, $testScript);

$output = shell_exec(escapeshellarg($pythonPath) . " " . escapeshellarg($tempFile));
echo "Python Script Output: " . $output . "\n\n";

// Test the actual recommendation script
$scriptPath = __DIR__ . "/../recommendation/test_enhanced_recommendations.py";
echo "Testing recommendation script: " . $scriptPath . "\n";
$recommendationOutput = shell_exec(escapeshellarg($pythonPath) . " " . escapeshellarg($scriptPath) . " anonymous");
echo "Recommendation Script Output: " . $recommendationOutput . "\n\n";

// Test file permissions
echo "Current Directory: " . __DIR__ . "\n";
echo "Directory Contents:\n";
$files = scandir(__DIR__);
foreach ($files as $file) {
    echo $file . " - " . fileperms(__DIR__ . '/' . $file) . "\n";
}

// Clean up
unlink($tempFile);
?> 