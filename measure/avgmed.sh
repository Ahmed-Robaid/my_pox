#!/bin/sh
sort -n | awk '
  BEGIN {
    c = 0;
    sum = 0;
  }
  $1 ~ /^[0-9]*(\.[0-9]*)?$/ {
    a[c++] = $1;
    sum += $1;
  }
  END{
  ave = sum / c;
  std = (ave - sum)^2
  std = sqrt(std)
 std = sqrt(std/(NR-1))
 OFS="\t";
 print "samples = "c;
 print "average = "ave;
 print "min = " a[0];
 print "stand dev = "std;
 print "max = "a[c-1];
 
  }
  '
