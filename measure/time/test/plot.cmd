set term png
set output "ping_time.png"
set xlabel "# of hosts"
set ylabel "time(ms)"
set style line 1 lt rgb "blue" lw 2 pt 6
set style line 5 lt rgb "red" lw 2 pt 6
plot "averages.dat" using 1:2 title 'l2_learning' with linespoint ls 1, \
     "averages.dat" using 1:3 title 'l2_learning + arpnat' with linespoint ls 5   
