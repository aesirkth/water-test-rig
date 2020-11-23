# water-test-rig

Injector Water Test Rig

## Hardware

The water test rig is based around a Raspberry Pi Zero W and a [MCP3008](datasheets/MCP3008.pdf) 10-bit ADC.

## System set-up

### Installing Linux & necessary software

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
    $ sudo apt-get install git -y
    ```

### Installing InfluxDB

(Based around the blog post written by Simon Hearne: https://simonhearne.com/2020/pi-influx-grafana/)

1. Add Influx repositories:

   ```bash
   $ wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key    add -
   $ source /etc/os-release
   $ echo "deb https://repos.influxdata.com/debian $(lsb_release -cs)   stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
   ```

2. Update apt and install InfluxDB:

   ```bash
   $ sudo apt update && sudo apt install -y influxdb
   ```

3. Start InfluxDB service (and set to start at boot):

   ```bash
   $ sudo systemctl unmask influxdb.service
   $ sudo systemctl start influxdb
   $ sudo systemctl enable influxdb.service
   ```

4. Set up InfluxDB database:

   ```bash
   $ influx

   > create database watertestrig
   > use watertestrig
   > create user waterrig with password 'waterrigpw' with all privileges
   > grant all privileges on watertestrig to waterrig

   > create retention policy "rawdata" on "watertestrig" duration 24h replication 1 default

   > exit
   ```

### Install Nginx

```bash
$ sudo apt install -y nginx
```

Enable the service:

```bash
$ sudo systemctl enable nginx
```

Give permissions to the folder:

```bash
$ sudo chmod +755 -R /var/www/html
```

### Installing Python dependencies

```bash
$ sudo apt-get install -y python3-numpy
$ sudo apt-get install -y python3-matplotlib
$ pip3 install adafruit-circuitpython-busdevice
$ pip3 install adafruit-circuitpython-mcp3xxx
$ pip3 install influxdb
$ pip3 install psutil
```

### Clone (or copy) dependencies

```bash
$ git clone https://github.com/aesirkth/water-test-rig
$ cd water-test-rig
```

## System usage

Check the size of the Influx database:

```bash
$ sudo du -sh /var/lib/influxdb/data/watertestrig
92K     /var/lib/influxdb/data/watertestrig
```
