#!/bin/bash

#################################################################################
# ============================================================================= #
# |---------------------------------CuckooPi----------------------------------| #
# |            A Data-Driven Digital Cuckoo Clock for Raspberry Pi            | #
# |                                                                           | #
# |                    Raspberry Pi Configuration Script                      | #
# |                                                                           | #
# |                                10.13.2020                                 | #
# |---------------------------------------------------------------------------| #
# ============================================================================= #
#################################################################################

# To execute this setup script, run the following from a terminal window in the
# same directory as this file: bash setup.sh
#
# Make sure you have configured your internet connection before running!


#################################################################################
# Script Variables (edit for custom configuration)
#################################################################################

PROJDIR="Projects"  # Projects Directory
PROJNAME="CuckooPi" #  Project Name
HOMEDIR="/home/pi/" #  Home Directory


#################################################################################
# Install system updates if available
#################################################################################

sudo apt-get update
sudo apt-get upgrade


#################################################################################
# Create project directories
#################################################################################

# Main directory
mkdir "${HOMEDIR}/${PROJDIR}/${PROJNAME}"

# Media file storage directory
mkdir "${HOMEDIR}/${PROJDIR}/${PROJNAME}/cache"


#################################################################################
# Install Git Software for Version Control
#################################################################################

# Install
sudo apt install -y git

# Configure
git config --global user.name "your.username"
git config --global user.email "your.email@mail.com"

# Check configuration
git config --list


#################################################################################
# Install Required Python Libraries
#################################################################################

# Install all over libraries with pip
pip3 install -r "${HOMEDIR}/${PROJDIR}/${PROJNAME}/requirements.txt"


#################################################################################
# Install xcreensaver for screen management
#################################################################################

sudo apt install -y xscreensaver


#################################################################################
# Install libraries for media file encoding and editing
#################################################################################

# LAME
sudo apt-get install -y libmp3lame-dev
sudo apt-get install -y lame

# sox
sudo apt-get install -y sox
sudo apt-get install -y libsox-fmt-mp3

# FFmpeg (may take some time to download and compile)
sudo bash "${HOMEDIR}/${PROJDIR}/${PROJNAME}/config/ffmpeg_install.sh"

# Feh
sudo apt-get install -y feh


#################################################################################
# Install CuckooPi
#################################################################################

# Clone project repository to local storage
git clone https://github.com/ericvc/CuckooPi "${HOMEDIR}/${PROJDIR}/${PROJNAME}"

# Add shortcut to desktop
sudo cp "${HOMEDIR}/${PROJDIR}/${PROJNAME}/config/cuckoopi.desktop" "${HOMEDIR}/Desktop/cuckoopi.desktop"


#################################################################################
# End of script.
#################################################################################
