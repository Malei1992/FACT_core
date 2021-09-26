#!/usr/bin/env bash

# cd in this files directory for relative paths to work
cd "$( dirname "${BASH_SOURCE[0]}" )"

FACTUSER=$(whoami)

CODENAME=$(lsb_release -cs)
if [ "${CODENAME}" = "ulyana" ]; then
    CODENAME=focal
elif [ "${CODENAME}" = "tara" ] || [ "${CODENAME}" = "tessa" ] || [ "${CODENAME}" = "tina" ]; then
    CODENAME=bionic
elif [ "${CODENAME}" = "rebecca" ] || [ "${CODENAME}" = "rafaela" ] || [ "${CODENAME}" = "rosa" ]; then
    CODENAME=trusty
    sudo apt-get -y install "linux-image-extra-$(uname -r)" linux-image-extra-virtual
elif  [ "${CODENAME}" = "kali-rolling" ]; then
    CODENAME=buster
elif [ -z "${CODENAME}" ]; then
	echo "Could not get Ubuntu codename. Please make sure that lsb-release is installed."
	exit 1
fi

echo "Install Pre-Install Requirements"
#sudo apt-get -y install python3-pip git libffi-dev

# Install packages to allow apt to use a repository over HTTPS
#sudo apt-get -y install apt-transport-https ca-certificates curl software-properties-common

echo "Installing Docker"

sudo systemctl enable docker

# add fact-user to docker group
if [ ! "$(getent group docker)" ]
then
    sudo groupadd docker
fi
sudo usermod -aG docker "$FACTUSER"

if pip3 freeze 2>/dev/null | grep -q enum34
then
  echo "Please uninstall the enum34 pypi package before continuing as it is not compatible with python >3.6 anymore"
  exit 1
fi

#sudo -EH pip3 install --upgrade pip

#sudo -EH pip install -r ./requirements_pre_install.txt

echo -e "Pre-Install-Routine complete! \\033[31mPlease reboot before running install.py\\033[0m"

exit 0
