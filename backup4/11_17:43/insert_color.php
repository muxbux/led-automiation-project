<?php
// Database configuration
$host = "localhost";
$username = "write";
$password = "write";
$database = "rgbdata";

// Create a connection
$conn = new mysqli($host, $username, $password, $database);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

function calculateBrightness($r, $g, $b) {
    return (0.299 * $r + 0.587 * $g + 0.114 * $b);
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (isset($_POST["color"])) {
        // Handle the "Color Settings" form
        // ... (previous color settings code)
        $color = $_POST["color"];
        // Convert the hex color to RGB values
        list($r, $g, $b) = sscanf($color, "#%02x%02x%02x");
        // Calculate the hue (you can reuse the existing calculation for hue)
        $max = max($r, $g, $b);
        $min = min($r, $g, $b);
        if ($max === $min) {
            $hue = 0;
        } elseif ($max === $r) {
            $hue = 60 * (($g - $b) / ($max - $min));
        } elseif ($max === $g) {
            $hue = 60 * (2 + ($b - $r) / ($max - $min));
        } elseif ($max === $b) {
            $hue = 60 * (4 + ($r - $g) / ($max - $min));
        }
        if (!is_numeric($hue)) {
            $hue = 0;
        }
        $brightness = calculateBrightness($r, $g, $b);
        $mode = $_POST["mode"];
        $sql = "INSERT INTO settings (mode, r, g, b, hue, brightness) VALUES ('$mode', '$r', '$g', '$b', '$hue', '$brightness')";
        if ($conn->query($sql) === true) {
            echo "Record added successfully.";
        } else {
            echo "Error: " . $sql . "<br>" . $conn->error;
        }

    } elseif (isset($_POST["secColor"]) && isset($_POST["minColor"]) && isset($_POST["hourColor"])) {
        // Handle the "Clock Settings" form
        $secColor = $_POST["secColor"];
        $minColor = $_POST["minColor"];
        $hourColor = $_POST["hourColor"];
        list($sec_r, $sec_g, $sec_b) = sscanf($secColor, "#%02x%02x%02x");
        list($min_r, $min_g, $min_b) = sscanf($minColor, "#%02x%02x%02x");
        list($hour_r, $hour_g, $hour_b) = sscanf($hourColor, "#%02x%02x%02x");
        $sec_hue = calculateHue($sec_r, $sec_g, $sec_b);
        $min_hue = calculateHue($min_r, $min_g, $min_b);
        $hour_hue = calculateHue($hour_r, $hour_g, $hour_b);
        
        // Insert the hue values and the current timestamp
        $sql = "INSERT INTO clock_colors (sec_hue, min_hue, hour_hue, timestamp) VALUES ('$sec_hue', '$min_hue', '$hour_hue', NOW())";
        if ($conn->query($sql) === true) {
            echo "Clock colors added successfully.";
        } else {
            echo "Error: " . $sql . "<br>" . $conn->error;
        }
    }
    $conn->close();
}

function calculateHue($r, $g, $b) {
    $max = max($r, $g, $b);
    $min = min($r, $g, $b);
    if ($max === $min) {
        return 0;
    }
    $delta = $max - $min;
    $hue = 0;
    if ($max === $r) {
        $hue = 60 * ((($g - $b) / $delta) % 6);
    } elseif ($max === $g) {
        $hue = 60 * ((($b - $r) / $delta) + 2);
    } elseif ($max === $b) {
        $hue = 60 * ((($r - $g) / $delta) + 4);
    }
    return $hue;
}
header("Location: /"); // Replace "/" with the desired URL
exit; // Make sure to exit to prevent further script execution
?>
