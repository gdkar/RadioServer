#! /usr/bin/python

import RadioServer
import Listener
RS=RadioServer.RadioServer()
RS.addInputDeviceByName("right--line in",0)
RS.addInputDeviceByName("left--line in",1)
RS.addOutputDeviceByName("right--speaker",0)
RS.addOutputDeviceByName("left--speaker",1)

RS.start()
