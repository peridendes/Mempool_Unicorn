import logging
import math
import numpy as np
import os
import requests
import sys
import time
from unicornhatmini import UnicornHATMini

logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG

# Function to retrieve mempool data from the API
def get_mempool_data():
    node_address = os.getenv("MEMPOOL_NODE_ADDRESS")
    if not node_address:
        # Check if the .env file exists and load the environment variables from it
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                for line in f:
                    key, value = line.strip().split("=")
                    os.environ[key] = value
            node_address = os.getenv("MEMPOOL_NODE_ADDRESS")

        if not node_address:
            node_address = input("Enter your mempool.space self-hosted node address: ")
            os.environ["MEMPOOL_NODE_ADDRESS"] = node_address

            # Save the environment variable to the user's machine
            with open(".env", "w") as f:
                f.write(f"MEMPOOL_NODE_ADDRESS={node_address}\n")

    if node_address:
        url = f"{node_address}/api/v1/fees/mempool-blocks"
        max_retries = 3
        retry_interval = 15  # seconds
        retries = 0

        while retries < max_retries:
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                blocks = data[:8]  # Retrieve 8 blocks from the API
                return blocks
            except (requests.exceptions.RequestException, ValueError) as e:
                print(f"Error occurred: {e}")
                print("Retrying after 15 seconds...")
                time.sleep(retry_interval)
                retries += 1

        print("Max retries exceeded. Exiting...")
    else:
        print("No MEMPOOL_NODE_ADDRESS found. Exiting...")

    return None

# Function to calculate the length of the column by the block size
def calculate_bar_length(block_size):
    bar_length = min(math.ceil(block_size / (2 * 1024 * 1024) * display_height), display_height)
    return bar_length

# Function to adjust fee range to match bar length
def form_fit_fees(fee_range, bar_length):

    # Create an array of indices evenly spaced within the range of the fee segments
    x_old = np.linspace(0, len(fee_range) - 1, len(fee_range))

    # Create an array of indices evenly spaced within the desired bar length
    x_new = np.linspace(0, len(fee_range) - 1, bar_length)

    # Use linear interpolation to estimate new values based on the old fee range
    fee_range = np.interp(x_new, x_old, fee_range).tolist()

    logging.debug(f"{fee_range}")

    return fee_range

# Function to calculate the segment colors based on fee range
def calculate_segment_colors(fee_range):
    segment_colors = []

    for fee in fee_range:
        if fee <= 10:
            # Blue to Green
            r = 0
            g = int(255 * fee / 10)
            b = int(255 * (10 - fee) / 10)
        elif fee <= 20:
            # Green to Yellow
            r = int(255 * (fee - 10) / 10)
            g = 255
            b = 0
        elif fee <= 60:
            # Yellow to Red
            r = 255
            g = int(255 * (60 - fee) / 50)
            b = 0
        else:
            # Gradient from red to fuchsia
            r = 255
            g = 0
            b = int(255 * (max(fee_range) - fee) / (max(fee_range) - 60))

        segment_colors.append((r, g, b))

    return segment_colors

# Function to convert mempool data to LED pixels
def convert_data_to_led_pixels(blocks):
    led_pixels = []

    for i, block in enumerate(blocks):
        bar_length = calculate_bar_length(block['blockSize'])
        logging.debug(f"Block: {i}, Bar Length: {bar_length}\n{block['feeRange']}")
        fee_range = form_fit_fees(block['feeRange'], bar_length)

        segment_colors = calculate_segment_colors(fee_range)

        led_bar = []
        segment_lengths = [bar_length // display_height] * display_height
        remainder = bar_length % display_height

        for i in range(remainder):
            segment_lengths[i] += 1

        for i in range(display_height):
            led_bar.extend([segment_colors[i % len(segment_colors)]] * segment_lengths[i])
            
        led_pixels.append(led_bar)

    return led_pixels

# Main program
unicornhatmini = UnicornHATMini()

rotation = 180
if len(sys.argv) > 1:
    try:
        rotation = int(sys.argv[1])
    except ValueError:
        print("Usage: {} <rotation>".format(sys.argv[0]))
        sys.exit(1)

unicornhatmini.set_rotation(rotation)
display_width, display_height = unicornhatmini.get_shape()

# Too bright for the eye
unicornhatmini.set_brightness(0.05)

while True:
    blocks = get_mempool_data()
    led_pixels = convert_data_to_led_pixels(blocks)

    for y, led_row in enumerate(led_pixels):
        for x, pixel_color in enumerate(led_row):
            r, g, b = pixel_color
            unicornhatmini.set_pixel(8 - y, 6 - x, r, g, b)

    unicornhatmini.show()
    time.sleep(5)  # Wait for 5 seconds before refreshing the data and screen