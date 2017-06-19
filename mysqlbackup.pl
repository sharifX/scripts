#!/usr/bin/perl
 
# Do a mysql dump for backup purposes.
# Added directory grep, so we back up 
# all the database. Don't have to edit the list 
# when a new database is created 
# Added a trim function for the directory 
# name 
 
use strict ; 
 
my ($cmd, $rv, $cmd1, $cmd2, $rv1, $rv2) ; 
my ($account, $password) ; 
our ($BU_DIR) ; 
my ($db, @dbs_to_backup) ; 
 
$account  = "root" ;
$password = "<password>" ;
$BU_DIR = "/root/sql-backup" ; # Where the backups are placed. 
 
#Delete SQL backups older than 7 days
$cmd2 = "find /mysql/sql-backup/ -ctime +7 -exec rm -f {} \\;" ; 

$rv2 = `cmd2` ;
 
#get the databse name from the directory
$cmd1 = "ls -F /mysql/mysql/ |grep '\/'" ;
@dbs_to_backup = `$cmd1`;
 
#replace the ending '/'
foreach $db (@dbs_to_backup)
    { $db =~ s/\///g ; 
      $db = trim($db); 
    }


 
foreach $db (@dbs_to_backup)
{
  print "Backing up $db...\n" ; 
  make_backup($db, $account, $password) ; 
}
 
 
print "Done.\n" ;
exit 0 ; 
 
# Backup and compress. 
sub make_backup
{
 
  my ($dbname, $account, $password) ;
  my ($cmd, $rv) ; 
  my ($cur_time, $bu_filename) ; 
 
 
  ($dbname, $account, $password) = @_ ; 
  
  # Get the current perl time
  $cur_time = time() ; 
 
  # Make file backup filename 
  $bu_filename = $BU_DIR . "/" . $dbname . ".sql-" . $cur_time ; 
 
  # Do the backup. 
  $cmd = "mysqldump --opt $dbname --user=$account --password=$password"
     . "> $bu_filename " ; 
  print $cmd; 
  $rv = `$cmd` ; 
  print $rv . "\n" ; 
 
  # Compress the file.
  #$cmd = "gzip --best $bu_filename" ; 
  #$rv = `$cmd` ; 
 
}
 
 sub trim {
   my($string)=@_;
   for ($string) {
       s/^\s+//;
       s/\s+$//;
   }
   return $string;
   }
