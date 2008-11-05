import ppgplot, plot_utils
import numpy as np
import datetime
import rating_utils

currdatetime = datetime.datetime.today()

# constants for text formating with PGPLOT
LINELENGTH = 65
LINESPACING = 0.025
PARASPACING = 0.05

# Plot settings
NUMPHASE = 2 # number of phases to plot

def plot_report(rating_objects, cand_ratings, descriptions):
    """
    'rating_objects' is a list of DatabaseRater objects.
    'cand_ratings' is a dictionary where for each entry the key 
	is a pdm_cand_id and the value is a list of ratings 
	(corresponding to 'rating_objects').
    'descriptions' is a dictionary where for each entry the key
	is a pdm_cand_id and the value is a description of the
	candidate.
    """
    plot_utils.beginplot("demo_rating_report%s.ps" % currdatetime.strftime('%y%m%d'), vertical=True)
    plot_report_coversheet(rating_objects)
    for (description,pdm_cand_id) in sorted([(n,i) for (i,n) in descriptions.items()]):
	plot_utils.nextpage(vertical=True)
	plot_candidate_sheet(rating_objects, pdm_cand_id, cand_ratings[pdm_cand_id], descriptions[pdm_cand_id])
    plot_utils.closeplot()

def plot_candidate_sheet(rating_objects, pdm_cand_id, cand_ratings, description):
    plot_utils.beginplot("cand_rating_report%s(%d).ps" % (currdatetime.strftime('%y%m%d'),pdm_cand_id), vertical=True)
    ppgplot.pgtext(0,1,"%d: %s" % (pdm_cand_id, description))
    top = 0.5
    first = True
    for ratobj, rating in zip(rating_objects,cand_ratings):
	if (top - PARASPACING) < 0:
	    if first:
		#
		# Add P, DM, subints, subbands?
		#
                pfd = rating_utils.get_pfd_by_cand_id(pdm_cand_id)
                prof = rating_utils.prep_profile(pfd)
                ppgplot.pgsvp(0.10, 0.90, 0.60, 0.90)
                ppgplot.pgswin(0, NUMPHASE, 1.1*np.min(prof), 1.1*np.max(prof))
                ppgplot.pgbox('BCNTS', 0.25,5,'BC',0.0,0)
		onephase = np.linspace(0,1,prof.size, endpoint=False)
		manyphase = np.resize(onephase,prof.size*NUMPHASE)+np.arange(0,NUMPHASE).repeat(prof.size)
                ppgplot.pgline(manyphase, np.resize(prof, (NUMPHASE*prof.size,)))
		first = False
	    plot_utils.nextpage(vertical=True)
	    ppgplot.pgtext(0,1,"%d: %s (cont'd)" % (pdm_cand_id, description))
	    top = 0.9
	ppgplot.pgtext(0,top, '%s: %s' % (ratobj.name, rating))
	top -= PARASPACING
    if first:
	pfd = rating_utils.get_pfd_by_cand_id(pdm_cand_id)
        prof = rating_utils.prep_profile(pfd)
        ppgplot.pgsvp(0.10, 0.90, 0.60, 0.90)
        ppgplot.pgswin(0, NUMPHASE, 1.1*np.min(prof), 1.1*np.max(prof))
        ppgplot.pgbox('BCNTS', 0.25,5,'BC',0.0,0)
        ppgplot.pgline(np.linspace(0,NUMPHASE,prof.size*NUMPHASE), np.resize(prof, (NUMPHASE*prof.size,)))

def plot_report_coversheet(rating_objects):
    """
    'rating_objects' is a list of DatabaseRater objects.
    """
    ppgplot.pgtext(0,1,"Demo Ratings Report (%s)" % currdatetime.strftime('%c'))

    top = 0.9
    for r in rating_objects:
	formatted_description = ' '.join([line.strip() for line in r.description.splitlines()])
	formatted_name = ("%s:" % r.name).ljust(LINELENGTH-1)
	text = ("%s %s" % (formatted_name, formatted_description))
	lines = []
	while text:
	    if len(text) > LINELENGTH:
		index = text.rfind(' ',0, LINELENGTH)
		lines.append(text[0:index])
		text = text[index+1:]
	    else:
		lines.append(text)
		text = ''
	if (top - len(lines)*LINESPACING) < 0:
	    # text will spill over bottom of page
	    plot_utils.nextpage(vertical=True)
	    ppgplot.pgtext(0,1,"Demo Ratings Report (%s) (cont'd)" % currdatetime.strftime('%c'))
	    top = 0.9
	for line in lines:
	    ppgplot.pgtext(0,top, line)
	    top -= LINESPACING
	top -= PARASPACING

def main():
    pass

if __name__=='__main__':
    main()
