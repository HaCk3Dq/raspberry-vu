Spectrumyzer
==============

[![prev](https://i.ytimg.com/vi/nsqza-5bOK8/maxresdefault.jpg)](http://www.youtube.com/watch?v=nsqza-5bOK8)
(click on the preview to watch demo)

Dependencies
--------------

Make sure you have `git` and the full `gcc` stack installed, and then install the following packages: 

```
python
cairo
python-cairo
python-gobject
fftw
libpulse
```

Ubuntu/Linux Mint

```
apt-get install libpulse-dev python3-dev libfftw3-dev
```

Build
--------------

    git clone https://github.com/HaCk3Dq/spectrumyzer.git
    make

Note:
Locate `Python.h` and change path to `python3.6m` in Makefile if you need

If this completes successfully, test with:

    ./spectrumyzer.py

And try to play some music

References
--------------
* https://github.com/rm-hull/raspberry-vu

* https://github.com/ianhalpern/Impulse
