<?php
// Check if a file was uploaded successfully
if (isset($_FILES['file_upload']) && $_FILES['file_upload']['error'] === UPLOAD_ERR_OK) {
  $file_name = $_FILES['file_upload']['name'];
  $temp_path = $_FILES['file_upload']['tmp_name'];

  // Example: Move the file to a permanent directory
  $target_dir = "uploads/";
  $target_file = $target_dir . basename($file_name);

  if (move_uploaded_file($temp_path, $target_file)) {
    echo "File uploaded successfully.";
  } else {
    echo "There was an error moving the file.";
  }
} else {
  echo "No file was uploaded or there was an upload error.";
}
?>
