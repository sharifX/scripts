#!/usr/bin/perl -w 
# reading enchanced MARC file 

use strict;
use MARC::File::USMARC;


my $filename="file.mrc"; 

# create a new marc objec to read the  file 

my $file = MARC::File::USMARC->in( $filename );
my $issn; 
# read the marc file with all the MARC records 
    while ( my $marc = $file->next() ) {
        

  #print $marc->as_formatted, "\n\n" ;
  
  if ($marc->field('700'))  { 
   $issn =   $marc->field('700')->subfield("a");
   } 
  my $url;
  if($marc->field('856')) {
  $url   = $marc->field('856')->subfield("u");
  }

if ($sub2) { 

   $title = "$title: $sub2" ; 
  } 
else 
 { 

   $title = $title; 
 
}  
 
 print "$title\t$isbn\t$url\t$author\n";
 #print "$title\n";


}   
   $file->close();
    undef $file;
