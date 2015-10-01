set term png
set output "l2learn_arpnat.png"
set yrange [2.5:10.5]
set xlabel "time"
set ylabel "cpu usage (%)"
plot "forw.dat" using 1:2 title 'l2_learning' with lines, \
     "forw_arpnat.dat" using 1:2 title 'l2_learning+arpnat' with lines

