import requests
import math
import time
from unicornhatmini import UnicornHATMini

# Function to retrieve mempool data from the API
def get_mempool_data():
    url = 'https://mempool.space/api/v1/fees/mempool-blocks'
    max_retries = 3
    retry_interval = 15  # seconds
    retries = 0

    while retries < max_retries:
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            blocks = data[:8] # Retrieve 8 blocks from the API
            return blocks
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"Error occurred: {e}")
            print("Retrying after 15 seconds...")
            time.sleep(retry_interval)
            retries += 1

    print("Max retries exceeded. Exiting...")
    return None

# Function to calculate the segment colors based on fee range
def calculate_segment_colors(fee_range):
    segment_colors = []

    for fee in fee_range:
        if fee <= 5:
            # Gradient from white to blue
            r = int(255 * (5 - fee) / 4)
            g = int(255 * (5 - fee) / 4)
            b = 255
        elif fee <= 10:
            # Gradient from blue to green
            r = 0
            g = int(255 * (fee - 5) / 5)
            b = int(255 * (10 - fee) / 5)
        elif fee <= 15:
            # Gradient from green to yellow
            r = int(255 * (fee - 10) / 5)
            g = 255
            b = 0
        elif fee <= 20:
            # Gradient from yellow to orange
            r = 255
            g = int(255 - (127 * (20 - fee) / 5 ))
            b = 0
        elif fee <= 60:
            # Gradient from orange to red
            r = 255
            g = int(128  * (60 - fee) / 40)
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
        block_size = block['blockSize']
        column_length = min(math.ceil(block_size / (2 * 1024 * 1024) * 7), 7)  # Calculate column length
        fee_range = block['feeRange']

        segment_colors = calculate_segment_colors(fee_range)
        segment_colors.reverse()
        
        led_col = []
        segment_lengths = [column_length // 7] * 7
        remainder = column_length % 7

        for i in range(remainder):
            segment_lengths[i] += 1

        led_col.extend([(0, 0, 0)] * (7 - column_length))
        for i in range(len(segment_colors)):
            led_col.extend([segment_colors[i]] * segment_lengths[i])

        led_pixels.append(led_col)

    return led_pixels

# Main program
unicornhatmini = UnicornHATMini()

while True:
    blocks = get_mempool_data()
    led_pixels = convert_data_to_led_pixels(blocks)

    for y, led_row in enumerate(led_pixels):
        for x, pixel_color in enumerate(led_row):
            r, g, b = pixel_color
            unicornhatmini.set_pixel(y, x, r, g, b)

    unicornhatmini.show()
    time.sleep(15)  # Wait for 15 seconds before refreshing the data and screen