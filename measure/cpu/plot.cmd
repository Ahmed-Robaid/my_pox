set term png
set output "l2learn_arpnat.png"
set xlabel "time(sleep=5ms)"
set xrange[5:200]
set yrange[0:80]
set ylabel "cpu usage (%)"
plot "cpu_mr_l2.dat" using 1:2 title 'l2_learning' with linespoint ls 1, \
     "cpu_mr_arp.dat" using 1:2 title 'l2_learning+arpnat' with linespoint ls 3

