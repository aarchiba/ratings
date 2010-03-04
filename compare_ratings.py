import MySQLdb

import rating


def compare_ratings(ratings):
    DBconn = rating.usual_database()
    DBcursor = MySQLdb.cursors.DictCursor(DBconn)

    ids = []
    for rr in ratings:
        if isinstance(rr,basestring):
            DBcursor.execute("SELECT * FROM rating_type_current_versions WHERE name=%s", rr)
            ids.append(DBcursor.fetchone()["rating_id"])
        else:
            r,v = rr
            DBcursor.execute("SELECT * FROM rating_types WHERE name=%s and version=%s", (r,v))
            ids.append(DBcursor.fetchone()["rating_id"])

    id1, id2 = ratings
    fields = ", ".join(["rating%d.value" % i for i in range(len(ids))])
    join = " JOIN ".join(["ratings AS rating%d" % i for i in range(len(ids))])
    ands = " AND ".join(["rating1.pdm_cand_id=rating%d.pdm_cand_id AND rating%d.rating_id = %%s" % (i,i) for i in range(len(ids))])

    command = "SELECT " + fields + " FROM " + join + " WHERE " + ands
    print command
    
    DBcursor.execute(command, ids)
    rs = []
    for match in DBcursor.fetchall():
        v = []
        for i in range(len(ids)):
            if not i:
                v.append(match["value"])
            else:
                v.append(match["rating%d.value" % i])
        rs.append(v)
    return rs


if __name__=='__main__':
    import numpy as np
    import pylab as plt
    #r = np.array(compare_ratings([("Gaussian Height", 5), ("Gaussian Height", 4)]))
    r = np.array(compare_ratings([("Gaussian Height", 5), ("Gaussian Height", 3)]))
    print "%d matches" % r.shape[0]
    plt.plot(r[:,1],r[:,0],".")
    plt.xlabel("Gaussian Height old")
    plt.ylabel("Gaussian Height new")
    plt.show()

