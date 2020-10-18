CuckooPi: A Data-Driven Cuckoo Clock for Raspberry Pi
================

The CuckooPi project is an effort to create a data-driven digital Cuckoo
clock using information obtained through various APIs. It uses reports
of bird sightings in your local area (data from
[eBird](https://ebird.org/home)) to determine which bird species to
display. Once selected, sound recordings of that species’ song and calls
are collected from the publically accessible
[xeno-canto](https://www.xeno-canto.org/) database and photographs
obtained from Flickr. These recordings and photographs are played each
hour, on the hour, and provide a suprising and educational reminder of
what time it is. There is also an option to replay the media files at
any time using the RasPi GPIO.

The CuckooPi clock is a great way to familiarize yourself with the birds
in your area. Because the CuckooPi uses recent bird identification
records (within the last two weeks by default), the species you will see
on the clock are constantly in flux. The clock is also configured to
display species at the correct time of the day. Nocturnal taxa like owls
and nightjars will only appear after sunset (apologies to the northern
hawk owl and other exceptional species that defy this scheme).

All photos are captioned with the common name (e.g., song sparrow) and
scientific name (*Melospiza meloida*)

## Installation (Raspberry Pi OS)

All code was written and test for a Raspberry Pi 3B v1.2. More
information about the system can be found in the file `system.txt`.

### Program Dependencies and Files

Before installation, I highly recommend first registering for eBird and
Flickr accounts (if necessary) to obtain the API credentials needed to
access these databases (xeno-canto is public). Eventually, you will need
to edit the file `example_api_keys.json` to include this information.

First, copy the code in this GitHub repository to your local machine,
assuming you have git installed.

    git clone https://github.com/ericvc/CuckooPi /home/your-path-here

In the `config/` subdirectory, there is a bash script `setup.sh` that
can be run to automate the installation of system and Python
dependencies that are needed for the program to run. Most of the former
are for editing and encoding media files.

You may wish to edit the installation script to customize directory path
settings. To do so, simply edit the first few lines of the file to set
your script variables, which will be used throughout the script.

    PROJDIR="Projects"  # Projects Directory
    PROJNAME="CuckooPi"  # Project Name
    HOMEDIR="/home/pi"  # Home Directory

To run the installation script, open a terminal window in the project
directory and run the follwing:

    sudo bash setup.sh

The installation script will create a program icon on the desktop.
Clicking this icon will launch the program. No other steps are required.

If you would like for the program to run automatically at startup, I
have included the file `cuckoopi.service` which can be used to launch
the CuckooPi as a service. The file contents are:

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

To configure this service to run at startup, run the
following:

``` 
sudo cp /home/pi/Projects/CuckooPi/config/cuckoopi.service /etc/systemd/system/cuckoopi.service
sudo systemctl enable cuckoopi.service  # Run at startup 
sudo systemctl start cuckoopi.service  # Enable now 
```

### Other Configuation Options

The CuckooPi uses a single tactile push button that allows the user to
playback the bird photo and audio recording of the hour. On my system, I
have this button connected to board pin 8 (GPIO 14). These settings can
be changed or removed by editing the main program script `cuckoo.py`.

CuckooPi’s screen management relies on the Xscreensaver. Once installed,
I highly recommend configuring your screensaver to display only a blank
screen when activated. Whichever screensaver you select will be
displayed the majority of the time.

## Future Directions

I am excited to build upon this software and create a housing to
complete the clock. A few ideas I am planning on, but have not committed
to, include:

  - Equip the RasPi with a 3.5" LCD screen for visual displays. Also
    considering 7" touch screen options.
  - Dedicated speakers, currently weighing different options based on
    the size/quality tradeoff
  - A 16x2 I2C LCD will be dedicated to displaying the current date and
    time
  - Housing options: considering either repurposing a birdhouse or
    building something out of Legos. The latter is a good option because
    it would make mounting the electronic components much easier.
