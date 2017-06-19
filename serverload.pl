#!/usr/bin/perl
# Server Load Monitoring 
 
# This grabs top pid, system, mem information
# grabs information from apache status 
# does a ps -A, then looks at lsof for related httpd pid
  
 
use strict; 
use Linux::SysInfo qw/sysinfo/;
# http://search.cpan.org/~vpit/Linux-SysInfo-0.11/lib/Linux/SysInfo.pm
 
# grab the sysinfo
my $si = sysinfo;
 
 
# email setup
my $from='<FROM_ADDRESS>';
my $to='<TO_ADDRESS>'; 
my $subject='<SERVER_NAME>: LOAD ALERT' ;
 
# get all PS, sort reverse and get some of the output 
# because we are only interested in the process that is 
# hogging up CPU and MEM 
 
my @psa = `ps --no-headers -A -o \"%mem %cpu ucomm pid\"|sort -r|head -n4`;
 
 open(PS_A, "ps --no-headers -A -o \"%mem %cpu ucomm pid\"|sort -r|head -n4|");
  
 
 # apache status page: 
  my @status = `elinks http://myserver/server-status | awk \' /ID\$/ { print; exit } { print }\'`;
 
 my $tstamp  = time;
  
 my @lsof ;
 
# If the minute average load is more than 4.00 then 
# send the email 
   if (  $si->{'load1'} > 5.00 ) 
  {
 
 open (MAIL, "|/usr/sbin/sendmail -t -oi");
 print MAIL "FROM: $from\n";
 print MAIL "TO: $to\n";
 print MAIL "Reply-to: $from \n";
 print MAIL "Subject: $subject\n\n";
 print MAIL "$_: $si->{$_}\n" for keys %$si;
 print MAIL "\n *************  TOP PIDs *********** \n@psa\n ************* \n"; 
 print MAIL "\nApache server status: http:\/\/myserver\/server-status\n---------\n"; 
 print MAIL "=============\n@status\n============\n"; 
 print MAIL "\n------------%mem %cpu command pid--------------\n" ;
 
 my $lsof_filename = "lsof.out".$tstamp ; 
  
 # loop through the PS -A output 
  while (<PS_A>) {
 
     print MAIL $_; 
   my ($mem, $cpu, $comm, $pid) = split;
# get list of open files for all these top PID
  
   my $cmd = "lsof|grep $pid|grep httpd"; 
 
 my @content = `/usr/sbin/lsof|grep $pid|grep httpd` ; 
 #print @content; 
    
 
# write the output in a file 
 
  # open(LSOF, ">>$lsof_filename"); #open for write, append
  # print LSOF  "\n$cmd\n----------------\n@lsof\n---------------\n";  
  # close(LSOF);
 
 print MAIL  "\n$cmd\n----------------\n@content\n---------------\n";  
 
   }
 
close (PS_A); 
close(MAIL);
 }  
