# Setting up the test rig

1. **MAKE SURE THE TEST RIG IS NOT POWERED. UNPLUG ANY USB CABLES.**
1. Connect the sensors to the test rig. **DO NOT DO THIS IF THE RIG IS POWERED**
1. Connect a sufficiently powerful USB charger (at least 2A) to the PWR USB input.
1. Wait a few minutes.
1. Connect to the `watertestriggobrr` Wi-Fi network with the password `aesir2020`.
1. Open the URL `http://192.168.4.1` in your browser.
1. Wait some more minutes. Everything is quite slow to start up.
1. Profit

# Packing the test rig

1. **DO NOT DISCONNECT SENSORS WHILE THE RIG IS POWERED**
1. Unpower the test rig by disconnected the **USB cables**.
1. Wait a few seconds.
1. Unplug the sensors.

# Updating the test rig

**This section may contain errors. Follow at your own risk and patience :)**

First of all, make sure that your computer **is not connected to the test rig over Wi-Fi**. Also make sure that your computer has a working internet connection.

When the rig is powered (**according to the steps listed in _Setting up the test rig_**), connect with a USB cable from your computer to the `USB` port on the Raspberry Pi.

Depending on your OS, the next steps are a bit different, but you now need to enable network sharing with the RPI (Raspberry Pi).
It is already set up to enable ethernet over USB if your OS supports it.

For Windows, this guide could work: https://pixel.red/guide/sharing-internet-raspberry-pi-via-usb/

Some other ways to make it work can be found at this link, but you **do not need to do anything on the actual RPI**: https://learn.adafruit.com/turning-your-raspberry-pi-zero-into-a-usb-gadget/ethernet-tweaks

Make sure that your computer supports Bonjour: https://learn.adafruit.com/bonjour-zeroconf-networking-for-windows-and-linux/

If the sharing is set up correctly, it should now be possible to SSH into the pi:

```bash
$ ssh pi@raspberrypi.local
```

The password is `aesir2020`.

Make sure that the RPI can connect to the internet:

```bash
$ ping -c 5 google.se
```

You should just by SSH'ing have ended up in the `/home/pi` directory. Go to the `/home/pi/water-test-rig/` directory:

```bash
$ cd /home/pi/water-test-rig/
```

From there, you should be able to pull the latest changes and simply run the `install.sh` script:

```bash
$ git pull && bash install.sh skip-install
```
