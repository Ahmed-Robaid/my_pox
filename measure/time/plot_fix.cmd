set term png
set output "ping_tim_fix.png"
set xlabel "host"
set xtics ("h5" 5, "h10" 10, "h15" 15, "h20" 20, "h25" 25, "h30" 30 )
set ylabel "time(ms)"
set xrange [2:30]
set style line 1 lt rgb "blue" lw 2 pt 6
set style line 5 lt rgb "red" lw 2 pt 6
plot "averages_fixed.dat" using 1:2 title 'l2_learning' with linespoint ls 1, \
     "averages_fixed.dat" using 1:3 title 'l2_learning + arpnat' with linespoint ls 2 
