#!/bin/bash
set -e  # Exit immediately if a pipeline returns a non-zero status
set -x  # Print a trace of simple commands.

# Make sure internet is enabled via `lxd init`.
# 
# Use the following settings:
#
# Would you like to use LXD clustering? (yes/no) [default=no]:
# Do you want to configure a new storage pool? (yes/no) [default=yes]: no
# Would you like to connect to a MAAS server? (yes/no) [default=no]:
# Would you like to create a new local network bridge? (yes/no) [default=yes]: yes
# What should the new bridge be called? [default=lxdbr0]:
# What IPv4 address should be used? (CIDR subnet notation, “auto” or “none”) [default=auto]:
# What IPv6 address should be used? (CIDR subnet notation, “auto” or “none”) [default=auto]:
# Would you like LXD to be available over the network? (yes/no) [default=no]: yes
# Address to bind LXD to (not including port) [default=all]:
# Port to bind LXD to [default=8443]:
# Trust password for new clients:
# Again:
# No password set, client certificates will have to be manually trusted.Would you like stale cached images to be updated automatically? (yes/no) [default=yes]
# Would you like a YAML "lxd init" preseed to be printed? (yes/no) [default=no]:

# images:archlinux does not have internet connection out-of-the-box so we're using ubuntu for now.
# If archlinux was working, it would make installing the latest versions of packages much easier.
echo "Downloading Ubuntu image..."
lxc image copy images:ubuntu/disco local: --alias ubuntu

echo "Launching Linux container..."
lxc launch ubuntu lovelace-build

# I think this is needed because if I immediately start apt installing, the internet connection
# is still not up and running.
echo "Sleeping for 30 seconds until image fully spins up..."
sleep 30

# Ubuntu disco dingo already comes with Python 3.7.3 so no need to install Python.
echo "Installing Python packages..."
lxc exec lovelace-build -- sudo apt update
lxc exec lovelace-build -- sudo apt install -y python3-pip
lxc exec lovelace-build -- sudo pip3 install numpy scipy bitstring

echo "Installing Julia..."
lxc exec lovelace-build -- sudo apt install -y wget
lxc exec lovelace-build -- wget https://julialang-s3.julialang.org/bin/linux/x64/1.1/julia-1.1.0-linux-x86_64.tar.gz
lxc exec lovelace-build -- tar xvf julia-1.1.0-linux-x86_64.tar.gz
lxc exec lovelace-build -- mv ~/julia-1.1.0 ~/julia && echo 'PATH=$PATH:~/julia/bin' >> ~/.bashrc && source ~/.bashrc

echo "Installing latest version of node.js..."
# lxc exec lovelace-build -- sudo apt install -y curl software-properties-common
# lxc exec lovelace-build -- curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
lxc exec lovelace-build -- sudo apt install -y nodejs

echo "Installing gcc..."
lxc exec lovelace-build -- sudo apt install -y gcc

echo "python3 --version"
lxc exec lovelace-build -- python3 --version
echo "node --version"
lxc exec lovelace-build -- node --version
echo "julia --version"
lxc exec lovelace-build -- julia --version
echo "cc --version"
lxc exec lovelace-build -- cc --version

echo "Publishing lovelace-image..."
lxc publish lovelace-build --force --alias lovelace-image

echo "Stopping lovelace-build container..."
lxc delete --force lovelace-build
