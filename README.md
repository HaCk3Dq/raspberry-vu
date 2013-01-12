Impulse / Raspberry Ladder VU Meter
===================================
Modified from Ian Halpern's screenlet, this version is specifically hacked to 
run on a Raspberry Pi, with a Raspberry ladder (http://www.tandyonline.co.uk/raspberry-ladder-kit.html),
the idea being that the LED's bounce in time to the currently streaming audio.


![Rasberry Ladder](https://raw.github.com/rm-hull/raspberry-vu/master/raspberry-ladder.png)

To quote the original project's README:

> "Impulse is a bit of eye-candy for your desktop. It is a widget that displays
a graphical spectrum analyzer on your gnome desktop. It is written in c and
python and uses GTK and cairo graphics to generate the animation. The impulse
library creates a pulse audio connection context that reads the output stream
from pulseaudio in a thread natively which can then be read from python. You
can specify impulse to either output the raw stream or output the fft of the
raw stream."

This hack eshews the cairo graphics and screenlets frippery, and interfaces to 
the Raspberry Ladder via the GPIO, and uses the UNIX curses library to present
a crude spectum analyser.

See a demonstration of it in action at https://vimeo.com/56822701.

Pre-requisites
--------------
1. Make sure you have git and the full gcc stack installed, and then install the 
   following packages: `sudo apt-get install python-dev libfftw3-dev libpulse-dev`

2. Make sure that the Raspberry Ladder is fully working according to the
   instructions on pp10-11 of http://issuu.com/themagpi/docs/the_magpi_issue_7?mode=window,
   and that the wiringPI `gpio` command has been build and installed properly.

3. Compile and install the wiringPi python bindings from https://github.com/rm-hull/wiringPi

Building & Testing
------------------
Build the C code and python bindings:

    make clean all

If this completes successfully, `tree build` should look something like:

    build
    └── armv6l
        ├── impulse
        │   ├── COPYING
        │   ├── impulse.py
        │   ├── impulse.so
        │   └── README.md
        └── test
            └── test-impulse

    3 directories, 5 files

If this completes successfully, test with:

    cd build/armv6l/test/
    ./test-impulse

This should stream zeros up the screen; then start pulseaudio and your favourite
 media player (in another window):

    pulseaudio --daemonize
    mplayer K.Minogue-I_should_be_so_lucky.mp3

Those zero's from the test program should be replaced with some changing values
as the media plays.

Running the VU Meter
--------------------
Since the access to the GPIO is via `/dev/mem`and this is protected, we must
run pulseaudio and mplayer with elevated `sudo` permissions.

Hence, in one terminal session:

    sudo pulseaudio

In anothe terminal:

    sudo mplayer K.Minogue-I_should_be_so_lucky.mp3

Then in another terminal:

    cd ~/rasberry-vu/build/armv6l/impulse/
    sudo ./impulse.py

If all goes as expected, you should see the Raspberry ladder LED's bouncing
(as well as the on-screen spectrum analyser) in time to the music playing. 
Pressing any key will exit the app.

Troubleshooting
---------------
Tested working with Rev B 512Mb Rasberry Pi (Raspbian "Wheezy" & latest 
[RPi-Firmware](https://github.com/Hexxeh/rpi-update))

* If Pulseaudio doesn't seem to be working properly:

    - do not run pulseaudio in system mode

    - make sure the user is added to the _audio_ and _pulse-access_ groups: 
      `sudo usermod -aG audio,pulse-access pi` - and then restart pulseaudio.

    - start pulseaudio in debug mode: `pulseaudio --log-level=debug` instead 
      of daemonized and scutinize the logs for any obvious errors.

* If the make command fails, check to ensure you have all the build tools installed properly.

TODO
----
* Work out how to get it working without `sudo` privileges.

References
----------
* http://raspberrypi.stackexchange.com/questions/639/how-to-get-pulseaudio-running

* http://raspberrypi.stackexchange.com/questions/1621/no-sound-output-in-vlc

* https://projects.drogon.net/the-raspberry-ladder-board/

* http://www.tandyonline.co.uk/raspberry-ladder-kit.html

* http://issuu.com/themagpi/docs/the_magpi_issue_7?mode=window

* https://github.com/Hexxeh/rpi-update
