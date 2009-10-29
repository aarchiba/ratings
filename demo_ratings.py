import config as c
import demo_report
import sys

if c.survey == "PALFA":
    # PALFA pdm_cand_ids
    pdm_cand_ids = {
    284989: "- Known pulsar, narrow peak (J1900+06)",
#    283739: "- Known pulsar, two peaks (J1850+0026)",
#    591295: "- Known pulsar, fainter, with burst of RFI",
#    184508: "- Known pulsar, very strong (B1915+13)",
#    197463: "- Known pulsar (J1921+0812)",
#    314966: "- Known pulsar (J1948+25)",
#    657727: "- Known pulsar (J2013+31)",
#    477058: "- Known pulsar (J1929+1905)",
#    591295: "- Known pulsar (J1919+13) w/ nice RFI burst",
#    570099: "- Known pulsar (J1855+02) w/ nice RFI burst",
    663819: "- New PALFA MSP, 2.15 ms",
    157246: "- Noise, 3.21 ms",
#    434756: "- Known MSP, bright (J1910+1256)",
#    618994: "- Known pulsar, Short duration (2 time bins) #1",
#    624594: "- Known pulsar, Short duration (2 time bins) #2",
    438103: "- Known pulsar (DMB)",
#    438102: "- Known pulsar (DMB), disappears after 200s",    	
    638386: "- Known pulsar, weak (J1905+09)",
    280798: "- Known pulsar, weak (B1904+06)",
    281307: "- Known pulsar, weak (B1904+06)",
    2802: "- RFI wrapped at nonzero DM",
    368835: "- RFI(?), nulling, DM slightly high",
    34082: "- RFI with wandering pulse vs time",
    38999: "- RFI, noisy",
    39549: "- RFI, wandering pulse vs time",
    38178: "- Noisy signal  1",
    2151: "- Noisy signal  2", 
    2150: "- Noisy signal  3",
    3264: "- Noisy signal  4",
    2050: "- Noisy signal  5",
    1944: "- Noisy signal  6",	
    1309: "- Noisy signal  7",	
    3307: "- Noisy signal  8",
    13166: "- Noisy signal  9",
    13105: "- Noisy signal 10",
    138785: "- Noisy signal 11",
    431941: "- Noisy signal 12",
    206485: "- Noisy signal 13",
    297325: "- Noisy signal 14",
    258999: "- Noisy signal 15",
    42297: "- RFI, pulsar-like pulses, wandering pulse vs time 1",
    786137: "- RFI, pulsar-like pulses, wandering pulse vs time 1",
    63510: "- RFI, severely wandering pulse vs time",	
#    223681: "- 23rd harmonic of PSR B2002+31",
#    283742: "- 17th harmonic of PSR J1850+0026",
#    223682: "- 29th harmonic of PSR B2002+31",
#    223683: "- 31st harmonic of PSR B2002+31",
#    297624: "- 90th harmonic of PSR B1900+06",
     126399: "- 31st harmonic of PSR 1921+0812, weak",
     127435: "- 17th harmonic of PSR J1921+0812, very weak",
     351351: "- 17th harmonic of PSR B1924+16, weak, intermittent",
     184532: "- 41st harmonic of PSR B1915+13, very weak, intermittent",
#    38479: "- Integer ratio (3/8) of pulsar period (J1921+0812)",	
#    184526: "- Integer ratio (5/16) of pulsar period (B1915+13)",
#    297610: "- Integer ratio (5/33) of pulsar period (J1900+06)",
#    297608: "- Integer ratio (3/28) of pulsar period (J1900+06)",
#    297601: "- Integer ratio (2/25) of pulsar period (J1900+06)",
#    432680: "- Integer ratio (3/25) of pulsar period (J1844+00)",
    127432: "- Integer ratio (2/7) of pulsar period (J1921+08), weak",
    284995: "- Integer ratio (2/9) of pulsar period (1900+06), weak",
    429797: "- Integer ratio (2/9) of pulsar period (J1908+0909), weak",
    351350: "- Integer ratio (2/11) of pulsar period (B1924+16), weak, intermittent",
    98999: "- RFI with two pulses",
    46908: "- Sub-millisecond candidate  1",
    70081: "- Sub-millisecond candidate  2",
    4303: "- Sub-millisecond candidate  3",	
    466616: "- Sub-millisecond candidate  4",
    397570: "- Sub-millisecond candidate  5",
    433056: "- Sub-millisecond candidate  6",
    492249: "- Sub-millisecond candidate  7",
    434962: "- Sub-millisecond candidate  8",
    334718: "- Sub-millisecond candidate  9",
    548226: "- Pulsar-like DM, P=1 ms",
    93300: "- Candidate MSP at DM=823(!)",
    294242: "- RFI, very artificial RFI signal",
    467129: "- RFI, very spiky antipulses",
    275603: "- RFI, saw-tooth pulses",	
    78392: "- Ambiguous candidate  1",
    311672: "- Ambiguous candidate  2",
    314909: "- Ambiguous candidate  3",
    345356: "- Ambiguous candidate (probably RFI)  4",
    293226: "- Ambiguous candidate  5",
    307906: "- Ambiguous candidate  6",
    303103: "- Ambiguous candidate  7",
    397570: "- Ambiguous candidate  8",
    317720: "- Ambiguous candidate  9",
    650895: "- Ambiguous candidate 10",
    273767: "- Ambiguous candidate 11",
    266771: "- Ambiguous candidate 12",
    426141: "- Ambiguous candidate 13",	
    470608: "- No obvious pulses",	
    603449: "- RFI with multiple pulses",
    298491: "- RFI with pulsar-like DM 1",
    589045: "- RFI with broad profile 1",
    613744: "- RFI with broad profile 2",
    61646: "- RFI with pulsar-like DM 2",
    402979: "- RFI, pulsar-like profile",
    465607: "- RFI, at 2nd harmonic of 60 Hz #1",
    58950: "- RFI, at 2nd harmonic of 60 Hz #2", 
    72223: "- RFI, at 2nd harmonic of 60 Hz #3",  
    42047: "- RFI, at 60 Hz #1",
    2551: "- RFI, at 60 Hz #2",
    35710: "- RFI, at 60 Hz #3",
    399272: "- RFI, at 60 Hz #4", 
    11166: "- RFI, at 125 Hz #1",
    120364:"- RFI, at 125 Hz #2",
    551191: "- RFI, at 125 Hz #3",
    565749: "- RFI, at 333 Hz", 	
    597346: "- RFI, at 1000 Hz",
    560447: "- RFI, at 1.5 ms",
    587608: "- RFI, at 2.76 ms",
    549070: "- RFI, at 500 Hz #1",
    566317: "- RFI, at 500 Hz #2",
    301499: "- RFI, at 400 Hz",
    598694: "- RFI, at 250 Hz",
    297289: "- RFI, strong 1",
    592453: "- RFI, strong 2",
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
    import rfi_rating

    global cand_ratings
    cand_ratings = {}
    rating_objects = []


#    for R in [profile_ratings.GaussianWidth, profile_ratings.GaussianHeight, harmonic_rating.HarmonicRating, profile_ratings.DutyCycle, pfd_ratings.RatioRating,known_pulsar_rating.KnownPulsarRating, rfi_rating.RFIRating]:
#    for R in [known_pulsar_rating.KnownPulsarRating]:
#    for R in [harmonic_rating.HarmonicRating]:
#    for R in [profile_ratings.GaussianHeight]:
#    for R in [profile_ratings.GaussianWidth]:
#    for R in [pfd_ratings.RatioRating]:
    for R in [rfi_rating.RFIRating]:

        r = R(rating.usual_database())
	rating_objects.append(r)
	print r.name
        demo_rating(r)
    if (len(sys.argv) > 1) and ("report" in [x.lower() for x in sys.argv[1:]]):
	demo_report.plot_report(rating_objects,cand_ratings,pdm_cand_ids)
