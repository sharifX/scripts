#!/usr/bin/python 
import commands,sys
status, output = commands.getstatusoutput("/etc/init.d/globus-gridftp-server status")
if status != 0:
   print "CRITICAL - globus-gridftp-server is not running" 
   sys.exit(2) 
else: 
   print "OK - globus-gridftp-server is running" 
   sys.exit(0) 
