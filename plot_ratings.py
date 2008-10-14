import pylab
import numpy as np

import rating
import harmonic_rating
import pfd_ratings

class RatingPlotter(rating.DatabaseWalker):
    def __init__(self,DBconn):
        rating.DatabaseWalker.__init__(self,DBconn,with_files=False)

        self.candidates = {}

        self.unclassified = set()

        self.classified_real = set()
        self.classified_maybe = set()
        self.classified_RFI = set()
        self.classified_notreal = set()
        self.classified_known = set()

        self.rated_harmonic = set()
        self.rated_ratio = set()

        self.HarmonicRating = harmonic_rating.HarmonicRating(DBconn)
        self.RatioRating = pfd_ratings.RatioRating(DBconn)


    def act_on_candidate(self,hdr,candidate,pfd_file=None):
        id = candidate["pdm_cand_id"]
        self.candidates[id] = candidate

        if self.HarmonicRating.value(candidate)>0.5:
            self.rated_harmonic.add(id)
        if self.RatioRating.value(candidate)>1.5:
            self.rated_ratio.add(id)

        r = rating.manual_classification(self.DBconn,candidate)
        if r in (1,2):
            self.classified_real.add(id)
        elif r==3:
            self.classified_maybe.add(id)
        elif r==4:
            self.classified_RFI.add(id)
        elif r==5:
            self.classified_notreal.add(id)
        elif r in (6,7):
            self.classified_known.add(id)
        else:
            self.unclassified.add(id)


    def plot_p_vs_sigma(self):
        pylab.figure()
        pylab.xlabel("P (s)")
        pylab.ylabel("sigma")
        self.plot("period","presto_sigma")
        pylab.gca().set_xscale("log")
        pylab.xlim(1e-4,10)
        pylab.legend(loc="best")
    def plot_p_vs_DM(self):
        pylab.figure()
        pylab.xlabel("P (s)")
        pylab.ylabel("DM")
        self.plot("period","dm")
        pylab.gca().set_xscale("log")
        pylab.ylim(0,1000)
        pylab.xlim(1e-4,10)
        pylab.legend(loc="best")


    def plot(self,xaxis,yaxis):
        def p(s,sz,color,label=""):
            x,y = zip(*[(c[xaxis],c[yaxis]) for c in [self.candidates[id] for id in s]])
            print "%s: %d points" % (label, len(s))
            pylab.scatter(x,y,sz,color=color,edgecolor=color,facecolor=color,label=label)
        rated = self.rated_harmonic.union(self.rated_ratio)
        p(self.unclassified.difference(rated),1,"gray","unclassified")
        p(self.classified_notreal.difference(rated),1,"black","not real")
        p(self.classified_RFI.difference(rated),1,"red","RFI")
        p(self.rated_harmonic,1,"yellow","60 Hz")
        p(self.rated_ratio,1,"orange","stronger at DM 0")
        p(self.classified_maybe,1,"green","maybe")
        p(self.classified_real,2,"green","likely")
        p(self.classified_known,2,"blue","known")



if __name__=='__main__':
    rp = RatingPlotter(rating.usual_database())
    rp.run()
    rp.plot_p_vs_DM()
    rp.plot_p_vs_sigma()
    pylab.show()
