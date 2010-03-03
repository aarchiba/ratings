
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

def demo_rating(rating):
    for (n,i) in sorted([(n,i) for (i,n) in pdm_cand_ids.items()]):
        r = rating.rate_by_cand_id(i)
        print "\t%s:\t%g" % (n,r)

if __name__=='__main__':
    import rating
    import profile_ratings
    import harmonic_rating
    import pfd_ratings

    for R in [profile_ratings.GaussianWidth, profile_ratings.GaussianHeight, profile_ratings.PeakOverRMS,harmonic_rating.HarmonicRating, profile_ratings.DutyCycle, pfd_ratings.RatioRating]:
        r = R(rating.usual_database())
        print r.name
        demo_rating(r)
