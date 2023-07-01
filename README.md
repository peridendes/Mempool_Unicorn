# Mempool Unicorn

[![License](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](LICENSE)

## Description

Mempool Unicorn is a Bitcoin transaction mempool visualization tool. It provides real-time insights into the pending transactions from your self-hosted instance of [mempool.space](https://mempool.space).

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Requirements

You must enable SPI on your Raspberry Pi:

* Run: `sudo raspi-config nonint do_spi 0`

## Installation

To install and set up Mempool Unicorn, follow these steps:

1. Install Pimoroni UnicornHATMini Stable library from PyPi:
    ```shell
    $sudo pip3 install unicornhatmini

2. Clone the repository:
   ```shell
   $ git clone https://github.com/peridendes/Mempool_Unicorn.git
   $ cd Mempool_Unicorn

## Usage
1. Run the script:
    ```shell
    $ python3 mempool.py

## Features

Mempool Unicorn offers the following features:

- [x] Real-time visualization of pending blocks
- [ ] Interactive features, such as highlighting the selected block or providing visual indicators for enhanced user experience.
- [ ] Navigate between different blocks and easily switch the selected block for detailed viewing.
- [ ] Display additional details about the selected block, such as block height, transaction count, fees, timestamp, and other relevant information.

## Contributing

If you would like to contribute to Mempool Unicorn, please follow these guidelines:

1. Fork the repository.
2. Create a new branch.
3. Make your changes and commit them.
4. Push your changes to your forked repository.
5. Submit a pull request.

## License

This project is licensed under the [GPL-3.0 License](LICENSE).

## Contact

If you have any questions or suggestions, feel free to reach out:

- Email: peridendes@reacher.me
- NOSTR: [peridendes](https://primal.net/profile/npub1fwxq6fzp6st48r5ytpum3xcl4fedrkplz9qt2uza03z25taszdpq7q7h0m)

We appreciate your interest and support in the project!

Please donate if you find this project useful.
![](https://github.com/peridendes/peridendes.github.io/blob/main/assets/images/qr.png?raw=true)