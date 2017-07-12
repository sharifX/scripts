#!/usr/bin/python
import os 
import sys 
print len(sys.argv) 
if len (sys.argv) != 3 :
    print "Usage: python "+sys.argv[0] + " <hdl server address> <PID>"
    sys.exit (1)
def main(): 
 c = pycurl.Curl()
 hdlserver = str(sys.argv[1]) 
 pid       = str(sys.argv[2]) 
 # construct the curl command 
 curlcmd = "curl http://"+hdlserver+"/api/handles/"+pid+"?pretty"
 print curlcmd 
 #c.setopt (c.URL,curlcmd)
 os.system(curlcmd)
if __name__ == '__main__':
  main()
