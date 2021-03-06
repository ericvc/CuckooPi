CuckooPi: A Data-Driven Cuckoo Clock for the Raspberry Pi (v 1.0.0)
================

The CuckooPi project is an effort to create a data-driven digital cuckoo
clock using information obtained through various APIs. First, it uses
reports of bird sightings in your local area (data from
[eBird](https://ebird.org/home)) to determine which bird species to
display. Once selected, audio recordings of that species’ songs and/or
calls are downloaded from the publically accessible
[xeno-canto](https://www.xeno-canto.org/) database while photographs are
obtained from [Flickr](https://www.flickr.com/services/api/). Audio
recordings and photographs are played each hour, on the hour, and
provide a surprising and educational reminder of what time it is. These
files can also be replayed at any time within the hour using the RasPi
GPIO. There is also an option to display a secondary screen showing a
brief description of the bird species as described on
[AllAboutBirds.org](www.allaboutbirds.org)

The CuckooPi clock is a great way to familiarize yourself with the bird
species in your area. Because CuckooPi uses recent bird identification
records (within the last two weeks by default), the species you will see
on the clock are constantly changing along with birds’ seasonal
migration patterns. The clock is also configured to display species at
the correct time of the day. Nocturnal taxa such as owls and nightjars
will only appear before sunrise and after sunset (apologies to the
northern hawk owl and other exceptional species that defy this scheme).
Additionally, all photos are captioned with the species’ common name
(e.g., song sparrow) and scientific (binomial) name (*Melospiza
melodia*).

## Installation (Raspberry Pi OS)

All code was written for and tested on a Raspberry Pi 3B v1.2. More
information about the system can be found in the file `system.txt`.

### Program Dependencies and Files

Before installation, I highly recommend registering for eBird and Flickr
accounts (if necessary) to obtain the API credentials needed to access
these databases (xeno-canto is public). Eventually, you will need to
edit the file `example_api_keys.json` to include this information and
rename the file `api_keys.json`.

First, copy the code in this GitHub repository to your local machine
(assuming you already have git installed):

    git clone https://github.com/ericvc/CuckooPi /home/your-path-here

In the `config/` sub-directory, there is a bash script `setup.sh` that
can be run to automate the installation of system and Python
dependencies that are needed by the program. Most of the former are for
editing and encoding media files.

You may wish to edit the installation script in order to customize
directory path settings. To do so, simply edit the first few lines of
the file to set your script variables:

    PROJDIR="Projects"  # Projects Directory
    PROJNAME="CuckooPi"  # Project Name
    HOMEDIR="/home/pi"  # Home Directory

To run the installation script, open a terminal window in the project
directory and run the follwing:

    sudo bash config/setup.sh

If you choose instead to manually install software dependencies, the
following code will be
useful.

``` 
#################################################################################
# Install Python Libraries
#################################################################################

# Install all over libraries with pip
pip3 install -r home/pi/Projects/CuckooPi/requirements.txt"


#################################################################################
# Install xscreensaver for screen management
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
sudo bash "home/pi/Projects/CuckooPi/config/ffmpeg_install.sh"
pip install ffmpeg-normalize

# Feh
sudo apt-get install -y feh

```

### Starting CuckooPi

The installation script will create a program icon on the desktop.
Clicking this icon will launch the program. No other steps are required.

If instead you would like for the program to run automatically at
startup, I have included the file `cuckoopi.service` which can be used
to launch the CuckooPi as a service (daemon). The file contents are:

    [Unit]
    Description=CuckooPi Clock
    After=network.target
    
    [Service]
    ExecStart=/usr/bin/python3 -u cuckoo.py
    WorkingDirectory=/home/pi/Projects/CuckooPi
    StandardOutput=inherit
    StandardError=inherit
    Restart=always
    User=pi
    
    [Install]
    WantedBy=multi-user.target

To configure this service to run at startup, run the following in a
terminal
window:

``` 
sudo cp /home/pi/Projects/CuckooPi/config/cuckoopi.service /etc/systemd/system/cuckoopi.service
sudo systemctl enable cuckoopi.service  # Run at startup 
sudo systemctl start cuckoopi.service  # Start service now 
```

### Other Configuation Options

My favorite thing about CuckooPi is the ability to keep tabs on bird
species that are moving through my area, thanks to eBird’s API and the
observations reported by local bird watching enthusiasts. By default,
this program will attempt to determine your approximate location from
your IP address and will use the maximum allowable search radius to
collect observations records. However, this feature is not likely to be
useful if you are using a VPN.

For best performance, I highly recommend setting your latitude/longitude
coordinate location manually by editing `cuckoo.py` and adjusting the
following options (line 92):

    # options
    lat = 38.00  # 2 decimal limit
    lon = -121.00  # 2 decimal limit
    search_radius = 20  # kilometers
    back = 7  # how many days back to search
    
    
    ebird = eBirdQuery(EBIRD_API_KEY, latitude=lat, longitude=lon, back=back, search_radius=search_radius)

I adjusted my settings to include only observations from the last 7 days
and limited the search radius to 20 km (12.4 mi). I have not yet
encountered any problems locating recent observations with these
settings, but your experience will strongly depend on the efforts of
birders in your area. If you have trouble finding records, first try
expanding the search radius before setting the location to a nearby area
with a more active birding scene.

The CuckooPi uses two tactile push buttons that allow the user to replay
the bird photo and audio recording of the hour as well as show a brief
description of that species. On my system, I have these button connected
to board pins 7 and 8 (GPIO 4 and 14). These settings can be changed or
removed by editing the main program script `cuckoo.py`.

CuckooPi’s screen management relies on the `xscreensaver` program. Once
installed, I recommend configuring your screensaver settings (from the
start menu) to display only a blank screen when activated. The
screensaver you select will be displayed the majority of the time.

My configuration also uses a 16x2 LCD to display the current date and
time. Code for running the LCD display is included in this repo, but
first, you must enable I2C on your RasPi. From the terminal run as root:

    sudo raspi-config

and navigate the menu to the interface options and enable I2C
connections.

## Future Directions

I am excited to build upon this software and create a housing to
complete the clock. A few ideas I am planning on, but have not committed
to, include:

  - Equip the RasPi with a 3.5" LCD screen for visual displays. Also
    considering 7" touch screen options with integrated audio.
  - Dedicated speakers, currently weighing different options based on
    the size/quality tradeoff and how they will be connected (HDMI,
    bluetooth, on-board, etc.)
  - Considering either repurposing a birdhouse or building something out
    of Legos. The latter is a good option because it would make mounting
    the electronic components much easier.

Check back soon for more updates on how the build ended up working out.
