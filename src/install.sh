#!/usr/bin/env bash
sudo apt-get update
# common
apt install  python3-pip apt-transport-https  autoconf automake build-essential git libtool python3-dev unzip libfuzzy-dev  libmagic-dev python3-tlsh net-tools
# backend
apt install  libpq-dev libssl-dev  libjpeg-dev mongodb   binutils file openssl  bison flex npm
apt install  cmake libicu-dev zlib1g-dev yasm libgmp-dev libpcap-dev pkg-config libbz2-dev nvidia-opencl-dev ocl-icd-opencl-dev opencl-headers clamav clamav-daemon clamdscan
apt install shellcheck luarocks lua5.3 liblua5.3-dev xvfb nginx libffi-dev ca-certificates curl software-properties-common docker-compose docker.io
python3 -m pip install -i https://mirrors.aliyun.com/pypi/simple/ --upgrade pip
python3 -m pip install  -i https://mirrors.aliyun.com/pypi/simple/ --upgrade setuptools
pip3 install -i https://mirrors.aliyun.com/pypi/simple/   -r requirements.txt
pip3 install -i https://mirrors.aliyun.com/pypi/simple/  ssdeep
bash install/pre_install.sh &&  mkdir /media/data &&  chown -R $USER /media/data


### 后端
#linter
npm install -g jshint

# yara
unzip v3.7.1.zip
cd yara-3.7.1
./bootstrap.sh
./configure --enable-magic && make -j$(nproc) && make install
cd ..
rm -rf v3.7.1.zip

#oms
systemctl stop clamav-freshclam.service
sudo -E freshclam

#FS_META
#bash plugins/analysis/file_system_metadata/install_docker.sh

# INPUT VECTORS
#bash plugins/analysis/input_vectors/install_docker.sh

#cve
#python3 plugins/analysis/cve_lookup/internal/setup_repository.py

# software_components
bash plugins/analysis/software_components/install.sh

# user_password plugins
cd plugins/analysis/users_and_passwords/bin/john
tar xf 1.9.0-Jumbo-1.tar.gz --strip-components 1
rm 1.9.0-Jumbo-1.tar.gz
cd src/
./configure -disable-openmp && make -s clean && make -sj4
cd /root/FACT_core/src/plugins/analysis/users_and_passwords/internal
python3 update_password_list.py
luarocks install luafilesystem
luarocks install argparse
luarocks install luacheck

# binwalk
cd plugins/analysis/binwalk/binwalk
python3 setup.py build
sudo -EH python3 setup.py install
#cd /root/FACT_core/src
#bash plugins/analysis/binwalk/install.sh
#rm -rf plugins/analysis/binwalk/binwalk
