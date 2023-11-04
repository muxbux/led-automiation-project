<?php
$host = "localhost";
$username = "write";
$password = "write";
$database = "rgbdata";

// Create a connection
$conn = new mysqli($host, $username, $password, $database);

// Check the connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Initialize an array to store validation errors
    $errors = array();

    $enableDarkMode = false;
    $prioritizeRFID = false;
    $prioritizeLAN = false;
    $enableIndicators = false;

    $enableDarkMode = isset($_POST["enableDarkMode"]) ? 1 : 0;
    $prioritizeRFID = isset($_POST["prioritizeRFID"]) ? 1 : 0;
    $prioritizeLAN = isset($_POST["prioritizeLAN"]) ? 1 : 0;
    $enableIndicators = isset($_POST["enableIndicators"]) ? 1 : 0;


    if (isset($_POST["brightness"]) && is_numeric($_POST["brightness"])) {
        $brightness = intval($_POST["brightness"]);
    } else {
        $errors[] = "Invalid brightness value.";
    }

    if (empty($_POST["darkModeStartTime"])) {
        $darkModeStartTime = null;
    } else {
        $darkModeStartTime = $_POST["darkModeStartTime"];
    }
    
    if (empty($_POST["darkModeEndTime"])) {
        $darkModeEndTime = null;
    } else {
        $darkModeEndTime = $_POST["darkModeEndTime"];
    }
    

    if (empty($errors)) {
        // Insert data into the database
        $sql = "INSERT INTO off_settings (enableDarkMode, prioritizeRFID, prioritizeLAN, enableIndicators, brightness, darkModeStartTime, darkModeEndTime)
                VALUES (?, ?, ?, ?, ?, ?, ?)";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("iiiiiss", $enableDarkMode, $prioritizeRFID, $prioritizeLAN, $enableIndicators, $brightness, $darkModeStartTime, $darkModeEndTime);

        if ($stmt->execute()) {
            echo "Off settings added successfully.";
        } else {
            echo "Error: " . $stmt->error;
        }

        $stmt->close();
    } else {
        foreach ($errors as $error) {
            echo $error . "<br>";
        }
    }

    $conn->close();
}

header("Location: /"); // Replace "/" with the desired URL
exit;
?>
