import requests
import time
from unicornhatmini import UnicornHATMini

# Function to retrieve mempool data from the API
def get_mempool_data():
    response = requests.get('https://mempool.space/api/v1/fees/mempool-blocks')
    data = response.json()
    blocks = data[:7]  # Consider only the first 7 blocks
    return blocks

# Function to calculate the segment colors based on fee range
def calculate_segment_colors(fee_range):
    segment_colors = []

    for fee in fee_range:
        if fee <= 30:
            # Gradient from green (1) to yellow to orange to red (300)
            r = int(255 * (fee / 30))
            g = int(255 * (1 - (fee / 30)))
            b = 0
        else:
            # Fuchsia for fees over 300
            r = 255
            g = 0
            b = 255

        segment_colors.append((r, g, b))

    return segment_colors

# Function to convert mempool data to LED pixels
def convert_data_to_led_pixels(blocks):
    max_block_size = max(block['blockSize'] for block in blocks)

    led_pixels = []
    for block in blocks:
        block_size = block['blockSize']
        row_length = int(block_size / max_block_size * 17)
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
import requests
import time
from unicornhatmini import UnicornHATMini

# Function to retrieve mempool data from the API
def get_mempool_data():
    response = requests.get('https://mempool.space/api/v1/fees/mempool-blocks')
    data = response.json()
    blocks = data[:7]  # Consider only the first 7 blocks
    return blocks

# Function to calculate the segment colors based on fee range
def calculate_segment_colors(fee_range):
    segment_colors = []

    for fee in fee_range:
        if fee <= 30:
            # Gradient from green (1) to yellow to orange to red (300)
            r = int(255 * (fee / 30))
            g = int(255 * (1 - (fee / 30)))
            b = 0
        else:
            # Fuchsia for fees over 300
            r = 255
            g = 0
            b = 255

        segment_colors.append((r, g, b))

    return segment_colors

# Function to convert mempool data to LED pixels
def convert_data_to_led_pixels(blocks):
    max_block_size = max(block['blockSize'] for block in blocks)

    led_pixels = []
    for block in blocks:
        block_size = block['blockSize']
        row_length = int(block_size / max_block_size * 17)
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
