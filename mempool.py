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
            blocks = data[:7] # 7 row limitation of UnicornHATmini
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
        if fee == 1:
            r = 255
            g = 255
            b = 255
        elif fee <= 5:
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
    for block in blocks:
        block_size = block['blockSize']
        row_length = min(math.ceil(block_size / (2 * 1024 * 1024) * 17), 17)  # Calculate row length
        fee_range = block['feeRange']

        segment_colors = calculate_segment_colors(fee_range)

        led_row = []
        segment_lengths = [row_length // 7] * 7
        remainder = row_length % 7

        for i in range(remainder):
            segment_lengths[i] += 1

        for i in range(7):
            led_row.extend([segment_colors[i]] * segment_lengths[i])

        led_row.extend([(0, 0, 0)] * (17 - row_length))
        led_pixels.append(led_row)

    return led_pixels

# Main program
unicornhatmini = UnicornHATMini()

while True:
    blocks = get_mempool_data()
    led_pixels = convert_data_to_led_pixels(blocks)

    for y, led_row in enumerate(led_pixels):
        for x, pixel_color in enumerate(led_row):
            r, g, b = pixel_color
            unicornhatmini.set_pixel(x, y, r, g, b)

    unicornhatmini.show()
    time.sleep(15)  # Wait for 15 seconds before refreshing the data and screen