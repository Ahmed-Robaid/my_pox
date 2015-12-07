set term pdf
set output "tree_time_sarp.pdf"
set xlabel "host #"
set xtics ("h10" 10, "h20" 20, "h30" 30, "h40" 40, "h50" 50, "h60" 60 )
set ylabel "time(ms)"
set xrange [2:64]
set yrange [0:300]
set key left
set key font ",11"
set linestyle 5 lt rgb "black" lw 2
set key box linestyle 5
set style line 1 lt rgb "blue" lw 2 pt 6
set style line 5 lt rgb "red" lw 2 pt 2
set style line 2 lt rgb "violet" lw 2 pt 5
set style line 3 lt rgb "green" lw 2 pt 9
plot "tree_l2.dat" using 1:2 title 'legacy' with linespoint ls 1, \
     "tree_sarp.dat" using 1:2 title 's_arp' with linespoint ls 2,\
     "tree_arpresp.dat" using 1:2 title 'arp_responder' with linespoint ls 3,\
     "tree_sarp_resp.dat" using 1:2 title 's_arp + arp_responder' with linespoint ls 5
