import config as c
import demo_report
import sys

if c.survey == "PALFA":
    # PALFA pdm_cand_ids
    pdm_cand_ids = {
        284989: "Known pulsar, narrow peak (J1900+06)",
        283739: "Known pulsar, two peaks (J1850+0026)",
        591295: "Known pulsar, fainter, with burst of RFI",
        184508: "Known pulsar, very strong (B1915+13)",
        197463: "Known pulsar (J1921+0812)",
        663819: "New MSP, 2.15 ms",
        157246: "Noise, 3.21 ms",
        434756: "Known MSP, bright (J1910+1256)",
        618994: "Pulsar. Short duration (2 time bins) #1",
        624594: "Pulsar. Short duration (2 time bins) #2",
        438102:"Pulsar. Disappears after 200s",	
        2802: "RFI wrapped at nonzero DM",
        368835: "RFI(?), nulling, DM slightly high",
        34082: "RFI with wandering pulse vs time",
        38999: "RFI, noisy",
        39549: "RFI, wandering pulse vs time",
        38178: "Noisy signal 1",
        2151: "Noisy signal 2",		
        42297: "RFI, pulsar-like pulses, wandering pulse vs time",
        63510: "RFI, severely wandering pulse vs time",	
        223681: "23rd harmonic of PSR B2002+31",
        283742: "17th harmonic of PSR J1850+0026",
        223682: "29th harmonic of PSR B2002+31",
        223683: "31st harmonic of PSR B2002+31",
        38479: "Integer ratio (3/8) of pulsar period (J1921+0812)",	
        184526: "Integer ratio (5/16) of pulsar period (B1915+13)",
        98999: "RFI with two pulses",
        46908: "Sub-millisecond candidate 1",
        70081: "Sub-millisecond candidate 2",
        4303: "Sub-millisecond candidate 3",	
        93300: "Candidate MSP at DM=823(!)",
        294242: "RFI, very artificial RFI signal",
        275603: "RFI, saw-tooth pulses",	
        78392: "Ambiguous candidate (by eye)",
        470608: "No obvious pulses",	
        603449: "RFI with multiple pulses",
        298491: "RFI with pulsar-like DM 1",
        589045: "RFI with broad profile 1",
        613744: "RFI with broad profile 2",
        61646: "RFI with pulsar-like DM 2",
        402979: "RFI, pulsar-like profile",
        465607: "RFI, at 2nd harmonic of 60 Hz",
    }
elif c.survey == "DRIFT":
    # GBT DRIFT pdm_cand_ids
    pdm_cand_ids = {
	7891: "Known pulsar, bright nuller",
        7922: "Known pulsar, fainter",
	4441: "New pulsar, 487 ms",
        4443: "New pulsar, half frequency",
	21775: "RFI wrapped at nonzero DM",
        26526: "Narrowband RFI",
	759: "Just noise, no peak, 250 ms",
        31164: "Just noise, no peak, 12 ms",
    }
else:
    pdm_cand_ids = {}
    raise ValueError("Unknown survey '%s', no demo candidates available" % c.survey)

def demo_rating(rating):
    for (n,i) in sorted([(n,i) for (i,n) in pdm_cand_ids.items()]):
        r = rating.rate_by_cand_id(i)
	if i in cand_ratings:
	    cand_ratings[i].append(r)
	else:
	    cand_ratings[i] = [r]
        print "\t%s:\t%g" % (n,r)

if __name__=='__main__':
    import rating
    import profile_ratings
    import harmonic_rating
    import pfd_ratings
    import known_pulsar_rating

    global cand_ratings
    cand_ratings = {}
    rating_objects = []
#    for R in [profile_ratings.GaussianWidth, profile_ratings.GaussianHeight, profile_ratings.PeakOverRMS,harmonic_rating.HarmonicRating, profile_ratings.DutyCycle, pfd_ratings.RatioRating,known_pulsar_rating.KnownPulsarRating]:
    for R in [known_pulsar_rating.KnownPulsarRating]:
        r = R(rating.usual_database())
	rating_objects.append(r)
	print r.name
        demo_rating(r)
    if (len(sys.argv) > 1) and ("report" in [x.lower() for x in sys.argv[1:]]):
	demo_report.plot_report(rating_objects,cand_ratings,pdm_cand_ids)
