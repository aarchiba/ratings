import rating
import numpy as np


class SubbandRating(rating.DatabaseRater):
    def __init__(self, DBconn, name, version, description):
        rating.DatabaseRater.__init__(self,DBconn,name,version,description,with_files=True)

    def rate_candidate(self,hdr,candidate,pfd_file=None):
        pfd_file.dedisperse(pfd_file.bestdm)
        subbands = pfd_file.combine_profs(1,pfd_file.nsub)[0,:,:]
        return self.rate_profile(hdr,candidate,subbands)

    def rate_profile(self,hdr,candidate,subbands):
        raise NotImplementedError


class BroadbandednessRatingI(SubbandRating):
    def __init__(self, DBconn):
        SubbandRating.__init__(self, DBconn, name="Broadbandedness I", version=0, \
            description="Remove brightest 10% of subbands and compute "\
			"a new summed profile. Compare cross-correlation " \
			"of the new and old profiles with the " \
			"auto-correlation of the old profile.")

    def rate_profile(self,hdr,candidate,subbands):
	# scale subbands
	global_max = np.maximum.reduce(np.maximum.reduce(subbands))
	min_parts = np.minimum.reduce(subbands, axis=1)
	subbands = (subbands-min_parts[:,np.newaxis])/global_max
	
	nsubs, nbins = subbands.shape
	N = int(0.10*nsubs)
	max_parts = np.maximum.reduce(subbands, axis=1)
	sortind = np.argsort(max_parts)
	origprof = subbands.sum(axis=0)
	newprof = subbands[sortind][:-N].sum(axis=0)
	# Use slices, [:-1], because 1st and last points in cross/auto
	# correlations are the same
	cross = np.correlate(np.concatenate([origprof]*2), \
			     newprof, 'valid')[:-1]
	cross -= cross.min()
	cross /= cross.max()
	cross += 1
    
	auto = np.correlate(np.concatenate([origprof]*2), \
			    origprof, 'valid')[:-1]
	auto -= auto.min()
	auto /= auto.max()
	auto += 1
	return np.sqrt(np.sum((cross/auto-1)**2)/nbins)
	
class BroadbandednessRatingII(SubbandRating):
    def __init__(self, DBconn):
        SubbandRating.__init__(self, DBconn, name="Broadbandedness II", version=0, \
            description="Remove brightest 10% of subbands and compute "\
			"a new summed profile. Compare cross-correlation " \
			"of the new and old profiles with the " \
			"auto-correlation of the old profile.")

    def rate_profile(self,hdr,candidate,subbands):
	# scale subbands
	global_max = np.maximum.reduce(np.maximum.reduce(subbands))
	min_parts = np.minimum.reduce(subbands, axis=1)
	subbands = (subbands-min_parts[:,np.newaxis])/global_max
	
	nsubs, nbins = subbands.shape
	N = int(0.10*nsubs)
	max_parts = np.maximum.reduce(subbands, axis=1)
	sortind = np.argsort(max_parts)
	origprof = subbands.sum(axis=0)
	newprof = subbands[sortind][:-N].sum(axis=0)
	# Use slices, [:-1], because 1st and last points in cross/auto
	# correlations are the same
	cross = np.correlate(np.concatenate([origprof]*2), \
			     newprof, 'valid')[:-1]
	cross -= cross.min()
	cross /= cross.max()
	cross += 1
    
	auto = np.correlate(np.concatenate([origprof]*2), \
			    origprof, 'valid')[:-1]
	auto -= auto.min()
	auto /= auto.max()
	auto += 1
	return np.sqrt(np.sum((auto-cross)**2)/nbins)
