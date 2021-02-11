Below is the track of the RPI barebones build instructions
.
.
.
.

Modify sudo nano /boot/config.txt as per Archive directory
Modify sudo nano /boot/cmdline.txt and add 'quiet'

Remove extra stuff
  sudo systemctl disable dphys-swapfile.service
  sudo systemctl disable keyboard-setup.service
  sudo systemctl disable apt-daily.service
  sudo systemctl disable wifi-country.service
  sudo systemctl disable hciuart.service
  sudo systemctl disable raspi-config.service
  sudo systemctl disable avahi-daemon.service
  sudo systemctl disable triggerhappy.service

sudo apt-get update
sudo apt-get upgrade -y

sudo apt-get install python3 python3-dev python-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsdl1.2-dev 
sudo apt-get install libsmpeg-dev python3-numpy python-numpy subversion libportmidi-dev libfreetype6-dev python3-pip 
sudo apt-get install python3-rpi.gpio python-pygame python3-sdl2 python-pygame can-utils git

mkdir ~/.ssh
cd ~/.ssh
ssh-keygen -t rsa -C "tim@russellweb.eu"
cat ~/.ssh/id_rsa.pub
	<< Add to git >>
mkdir ~/python
cd ~/python
git init
git pull git@github.com:timr1972/dashboard.git

and don't forget to modify /etc/network/interfaces
auto can0
iface can0 inet manual
    pre-up ip link set $IFACE type can bitrate 100000 listen-only off
    up /sbin/ifconfig $IFACE up
    down /sbin/ifconfig $IFACE down
