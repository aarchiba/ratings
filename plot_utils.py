import ppgplot

def beginplot(fn, vertical=False):
    """
    Set up a colour ps plot with filename fn for letter-size paper.

    Default is to orient paper horizontally (landscape). If vertical
    is True then the paper will be oriented vertically.
    """
    if ppgplot.pgqid()!=0:
	# ppgplot already has a device open
	
	# 
	# QUESTION: Should raise error here?
	#
	pass
    else:
	# Setup
	ppgplot.pgbeg("%s/CPS" % fn, 1, 1)
	if vertical:
	    ppgplot.pgpap(7.9, 11.0/8.5)
	else:
	    ppgplot.pgpap(10.25, 8.5/11.0)
	ppgplot.pgiden()

def nextpage(vertical=False):
    """
    Start a new page in the currently opened device.
    Default is to orient paper horizontally (landscape). If vertical
    is True then the paper will be oriented vertically.
    """
    # New page
    if ppgplot.pgqid()!=0:
        ppgplot.pgpage()
	ppgplot.pgswin(0,1,0,1)
	if vertical:
	    ppgplot.pgpap(7.9, 11.0/8.5)
	else:
	    ppgplot.pgpap(10.25, 8.5/11.0)
        ppgplot.pgiden()
    else:
        sys.stderr.write("Cannot start new page. No pgplot device open.\n")
        raise "No open pgplot device"

def closeplot():
    """
    closeplot()

    Close the currenly opened device, finalizing the plot.
    """
    # Close plot
    if ppgplot.pgqid()!=0:
        ppgplot.pgclos()
    else:
        sys.stderr.write("Cannot close plot. No pgplot device open.\n")
        raise "No open pgplot device"

def histogram(x, data, horizontal=True):
    """
    plot a histogram of data. The bins' left edges
    are given in x
    """

    bin_coords = x.repeat(2)
    data_coords = numpy.concatenate(([0], data.repeat(2), [0]))

    if horizontal:
        ppgplot.pgline(bin_coords, data_coords)
    else:
        ppgplot.pgline(data_coords, bin_coords)

