import subprocess
import re
import os


def geotag_images(image_folder, gps_data_file):
    """
    Embeds GPS data from a text file into images in a folder using ExifTool.

    Args:
        image_folder (str): Path to the folder containing the images.
        gps_data_file (str): Path to the text file containing GPS data.

    Raises:
        ValueError: If the image folder or GPS data file path is invalid.
        RuntimeError: If an error occurs during ExifTool execution.
    """

    # Error handling for input paths
    if not image_folder:
        raise ValueError("Please provide a valid image folder path.")
    if not gps_data_file:
        raise ValueError("Please provide a valid GPS data file path.")

    # Open the GPS data file and read lines
    try:
        with open(gps_data_file, "r") as f:
            gps_data_lines = f.readlines()
    except FileNotFoundError:
        raise ValueError("GPS data file not found.")

    # Process each image and corresponding GPS data line
    for image_filename in os.listdir(image_folder):
        if not image_filename.lower().endswith((".jpg", ".jpeg", ".tif", ".tiff")):
            continue  # Skip non-image files

        # Extract filename without header
        match = re.search(r"([^/.]+)\.", image_filename)

        if not match:
            print(f"Warning: Skipping {image_filename} due to invalid filename format.")
            continue
        image_name = match.group(1)

        # Find corresponding GPS data line
        gps_data_line = None
        for line in gps_data_lines:
            if image_name in line:
                gps_data_line = line.strip()
                break

        if not gps_data_line:
            print(f"Warning: GPS data not found for {image_filename}")
            continue  # Skip if no matching data

        # Extract GPS data (assuming comma-separated format after header)
        try:
            gps_data = gps_data_line.split("\t")[
                2:5
            ]  # Extract latitude, longitude and latitude (indexes 2,3,4)
        except IndexError:
            print(f"Warning: Invalid format in GPS data line for {image_filename}")
            continue  # Skip if data extraction fails

        # Construct ExifTool command
        command = (
            f"exiftool -overwrite_original -m -GPSLatitude={gps_data[0]} "
            f'-GPSLongitude={gps_data[1]} -GPSAltitude={gps_data[2]} "{image_folder}/{image_filename}"'
        )

        print(command)
        # Execute ExifTool command
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        # Check for errors
        if stderr:
            print(f"Error geotagging {image_filename}: {stderr.decode()}")


if __name__ == "__main__":
    image_folder = (
        f"D:/[03] Codes/Python/Cam1/Cam1"  # Replace with your image folder path
    )
    gps_data_file = f"D:/[03] Codes/Python/Cam1/Cam1/caminfo1.txt"  # Replace with your GPS data file path

    try:
        geotag_images(image_folder, gps_data_file)
        print("Geotag process complete.")
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}")
