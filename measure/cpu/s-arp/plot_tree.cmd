set term png
set output "tree.png"
set xlabel "time(sleep=2ms)"
set key font ",12"
set linestyle 5 lt rgb "black" lw 2
set key box linestyle 5
set xrange[0:200]
set yrange[0:40]
set ylabel "cpu usage (%)"
plot "cpu_treel2.dat" using 1:2 title 'l2_learning' with linespoint ls 1, \
     "cpu_tree_sarp.dat" using 1:2 title 's_arp' with linespoint ls 2,\
     "cpu_treearpresonder.dat" using 1:2 title 'l2_learning+arp_responder' with linespoint ls 3,\
     "cpu_tree_sarp_responder.dat" using 1:2 title 's_arp +arp_responder' with linespoint ls 4

