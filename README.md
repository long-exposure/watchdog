# Watchdog

Building supervision with Raspberry Pi

(C)2017 - Norbert Huffschmid

Watchdog is licensed under GPLv3.

## Hardware prerequisites

* Raspberry Pi
* SD card >= 4 GB
* RaspiCam

## Installation

Download the latest Raspian Jessie Lite image and write it to your SD-card as
described [here](http://www.raspbian.org/).

Power-on your Raspberry with keyboard, mouse and monitor connected.

Invoke raspi-config for the initial settings. Configure the correct keyboard layout, timezone and locale settings. Enable the camera, enable the SSH server, expand the filesystem on your SD-card, change the default password of user pi and finally reboot.

Probably you want your Raspberry Pi to be WLAN-enabled. There are different ways to achieve this, the most simple one is this:

Edit this configuration file:

`$ sudo nano /etc/wpa_supplicant/wpa_supplicant.conf`

Add or edit the following lines (take care of the quotes!):
```
network={
ssid="Your WLAN name"
psk="Your secret WLAN password"
key_mgmt=WPA-PSK
}
```
Update your Raspberry Pi to the latest software:
```
$ sudo apt-get update
$ sudo apt-get upgrade
```
Finally install the watchdog software from github:
```
$ sudo apt-get install git
$ git clone git://github.com/long-exposure/watchdog.git
$ cd watchdog
$ chmod +x install
$ sudo ./install
```
The installation takes some time. Drink a cup of coffee and be patient until the success message appears on the console.

## Configuration

All remaining configuration is done via a web interface:

    http://<IP address of your Raspberry Pi>/

The admin interface is password protected. You have to enter your standard login credentials (e.g. pi/raspberry).
