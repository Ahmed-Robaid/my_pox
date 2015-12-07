set term png
set output "linear_time.png"
set xlabel "host #"
set xtics ("h10" 10, "h20" 20, "h30" 30, "h40" 40, "h50" 50, "h60" 60 )
set ylabel "time(ms)"
set xrange [2:30]
set style line 1 lt rgb "blue" lw 2 pt 6
set style line 5 lt rgb "red" lw 2 pt 6
set style line 2 lt rgb "violet" lw 2 pt 6
set style line 3 lt rgb "green" lw 2 pt 6
plot "time_l2.dat" title 'l2_learning' with linespoint ls 1, \
     "tine_arpnat.dat" title 'l2_learning + arpnat' with linespoint ls 2,\
     "time_responder.dat" title 'l2_learning + arpnat' with linespoint ls 3,\
     "time_arprespsafe.dat" title 'l2_learning + arpnat' with linespoint ls 5
