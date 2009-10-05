#! /usr/bin/env python
#disablegss.py 
#  
#  Copyright (c) 2006 crazy___cow@hotmail.com
# 
#  This program is free software; you can redistribute it and/or 
#  modify it under the terms of the GNU General Public License as 
#  published by the Free Software Foundation; either version 2 of the
#  License, or (at your option) any later version.
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
#  USA


 
import dbus
import dbus.glib
import sys
import os
import subprocess
import string
import time
import pynotify

from stat import *

CONF_FILE = ".disablegss"

def disable_sleep(myprogram): 
  try:
    bus = dbus.Bus(dbus.Bus.TYPE_SESSION)
    devobj = bus.get_object('org.gnome.ScreenSaver',  '/org/gnome/ScreenSaver')
    dev = dbus.Interface(devobj, "org.gnome.ScreenSaver")
    cookie = dev.Inhibit(myprogram, 'Disabled by DisableGSS Daemon')
    emit_notification("Gnome screensaver stopped.")
    return dev, cookie
  except Exception, e:
    print "DisableGSS: could not send the dbus Inhibit signal: %s" % e
    #sys.exit(0) 
    return False, False


def allow_sleep(dev, cookie):
  try:
    dev.UnInhibit(cookie)
    emit_notification("Gnome screensaver enabled.")
    return (True)
  except Exception, e:
    print "DisableGSS: could not send the dbus UnInhibit signal: %s" % e
    #sys.exit(0)
    return (False)

#This function takes Bash commands and returns them
def runBash(cmd):
  p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
  out = p.stdout.read().strip()
  return out  #This is the stdout from the shell command

def list_commands():
  f = runBash('ps -eo comm=')
  f = f.splitlines()
  return f

def read_config( config_file ):
  __psaux = []
  try:
    f = open(config_file , 'r')
    __psaux = f.readlines()
    __psaux = [x.rstrip('\n') for x in __psaux]
    f.close();
    print "DisableGSS: config file read."
    return __psaux
  except IOError:
    print "DisableGSS: config file ~/.disablegss doesn't exist! Write it by hand. Add applications name that could disable gnome screensaver: one app name for every line of file."
    sys.exit(0)

def emit_notification( message ):
  n = pynotify.Notification('DisableGSS', message)
  if not n.show():
    print message

def main():
  homedir = os.getenv('HOME')
  config_file = os.path.join( homedir, CONF_FILE )
  condition = True
  disabled = False
  old_program = ""
  applist = []
  last_last_time_modified = ""
  last_time_modified = ""
  
  applist = read_config( config_file )
  last_time_modified = os.stat( config_file )[ST_MTIME]
  last_last_time_modified = last_time_modified

  if not pynotify.init("DisableGSS"):
    print "Couldn't start notifier"

  while condition:
    found = False
    commands = list_commands()

    for program in applist:
      if program in commands:
        found = True
        if program != old_program:
          print "DisableGSS: there is a program (" + program + ") in the config list that is currently running."
          old_program = program
        if disabled == False:
          dev, cookie = disable_sleep(program)
          disabled = True
          break
        
    if found == False and disabled == True:
      print "DisableGSS: there are no more programs that could stop gnome screensaver."
      allow_sleep( dev, cookie)
      disabled = False

    time.sleep(60)
    last_time_modified = os.stat( config_file )[ST_MTIME]
    if last_time_modified != last_last_time_modified:
      print "DisableGSS: config file modified."  
      applist = read_config( config_file )
      last_time_modified = os.stat( config_file )[ST_MTIME]
      last_last_time_modified=last_time_modified

    old_program = ""
    #condition=False

if __name__ == '__main__':
  main()
