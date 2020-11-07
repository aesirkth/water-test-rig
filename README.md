# water-test-rig

Injector Water Test Rig

## Hardware

The water test rig is based around a Raspberry Pi Zero W and a [MCP3008](datasheets/MCP3008.pdf) 10-bit ADC.

## Installing Linux

To install the right dependencies, the following guide is followed: https://www.losant.com/blog/getting-started-with-the-raspberry-pi-zero-w-without-a-monitor

The steps are as such (copied here for future reference):

1. Download Raspbian Lite (https://www.raspberrypi.org/downloads/raspberry-pi-os/)
2. Download Balena Etcher (https://etcher.io/)
3. Flash the Raspbian image to the MicroSD card with Etcher
4. Remove & reinsert the MicroSD card
5. Create a file called `ssh` in the root of the card. This enables SSH access.
6. Create a file called `wpa_supplicant.conf` in the root of the card and enter the following (with `LF` line endings!):

   ```
   country=SE
   ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
   update_config=1

   network={
   ssid="<ENTER SSID>"
   scan_ssid=1
   psk="<ENTER WIFI PASSWORD>"
   key_mgmt=WPA-PSK
   }
   ```

   This sets up a connection to a Wi-Fi network.

7. Insert the MicroSD card to the Raspberry Pi Zero W and boot it up.
8. SSH into the Raspberry Pi with its IP (check the DHCP lease table on the router or similar...):
   ```bash
   $ ssh pi@<ip address>
   ```
   You will be asked if the certificate should be trusted. Answer yes.
   The password is `raspberry`.
9. Change the password to `aesir2020` (it doesn't matter if anybody knows this password, we're not supposed to run this Pi against the global internet) by running:
   ```bash
   $ passwd
   ```
10. Update the software on the Pi (this might take a few minutes, so grab some drink):
    ```bash
    $ sudo apt-get update && sudo apt-get upgrade -y
    ```
11. Install `pip3`:
    ```bash
    $ sudo apt-get install python3-pip -y
    ```
