#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A wallpaper a day, keep the doctor away.

Usage:
  bing set [-d DIRECTORY] [-s] [-r] [--xfce4-path XFCE4_PATH] ENVIRONMENT
  bing story
  bing -V | --version
  bing -h | --help

Arguments:
  ENVIRONMENT                your desktop environment. Currently we support
                             gnome, gnome2, cinnamon, xfce4, mate.
                             If your desktop isn't listed, try "pywal" or "feh"

Options:
  -h, --help                 show the help info and exit
  -V, --version              show the version and exit
  -d, --directory=DIRECTORY  specify where to save the download picture
                             [default: /tmp]
  --xfce4-path=XFCE4_PATH    specify the image path for the relevant monitor
                             [default: /backdrop/screen0/monitor0/image-path]
  -s, --save-story           save the picture story alongside the image
  -r, --reapply              reapply the wallpaper if it has already been downloaded
"""

from __future__ import absolute_import, unicode_literals, print_function

import re
import time
import sys
from os import path
import subprocess

import requests
from docopt import docopt

from wonderful_bing import __version__


class Bing(object):
    def __init__(self):
        # Get all the information we need from this url, see issue#7
        self.url = ("https://www.bing.com/HPImageArchive.aspx?format=js"
                    "&idx=0&n=1&nc=1409879295618&pid=hp")
        self.response = requests.get(self.url).json()

    @property
    def picture_story(self):
        story_content = self.response['images'][0]['copyright']
        return story_content

    @property
    def picture_url(self):
        picture_url = self.response['images'][0]['url']
        if not picture_url.startswith('http'):
            picture_url = 'https://www.bing.com' + picture_url
        return picture_url

    @property
    def picture_name(self):
        match = re.search("\?id\=OHR\.(\w+)\_.+", self.picture_url)
        picture_name = match.group(1) + '.jpg'
        return picture_name


class Computer(object):
    def __init__(self):
        # We use this command to make it work when using cron, see #3
        self.command_table = {
            ("DISPLAY=:0 GSETTINGS_BACKEND=dconf "
             "/usr/bin/gsettings set org.gnome.desktop.background "
             "picture-uri file://{0}"): ['gnome', 'gnome2', 'cinnamon'],
            ("DISPLAY=:0 GSETTINGS_BACKEND=dconf "
             "/usr/bin/gsettings set org.mate.background "
             "picture-filename '{0}'"): ['mate'],
            ("DISPLAY=:0 xfconf-query -c xfce4-desktop "
             "-p {1} -s {0}"): ['xfce4'],
            ("wal -i '{0}'"): ["wal", "pywal"],
            ("feh --bg-scale '{0}'"): ["feh"],
        }

    def _get_command(self, environment):
        """Get the command for setting the wallpaper according to the
        desktop environtment, return None if we don't support it yet.

        :param environment: the desktop environment.
        """
        if environment in sum(self.command_table.values(), []):
            return [item[0] for item in self.command_table.items()
                    if environment in item[1]][0]

    def set_wallpaper(self, environment, picture_path, xfce4_path):
        """Set the given picture as wallpaper.

        :param environment: the desktop environment.
        :param picture_path: the absolute picture location.
        """
        command = self._get_command(environment)
        if not command:
            sys.exit(
                ("Currently we don't support your desktop_environment: {0}\n"
                 "Please file an issue or make a pull request :) \n"
                 "https://github.com/lord63/wonderful_bing").format(
                     environment))
        status = subprocess.Popen(command.format(picture_path, xfce4_path),
                                  shell=True)
        status.wait()
        if status.returncode == 0:
            print("Successfully set the picture as the wallpaper. :)")
        else:  # pragma: no cover
            print("Something bad happened, fail to set as wallpaper :(")

    def show_notify(self, content):
        """Show the notify to get to know the picture story.

        :param content: the picture story.
        """
        title = "Today's Picture Story"
        notify_icon = path.join(path.dirname(path.realpath(__file__)),
                                'img/icon.png')
        safe_content = content.replace('"', '\"')
        subprocess.Popen(["notify-send", "-a", "wonderful_bing", "-i",
                          notify_icon, title, safe_content])


class WonderfulBing(object):
    def __init__(self, arguments):
        self.environment = arguments['ENVIRONMENT']
        self.xfce4_path = arguments['--xfce4-path']
        self.directory = path.abspath(arguments['--directory'])
        self.bing = Bing()
        self.picture_path = path.join(self.directory, self.bing.picture_name)
        self.save_story = arguments['--save-story']
        self.picture_story_path = path.join(
            self.directory,
            path.splitext(self.picture_path)[0] + ".txt",
        )
        self.reapply = arguments["--reapply"]

    def download_picture(self):
        if path.exists(self.picture_path):
            print("You have downloaded the picture before.")
            print("Have a look at it --> {0}".format(self.picture_path))
            if self.reapply:
                self.apply_wallpaper()
            sys.exit()
        # Sleep for two seconds, otherwise the newly setted wallpaper
        # will be setted back by the system when your system boots up
        # if you have added this script to autostart.
        time.sleep(2)
        # Set stream to true to get the raw content
        request = requests.get(self.bing.picture_url, stream=True)
        with open(self.picture_path, "wb") as f:
            for chunk in request.iter_content(1024):
                f.write(chunk)
        print("Successfully download the picture to --> {0}.".format(
              self.picture_path))
        
        if self.save_story:
            # Save the story to a txt file alongside the picture
            with open(self.picture_story_path, "w") as f:
                f.write(self.bing.picture_story)
            print("Successfully saved the picture story to --> {0}.".format(
                self.picture_story_path))

    def rock(self):
        """Download the picture, set as wallpaper, show the notify."""
        self.download_picture()
        self.apply_wallpaper()
    
    def apply_wallpaper(self):
        computer = Computer()
        computer.set_wallpaper(self.environment, self.picture_path,
                               self.xfce4_path)
        computer.show_notify(self.bing.picture_story)


def main():
    arguments = docopt(__doc__, version=__version__)
    if not path.exists(arguments['--directory']):
        sys.exit('No such directory :(')

    try:
        wonderful_bing = WonderfulBing(arguments)
        if arguments['story']:
            print(wonderful_bing.bing.picture_story)
        else:
            wonderful_bing.rock()
    except requests.exceptions.ConnectionError:
        print("ConnectionError,check your network please.")
        print("Will try again after 5 minutes.")
        time.sleep(300)
        wonderful_bing.rock()


if __name__ == '__main__':  # pragma: no cover
    main()
