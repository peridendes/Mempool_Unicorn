import logging
import math
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
        node_address = input("Enter your mempool.space self-hosted node address: ")
        os.environ["MEMPOOL_NODE_ADDRESS"] = node_address

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
    return None

# Function to calculate the length of the column by the block size
def calculate_bar_length(block_size):
    bar_length = min(math.ceil(block_size / (2 * 1024 * 1024) * display_height), display_height)
    logging.debug(f"Block Size: {block_size}, Bar Length: {bar_length}")
    return bar_length

# Function to calculate the segment colors based on fee range
def calculate_segment_colors(fee_range):
    segment_colors = []

    for fee in fee_range:
        if fee <= 3:
            # Green
            r = 0
            g = 255
            b = 0
        elif fee <= 60:
            # Gradient from yellow to red
            r = 255
            g = int(255 * (60 - fee) / 57)
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

    blocks = blocks[::-1]  # Reverse the order of blocks

    for block in blocks:
        column_length = calculate_bar_length(block['blockSize'])
        fee_range = block['feeRange']

        segment_colors = calculate_segment_colors(fee_range)
        segment_colors.reverse()

        led_col = []
        segment_lengths = [column_length // display_height] * display_height
        remainder = column_length % display_height

        for i in range(remainder):
            segment_lengths[i] += 1

        led_col.extend([(0, 0, 0)] * (display_height - column_length))

        for i in range(display_height):
            led_col.extend([segment_colors[i % len(segment_colors)]] * segment_lengths[i])

        led_pixels.append(led_col)

    return led_pixels

# Main program
unicornhatmini = UnicornHATMini()

rotation = 0
if len(sys.argv) > 1:
    try:
        rotation = int(sys.argv[1])
    except ValueError:
        print("Usage: {} <rotation>".format(sys.argv[0]))
        sys.exit(1)

unicornhatmini.set_rotation(rotation)
display_width, display_height = unicornhatmini.get_shape()

# Too bright for the eye
unicornhatmini.set_brightness(0.1)

while True:
    blocks = get_mempool_data()

    # Debugging
    if blocks is not None:
        for i, block in enumerate(blocks):
            median_fee = block['medianFee']
            fee_range = block['feeRange']
            bar_length = calculate_bar_length(block['blockSize'])
            logging.debug(f"Block {i + 1}, Median Fee: {median_fee}, Fee Range: {fee_range}, Bar Length: {bar_length}")

    led_pixels = convert_data_to_led_pixels(blocks)

    for y, led_row in enumerate(led_pixels):
        for x, pixel_color in enumerate(led_row):
            r, g, b = pixel_color
            unicornhatmini.set_pixel(y, x, r, g, b)

    unicornhatmini.show()
    time.sleep(5)  # Wait for 5 seconds before refreshing the data and screen
