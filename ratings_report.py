import plot_utils
import rating_utils
import ppgplot
import datetime
import numpy as np

currdatetime = datetime.datetime.today()

NUMBINS = 1000 # number of histogram bins

"""
Generate a postscript document showing the results of ratings stored in the database.
"""

def get_all_rating_types():
    return rating_utils.get_data("SELECT * FROM rating_types;", dictcursor=True)
   
def get_ratings(rating_id, human_classification=None):
    """
    Return a numpy array of rating corresponding to 'rating_id' provided.
    'human_classification' is a list of human assigned classifications (from
    the default 8-level classification scheme) to include. If 'human_classifications'
    is None then all ratings will be returned.
    """
    if human_classification:
	pdm_class_type_id = rating_utils.get_default_pdm_class_type_id()
	ratings = rating_utils.get_data("SELECT r.value FROM ratings AS r LEFT JOIN pdm_classifications AS cl ON r.pdm_cand_id=cl.pdm_cand_id AND cl.pdm_class_type_id=%d WHERE r.rating_id=%d GROUP BY cl.pdm_cand_id HAVING sum(cl.rank IN (%s))/sum(cl.rank>0) > 0.5;" % (pdm_class_type_id, rating_id, ','.join([str(cl) for cl in human_classification])))
    else:
	ratings = rating_utils.get_data("SELECT value FROM ratings WHERE rating_id=%d" % rating_id)
    return np.array(ratings).squeeze()

def plot_rating_sheet(rating):
    """
    Plot a fact sheet on the ratings in the database corresponding to 'rating'.
    'rating' is a dictionary of information from the MySQL database (as returned
    by 'get_all_rating_types()'.
    """
    plot_utils.beginplot("rating_report%s.ps" % currdatetime.strftime('%y%m%d'), vertical=True)
    ch0 = ppgplot.pgqch()
    ppgplot.pgsch(0.5)
    ch = ppgplot.pgqch()
    ppgplot.pgsch(0.75)
    ppgplot.pgtext(0,1,"Rating Report for %s (%s) - page 1 of 2" % (rating["name"], currdatetime.strftime('%c')))
    ppgplot.pgsch(ch)
    
    # Plot Histograms
    
    all_ratings = get_ratings(rating["rating_id"]) 
    range = xmin,xmax = np.min(all_ratings), np.max(all_ratings)
    ppgplot.pgsci(1)
    ppgplot.pgslw(1)
    
    #===== Total/Classified/Unclassified
    # Get data
    ppgplot.pgsvp(0.1, 0.9, 0.75, 0.9)
    (tot_counts, tot_left_edges)=np.histogram(all_ratings, bins=NUMBINS, range=range)
    ppgplot.pgswin(xmin,xmax,0,np.max(tot_counts)*1.1)
    ppgplot.pgsch(0.5)
    ppgplot.pgbox("BCTS",0,5,"BCNTS",0,5)
    ppgplot.pgbin(tot_left_edges, tot_counts)
    (clsfd_counts, clsfd_left_edges)=np.histogram(get_ratings(rating["rating_id"], human_classification=(1,2,3,4,5,6,7)), bins=NUMBINS, range=range)
    ppgplot.pgsci(3) # plot classified in green
    ppgplot.pgbin(tot_left_edges, clsfd_counts)
    unclsfd_counts = tot_counts-clsfd_counts
    ppgplot.pgsci(2) # plot unclassified in red
    ppgplot.pgbin(tot_left_edges, unclsfd_counts)
    ppgplot.pgsci(1) # reset colour to black
    ppgplot.pgsch(0.75)
    ppgplot.pglab("","Counts","")

    #===== Class 1/2/3
    ppgplot.pgsvp(0.1, 0.9, 0.6, 0.75)
    (counts, left_edges)=np.histogram(get_ratings(rating["rating_id"], human_classification=(1,2,3)), bins=NUMBINS, range=range)
    ppgplot.pgswin(xmin,xmax,0,np.max(counts)*1.1)
    ppgplot.pgsch(0.5)
    ppgplot.pgbox("BCTS",0,5,"BCNTS",0,5)
    ppgplot.pgsci(1) # plot in black
    ppgplot.pgbin(tot_left_edges, counts)
    ppgplot.pgsci(1) # reset colour to black
    ppgplot.pgsch(0.75)
    ppgplot.pglab("","Class 1/2/3","")

    #===== RFI
    ppgplot.pgsvp(0.1, 0.9, 0.45, 0.6)
    rfi_ratings = get_ratings(rating["rating_id"], human_classification=(4,))
    (counts, left_edges)=np.histogram(rfi_ratings, bins=NUMBINS, range=range)
    ppgplot.pgswin(xmin,xmax,0,np.max(counts)*1.1)
    ppgplot.pgsch(0.5)
    ppgplot.pgbox("BCTS",0,5,"BCNTS",0,5)
    ppgplot.pgsci(1) # plot in black
    ppgplot.pgbin(tot_left_edges, counts)
    ppgplot.pgsci(1) # reset colour to black
    ppgplot.pgsch(0.75)
    ppgplot.pglab("","RFI","")

    #===== Noise
    ppgplot.pgsvp(0.1, 0.9, 0.3, 0.45)
    noise_ratings = get_ratings(rating["rating_id"], human_classification=(5,))
    (counts, left_edges)=np.histogram(noise_ratings, bins=NUMBINS, range=range)
    ppgplot.pgswin(xmin,xmax,0,np.max(counts)*1.1)
    ppgplot.pgsch(0.5)
    ppgplot.pgbox("BCTS",0,5,"BCNTS",0,5)
    ppgplot.pgsci(1) # plot in black
    ppgplot.pgbin(tot_left_edges, counts)
    ppgplot.pgsci(1) # reset colour to black
    ppgplot.pgsch(0.75)
    ppgplot.pglab("","Noise","")

    #===== Known/Harmonic
    ppgplot.pgsvp(0.1, 0.9, 0.15, 0.3)
    known_ratings = get_ratings(rating["rating_id"], human_classification=(6,7))
    (counts, left_edges)=np.histogram(known_ratings, bins=NUMBINS, range=range)
    ppgplot.pgswin(xmin,xmax,0,np.max(counts)*1.1)
    ppgplot.pgsch(0.5)
    ppgplot.pgbox("BCNTS",0,5,"BCNTS",0,5)
    ppgplot.pgsci(1) # plot in black
    ppgplot.pgbin(tot_left_edges, counts)
    ppgplot.pgsci(1) # reset colour to black
    ppgplot.pgsch(0.75)
    ppgplot.pglab(rating["name"],"Known/Harmonic","")

    #===== Second page for differential histograms
    plot_utils.nextpage(vertical=True)
    ppgplot.pgsch(0.75)
    ppgplot.pgtext(0,1,"Rating Report for %s (%s) - page 2 of 2" % (rating["name"], currdatetime.strftime('%c')))
    
    #===== RFI - Known
    ppgplot.pgsvp(0.1, 0.9, 0.75, 0.9)
    if rfi_ratings.size==0 or known_ratings.size==0:
        ppgplot.pgswin(0,1,0,1)
        ppgplot.pgbox("BC",0,0,"BC",0,0)
	ppgplot.pgsch(0.75)
        ppgplot.pglab("","RFI - Known","")
	ppgplot.pgsch(1.0)
	ppgplot.pgptxt(0.5, 0.5, 0.0, 0.5, "Not enough data")
    else:
        (known_counts, known_left_edges)=np.histogram(known_ratings, bins=NUMBINS, range=range, normed=True)
        (rfi_counts, rfi_left_edges)=np.histogram(rfi_ratings, bins=NUMBINS, range=range, normed=True)
        diff_counts = rfi_counts - known_counts
        ppgplot.pgswin(xmin,xmax,np.min(diff_counts)*1.1,np.max(diff_counts)*1.1)
	ppgplot.pgsch(0.5)
        ppgplot.pgbox("BCTS",0,5,"BCNTS",0,5)
        ppgplot.pgbin(tot_left_edges, diff_counts)
        ppgplot.pgsci(2) # set colour to red
        ppgplot.pgline(tot_left_edges, np.zeros_like(tot_left_edges))
        ppgplot.pgsci(1) # reset colour to black
	ppgplot.pgsch(0.75)
        ppgplot.pglab("","RFI - Known","")

    #===== RFI - Noise
    ppgplot.pgsvp(0.1, 0.9, 0.6, 0.75)
    if noise_ratings.size==0 or rfi_ratings.size==0:
        ppgplot.pgswin(0,1,0,1)
        ppgplot.pgbox("BC",0,0,"BC",0,0)
	ppgplot.pgsch(0.75)
        ppgplot.pglab("","RFI - Noise","")
	ppgplot.pgsch(1.0)
	ppgplot.pgptxt(0.5, 0.5, 0.0, 0.5, "Not enough data")
    else:
        (noise_counts, noise_left_edges)=np.histogram(noise_ratings, bins=NUMBINS, range=range, normed=True)
        (rfi_counts, rfi_left_edges)=np.histogram(rfi_ratings, bins=NUMBINS, range=range, normed=True)
        diff_counts = rfi_counts - noise_counts
        ppgplot.pgswin(xmin,xmax,np.min(diff_counts)*1.1,np.max(diff_counts)*1.1)
	ppgplot.pgsch(0.5)
        ppgplot.pgbox("BCTS",0,5,"BCNTS",0,5)
        ppgplot.pgbin(tot_left_edges, diff_counts)
        ppgplot.pgsci(2) # set colour to red
        ppgplot.pgline(tot_left_edges, np.zeros_like(tot_left_edges))
        ppgplot.pgsci(1) # reset colour to black
	ppgplot.pgsch(0.75)
        ppgplot.pglab("","RFI - Noise","")

    #===== Known - Noise
    ppgplot.pgsvp(0.1, 0.9, 0.45, 0.6)
    if noise_ratings.size==0 or known_ratings.size==0:
        ppgplot.pgswin(0,1,0,1)
        ppgplot.pgbox("BC",0,0,"BC",0,0)
	# Y-axis label is taken care of outside of if/else (below)
	ppgplot.pgsch(1.0)
	ppgplot.pgptxt(0.5, 0.5, 0.0, 0.5, "Not enough data")
    else:
        (noise_counts, noise_left_edges)=np.histogram(noise_ratings, bins=NUMBINS, range=range, normed=True)
        (known_counts, known_left_edges)=np.histogram(known_ratings, bins=NUMBINS, range=range, normed=True)
        diff_counts = known_counts - noise_counts
        ppgplot.pgswin(xmin,xmax,np.min(diff_counts)*1.1,np.max(diff_counts)*1.1)
	ppgplot.pgsch(0.5)
        ppgplot.pgbox("BCNTS",0,5,"BCNTS",0,5)
        ppgplot.pgbin(tot_left_edges, diff_counts)
        ppgplot.pgsci(2) # set colour to red
        ppgplot.pgline(tot_left_edges, np.zeros_like(tot_left_edges))
        ppgplot.pgsci(1) # reset colour to black
    ppgplot.pgswin(xmin,xmax,0,1)
    ppgplot.pgsch(0.5)
    ppgplot.pgbox("NTS",0,5,"",0,0)
    ppgplot.pgsch(0.75)
    ppgplot.pglab(rating["name"],"Known - Noise","")
    
    ppgplot.pgsch(ch0) # reset character height

def plot_rating_report():
    rating_types = get_all_rating_types()
    plot_utils.beginplot("rating_report%s.ps" % currdatetime.strftime('%y%m%d'), vertical=True)
    first = True
    for rating in rating_types:
	if first:
	    first = False
	else:
	    plot_utils.nextpage(vertical=True)
	plot_rating_sheet(rating)
	
    plot_utils.closeplot()
    
def main():
    plot_rating_report()
    
if __name__=='__main__':
    main()
