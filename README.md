# Wonderful_Bing

[![Latest Version][1]][2]
[![Build Status][3]][4]
![Platform][5]
[![Coverage Status][7]][8]

## Intro

Tired of the wallpaper? Let's make the change. This program is to download
Bing's picture and set as wallpaper with a notify to let you know the story
behind the picture.

## Requirements

* Linux platform(Currently support gnome and xfce)
* Python 2.7
* Requests lib
* Docopt lib
* Libnotify-bin(for Arch: libnotify)

## Install

    $ sudo pip install wonderful_bing
    $ sudo apt-get install libnotify-bin

## Usage

Use `bing --help` to get the detailed information.

* Manually

You need to set a directory(default `/tmp`)to save the download pictures,
end with '/', specify your desktop_environment(support gnome, cinnamon, xfce4).

    $ bing set -d /path/to/save/pictures/ desktop_environment

* Automatically(recommand)

1. Add it to `startup application`(in my Linux Mint16) if you power on your pc
   and power off your pc regularly, then every time you boot up your pc, this
   script will automatically run for you.

2. Or use `cron`. Let me give you an example:

        0 8 * * * env DISPLAY=:0 /usr/local/bin/bing set -d /home/lord63/pictures/bing/ cinnamon

   *we need `env DISPLAY=:0`, otherwise the notify can't display at all, and remember
   the `/` at the end.*

3. Or use `anacron` if you ofen hang up your pc instead of powering off it.
   but the original `anacron` will run the script in root, thus it may fail in setting the 
   picture to wallpaper. Follow [this][6] to let you run `anacron` as normal user. 
   Let me give you an example, add the following line in `$HOME/.anacron/anacrontab`:

        1 1 bing env DISPLAY=:0 /usr/local/bin/bing set -d /home/lord63/pictures/bing/ cinnamon

If you find a better way, please let me know :)

## Snapshots

the first time you run it:

    $ bing set -d /home/lord63/pictures/bing/ cinnamon
    Successfully download the picture to --> /home/lord63/pictures/bing/CascadePools.jpg
    Successfully set the picture as the wallpaper. :)

get today's picture story.

    $ bing story
    美国蒙大拿州的白鱼市，正在吃花楸浆果的太平鸟 (© Chuck Haney/Alamy)

if the picture has been downloaded before:

    $ bing set -d /home/lord63/pictures/bing/ cinnamon
    You have downloaded the picture before.
    Have a look at it --> /home/lord63/pictures/bing/CascadePools.jpg

if your pc doesn't connect to the network, it will try again after 5 mins.

    $ bing set -d /home/lord63/pictures/bing/ cinnamon
    ConnectionError,check your network please.
    Will try again after 5 minutes.

and the notify should looks like this:

![](./wonderful_bing/img/notify.png)

## License

MIT License


[1]: http://img.shields.io/pypi/v/wonderful_bing.svg
[2]: https://pypi.python.org/pypi/wonderful_bing
[3]: https://travis-ci.org/lord63/wonderful_bing.svg
[4]: https://travis-ci.org/lord63/wonderful_bing
[5]: http://img.shields.io/badge/Platform-Linux-blue.svg
[6]: http://www.wellengang.ch/?p=135
[7]: https://img.shields.io/coveralls/lord63/wonderful_bing.svg
[8]: https://coveralls.io/r/lord63/wonderful_bing
