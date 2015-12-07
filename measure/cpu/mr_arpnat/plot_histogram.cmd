set term pdf
set output "image.pdf"
# Make the x axis labels easier to read.
set xtics 
set  grid y

set yrange [0:25]
set ylabel "cpu consumption(%)"
set style data histogram
set style fill solid border -1
set boxwidth 0.9
set style histogram clustered 
plot for [COL=2:5] 'averages_linear.dat' using COL:xticlabels(1) title columnheader
