import math
import os
import requests
import signal
import sys
import time
from PIL import Image, ImageDraw, ImageFont
from unicornhatmini import UnicornHATMini

# Function to retrieve mempool data from the API
def get_mempool_data():
    # Attempt to load Environment Variable
    node_address = os.getenv("MEMPOOL_NODE_ADDRESS")

    if not node_address:
        # Check if the .env file exists and load the environment variables from it
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                for line in f:
                    key, value = line.strip().split("=")
                    os.environ[key] = value
            node_address = os.getenv("MEMPOOL_NODE_ADDRESS")

        # Failed to find value in .env file
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
                blocks = data[:8]  # Retrieve 8 blocks
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

# Function to retrieve block data from the API
def get_block_data():
    node_address = os.getenv("MEMPOOL_NODE_ADDRESS")
    
    if not node_address:
        # Check if the .env file exists and load the environment variables from it
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                for line in f:
                    key, value = line.strip().split("=")
                    os.environ[key] = value
            node_address = os.getenv("MEMPOOL_NODE_ADDRESS")

        # Failed to find value in .env file
        if not node_address:
            node_address = input("Enter your mempool.space self-hosted node address: ")
            os.environ["MEMPOOL_NODE_ADDRESS"] = node_address

            # Save the environment variable to the user's machine
            with open(".env", "w") as f:
                f.write(f"MEMPOOL_NODE_ADDRESS={node_address}\n")

    if node_address:
        url = f"{node_address}/api/v1/blocks"
        max_retries = 3
        retry_interval = 15  # seconds
        retries = 0

        while retries < max_retries:
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                blocks = data[:8]  # Retrieve 8 blocks
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

# Function for new block alert
def new_block_alert(block):
    height = block['height']
    reward = block['extras']['reward']
    reward = reward / 100000000  # Convert fee to whole bitcoin
    reward = round(reward, 3)  # Round fee to 3 decimal places
    tx_count = block['tx_count']
    median_fee = block['extras']['medianFee']

    # Text to scroll when new block is mined
    text = f"    New Block {height}    Reward: {reward} BTC    Tx Count: {tx_count}    Median Fee: ~{median_fee} sat/vB    "

    # Load a 5x7 pixel font
    font = ImageFont.truetype("5x7.ttf", 8)
    
    # Measure the width of text
    text_width = font.getsize(text)

    # Create a new PIL image big enough to fit the text
    image = Image.new('P', (text_width[0] + display_width + display_width, display_height), 0)
    draw = ImageDraw.Draw(image)
    
    # Draw the text into the image
    draw.text((display_width, -1), text, font=font, fill=255)

    # Align off right edge on display
    offset_x = 0

    # Draw text from image based
    while (offset_x + display_width <= image.size[0]):
        for y in range(display_height):
            for x in range(display_width):
                if image.getpixel((x + offset_x, y)) == 255:
                    unicornhatmini.set_pixel(x, y, 242, 169, 0) # Bitcoin Orange 
                else:
                    unicornhatmini.set_pixel(x, y, 0, 0, 0)

        # Scroll
        offset_x += 1

        unicornhatmini.show()
        time.sleep(0.05)

    return 0

# Function to calculate the length of the column by the block size
def calculate_bar_length(block_size):
    bar_length = min(math.ceil(block_size / (2 * 1024 * 1024) * display_height), display_height)
    return bar_length

# Function to adjust fee range to match bar length
def form_fit_fees(fee_range, bar_length):
    old_length = len(fee_range)
    new_length = bar_length

    # Calculate the scaling factor for linear interpolation
    scaling_factor = (old_length - 1) / (new_length - 1)

    # Calculate the new fee range using linear interpolation
    fee_range = [fee_range[math.floor(i * scaling_factor)] for i in range(new_length)]

    return fee_range

# Function to calculate the colors based on fee range
def rgb_fees(fee, data_type):
    if data_type == "mempool":
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
            # Red to Fuschia
            r = 255
            g = 0
            b = int(255 * max(((fee - 500) / 500), 1))
    else:
        # Blue to Red 
        r = int(255 * min(math.pow((fee / 60), 2), 1)) # exponential growth
        g = 0
        b = int(255 * max(math.pow(((60 - fee) / 60), 0.5), 0)) # exponential shrink

    return r, g, b

# Function to convert mempool data to LED pixels
def convert_mempool_to_led_pixels(mempool):
    led_pixels = []

    for i, block in enumerate(mempool):
        bar_length = calculate_bar_length(block['blockSize'])
        fee_range = form_fit_fees(block['feeRange'], bar_length)

        # Create an array of colors representing the fee range of the block
        segment_colors = []
        for fee in fee_range:
            rgb_fee = rgb_fees(fee, "mempool")
            segment_colors.append(rgb_fee)

        # Create an array to be colored
        segment_lengths = [bar_length // display_height] * display_height
        remainder = bar_length % display_height

        # Picking the segments of the array to color
        for i in range(remainder):
            segment_lengths[i] += 1

        # Color segments using array of colors
        led_bar = []
        for i in range(display_height):
            led_bar.extend([segment_colors[i % len(segment_colors)]] * segment_lengths[i])
            
        # Add Empty pixels to fill column to display edge
        led_bar.extend([(0, 0, 0)] * (display_height - len(led_bar)))
        # while len(led_bar) < display_height:
        #     led_bar.append((0, 0, 0))

        # Append the bar to LED Pixel Matrix
        led_pixels.append(led_bar)

    # LED Pixel Matrix
    return led_pixels

# Function to convert block data to LED pixels
def convert_block_data_to_led_pixels(blocks):
    led_pixels = []

    for block in blocks:
        bar_length = calculate_bar_length(block['size'])
        medianFee = block['extras']['medianFee']
        led_color = rgb_fees(medianFee, "block")

        # Create a column of LED pixels with the same color       
        led_bar = [led_color] * bar_length

        # Append the pixel data to led_pixels
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
unicornhatmini.set_brightness(0.1)

# Track the most recent block mined
latest_block = 0

# Main Program Loop
while True:
    blocks = get_block_data()

    # First run and whenever a new block is found
    if blocks[0]['height'] > latest_block:
        block_pixels = convert_block_data_to_led_pixels(blocks)
    
        # New block found
        if latest_block != 0:
            new_block_alert(blocks[0]) 

        # Refresh the entire screen to 0, 0, 0 (off)
        unicornhatmini.clear()

        # Set the LED pixels for the blocks
        for y, led_row in enumerate(block_pixels):
            for x, pixel_color in enumerate(led_row):
                r, g, b = pixel_color
                # Set the pixel for the right 8 columns at the corresponding position
                unicornhatmini.set_pixel(9 + y, display_height - x - 1, r, g, b)
                
        # Update tracking of most recent block mined
        latest_block = blocks[0]['height']
                    
    # Pull mempool data and change to LED values
    mempool = get_mempool_data()
    mempool_pixels = convert_mempool_to_led_pixels(mempool)

    # Set the LED pixels for the mempool
    for y, led_row in enumerate(mempool_pixels):
        for x, pixel_color in enumerate(led_row):
            r, g, b = pixel_color
            unicornhatmini.set_pixel(7 - y, display_height - x - 1, r, g, b)

    unicornhatmini.show()
    time.sleep(5)  # Wait for 5 seconds before refreshing the data and screen