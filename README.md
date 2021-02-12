<h1>Below is the track of the RPI barebones build instructions</h1>

<p>Modify sudo nano /boot/config.txt as per Archive directory</p>
<p>Modify sudo nano /boot/cmdline.txt and add 'quiet'</p>

<h2>Remove extra stuff</h2>
<ul>
	<li>  sudo systemctl disable dphys-swapfile.service</li>
	<li>  sudo systemctl disable keyboard-setup.service</li>
	<li>  sudo systemctl disable apt-daily.service</li>
	<li>  sudo systemctl disable wifi-country.service</li>
	<li>  sudo systemctl disable hciuart.service</li>
	<li>  sudo systemctl disable raspi-config.service</li>
	<li>  sudo systemctl disable avahi-daemon.service</li>
	<li>  sudo systemctl disable triggerhappy.service</li>
</ul>

<h2>Install packages</h2>
<ul>
	<li>sudo apt-get update</li>
	<li>sudo apt-get upgrade -y</li>
	<li>sudo apt-get install python3 python3-dev python-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsdl1.2-dev</li>
	<li>sudo apt-get install libsmpeg-dev python3-numpy python-numpy subversion libportmidi-dev libfreetype6-dev python3-pip</li>
	<li>sudo apt-get install python3-rpi.gpio python-pygame python3-sdl2 python-pygame can-utils git</li>
</ul>

<h2> Now setup the GIT stuff</h2>
mkdir ~/.ssh</br>
cd ~/.ssh</br>
ssh-keygen -t rsa -C "tim@russellweb.eu"</br>
cat ~/.ssh/id_rsa.pub</br>
	<< Add to git >></br>
mkdir ~/python</br>
cd ~/python</br>
git config --global user.email "{EMAIL}"</br>
git config --global user.name "{NAME}"</br>
git init</br>
git pull git@github.com:timr1972/dashboard.git</br>
</br>
<h2>and don't forget to modify /etc/network/interfaces</h2>
<ul>
	<li>auto can0</li>
	<li>iface can0 inet manual</li>
	<li>    pre-up ip link set $IFACE type can bitrate 100000 listen-only off</li>
	<li>    up /sbin/ifconfig $IFACE up</li>
	<li>    down /sbin/ifconfig $IFACE down</li>
</ul>
