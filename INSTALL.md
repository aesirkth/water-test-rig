# System set-up

## Installing Linux & necessary software

To install the right dependencies, the following guide is followed: https://www.losant.com/blog/getting-started-with-the-raspberry-pi-zero-w-without-a-monitor

The steps are as such (copied here for future reference):

1. Download Raspbian Lite (https://www.raspberrypi.org/downloads/raspberry-pi-os/)
2. Download Balena Etcher (https://etcher.io/)
3. Flash the Raspbian image to the MicroSD card with Etcher
4. Remove & reinsert the MicroSD card
5. Create a file called `ssh` in the root of the card. This enables SSH access.

6. Edit `config.txt` in the root of the card and add the following (with `LF` line endings!):

   ```
   dtoverlay=dwc2
   ```

7. Edit `config.txt` in the root of the card and add the following after `rootwait` (with `LF` line endings!):

   ```
   modules-load=dwc2,g_ether
   ```

   It should look like this (or similar):

   ```
   console=serial0,115200 console=tty1 root=PARTUUID=075f9017-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait modules-load=dwc2,g_ether
   ```

8. Make sure that your computer supports Bonjour: https://learn.adafruit.com/bonjour-zeroconf-networking-for-windows-and-linux/
9. Enable network forwarding from your computer to the RPI: https://learn.adafruit.com/turning-your-raspberry-pi-zero-into-a-usb-gadget/ethernet-tweaks
   The pi will not yet have access to the network, so some work remains.

10. Insert the MicroSD card to the Raspberry Pi Zero W and boot it up.
11. SSH into the Raspberry Pi with its IP (check the DHCP lease table on the router or similar...):
    ```bash
    $ ssh pi@<ip address>
    ```
    You will be asked if the certificate should be trusted. Answer yes.
    The password is `raspberry`.
12. Change the password to `aesir2020` (it doesn't matter if anybody knows this password, we're not supposed to run this Pi against the global internet) by running:

    ```bash
    $ passwd
    ```

13. Based off https://learn.adafruit.com/turning-your-raspberry-pi-zero-into-a-usb-gadget/ethernet-tweaks:

    1. Edit the file `/etc/network/interfaces`:

       ```bash
       $ sudo nano /etc/network/interfaces
       ```

       Add the following lines:

       ```
       source /etc/network/interfaces.d/default-usb
       ```

    1. Edit the file `/etc/network/interfaces.d/default-usb`:

       ```bash
       $ sudo nano /etc/network/interfaces.d/default-usb
       ```

       Add the following lines:

       ```
       auto usb0
       allow-hotplug usb0
       iface usb0 inet static
           metric 10
           address 192.168.137.2
           netmask 255.255.255.0
           network 192.168.137.0
           broadcast 192.168.137.255
           gateway 192.168.137.1
           dns-nameservers 8.8.8.8
       ```

       **Make sure that the above NEVER ends up in `/etc/network/interfaces`, as this will cause the DHCP server to never start.**

    1. Make it executable:

       ```bash
       $ sudo chmod 755 /etc/network/interfaces.d/default-usb
       ```

14. Make sure to assign the USB Gadget interface an ip `192.168.2.1` on your computer.
15. Reboot the pi: `sudo reboot 0`. Wait a bit and then reconnect over SSH.
16. Verify that you can ping google: `ping google.se`

From here on, the simplest method for automated installation is to run the `install.sh` over `ssh`:

```bash
ssh pi@raspberrypi.local < install.sh
```

This will run all the next steps automatically. It should be fine to run this file multiple times.

## Upgrade software

10. Update the software on the Pi (this might take a few minutes, so grab some drink):
    ```bash
    $ sudo apt-get update && sudo apt-get upgrade -y
    ```
11. Install `pip3`:
    ```bash
    $ sudo apt-get install python3-pip -y
    ```
12. Install `git`:
    ```bash
    $ sudo apt-get install git -y
    ```

## Installing InfluxDB

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

## Install Nginx

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

## Installing Python dependencies

```bash
$ pip3 install adafruit-circuitpython-busdevice
$ pip3 install adafruit-circuitpython-mcp3xxx
$ pip3 install influxdb
```

## Clone (or copy) dependencies

```bash
$ git clone https://github.com/aesirkth/water-test-rig
$ cd water-test-rig
```

# Nice to haves

Check the size of the Influx database:

```bash
$ sudo du -sh /var/lib/influxdb/data/watertestrig
92K     /var/lib/influxdb/data/watertestrig
```
