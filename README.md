# Watchdog
![Watchdog Logo](/www/watchdog-logo-64-64.png)

Building supervision with Raspberry Pi

(C)2017 - Norbert Huffschmid

License: GPLv3

## What is it?

Watchdog is a camera supervision solution for the Raspberry Pi. It is based on [motion detection](http://www.lavrsen.dk/foswiki/bin/view/Motion/WebHome) and currently provides these notification/storage options:

* Telegram messenger
* Dropbox
* Email
* FTP

With watchdog you get notified on your smartphone as soon as some motion has been detected in your home.

## How is it used?

Before you leave your home, you have to power-on the Raspberry Pi. After the startup procedure is complete, which will last approximately half a minute, every detected movement within the camera area will trigger an alarm. Notifications are delayed for 30 seconds, i.e. when you return home, again you have half a minute to power-off the Raspberry Pi.

If a burglar finds your watchdog and destroys it, most probably it already has sent a notification and uploaded the taken captures.

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
$ LATESTTAG=$(git describe --tags)
$ git checkout $LATESTTAG
$ chmod +x install
$ sudo ./install
```
The installation takes some time. Drink a cup of coffee and be patient until the success message appears on the console.

## Configuration

All remaining configuration is done via a web interface:

    http://<IP address of your Raspberry Pi>/

The admin interface is password protected. You have to enter your standard login credentials (e.g. pi/raspberry). The web admin gui hopefully is self-explaining.
Per default all features (plugins) are active. On the settings tab you can deactivate all plugins you don't need.

### Telegram

As Telegram user you can receive all capture images immediately on your smartphone. To make this work, you have to establish a telegram bot on the Raspberry Pi, which is rather easy and explained on the web admin gui. Telegram messages are sent to subscribed users and groups only. Users and groups have to chat with the created bot on the Raspberry Pi and send a /subscribe command. You have to acknowledge the subscribe request on the web gui before it has any effect. Subscribed users can also send a /photo command and immediately receive a live picture taken by the camera.

### Dropbox

With a dropbox account, you can automatically upload all captures to it. This is a pure storage feature.

### FTP

Alternatively you can upload all captures to some FTP server. This is a pure storage feature too.

### Email

It depends on your email account, if you can use (push) email for immediate alarm notifications. In the web admin gui you can choose, whether capture images should be sent as attachments or not. Alternatively you can send just small text emails and upload capture images to dropbox or some FTP server.

## Security

Be aware that monitoring systems like watchdog can be directed against you! Keep your Raspberry Pi secure! Change the default password! If a bad guy takes access on your Pi and its camera, he can observe you and your environment!

Run your Raspberry Pi behind a router and do NOT administer some port forwarding in order to access it from outside your local network. You have been warned!

## Disclaimer

This software is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

Good luck, stay safe!
