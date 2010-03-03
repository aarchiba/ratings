import MySQLdb
import re
import tarfile
import tempfile
import sys
import os
import shutil
import warnings
import subprocess
import numpy as np

import prepfold


def get_one(cursor,cmd,arg=None):
    cursor.execute(cmd,arg)
    return cursor.fetchone()
def get_all(cursor,cmd,arg=None):
    cursor.execute(cmd,arg)
    return cursor.fetchall()

def extract_file(dir,candidate,f,with_bestprof):
        filename = f["filename"]
        pfd_filename = filename.split(".ps.gz")[0]

        path = f["path"]
        base, junk = filename.split('_DM')
        rfn = os.path.join(dir,pfd_filename)
        if not os.path.exists(rfn):
            if False:
                # FIXME: double-check none starts with /
                tar = tarfile.open(os.path.join(path,base+"_pfd.tgz"),"r")
                tar.extract_all(dir)
            else:
                subprocess.call(["tar","-C",dir,"-x","-z","-f",os.path.join(path,base+"_pfd.tgz")])
        if with_bestprof:
            if not os.path.exists(rfn+".bestprof"):
                # Create bestprof file using 'show_pfd'
                dir, pfdfn = os.path.split(rfn)
                retcode = subprocess.call(["show_pfd",rfn,"-noxwin"],stdout=subprocess.PIPE)
                #retcode = subprocess.call(["show_pfd",rfn,"-noxwin"])
                if retcode:
                    raise ValueError("show_pfd failed with return code %d; pfd file is %s, directory contents are %s\n" % (retcode,rfn,sorted(os.listdir(dir))))
                shutil.move(pfdfn+".bestprof", dir)
                shutil.move(pfdfn+".ps", dir)

        return prepfold.pfd(rfn)


def run(DBconn, ratings, where_clause=None):
    for r in ratings:
        r.setup_tables()
    DBcursor = MySQLdb.cursors.DictCursor(DBconn)

    DBcursor.execute("SELECT * FROM headers")
    for hdr in DBcursor.fetchall()[::-1]:
        if where_clause is None:
            DBcursor.execute("SELECT * FROM pdm_candidates WHERE header_id = %s",hdr["header_id"])
        else:
            DBcursor.execute("SELECT * FROM pdm_candidates WHERE header_id = %s AND ("+where_clause+")",hdr["header_id"])
        d = tempfile.mkdtemp()
        try:
            for candidate in DBcursor.fetchall():
                cache = {}
                rs = [r for r in ratings if r.pre_check_candidate(hdr,candidate)]
                with_files = False
                with_bestprof = False

                for r in rs:
                    if r.with_files:
                        with_files=True
                    if r.with_bestprof:
                        with_bestprof=True

                if with_files:
                    ff = get_one(DBcursor,"SELECT * FROM pdm_plot_pointers WHERE pdm_cand_id = %s", candidate["pdm_cand_id"])
                    if ff is None:
                        raise ValueError("Warning: candidate %d does not appear to have file information\n" % candidate['pdm_cand_id'])
                    f = extract_file(d,candidate,ff,with_bestprof=with_bestprof)
                    #try:
                    #    f = extract_file(d,candidate,ff,with_bestprof=with_bestprof)
                    #except Exception, e:
                    #   sys.stderr.write(str(e))
                else:
                    f = None

                for r in rs:
                    r.act_on_candidate(hdr,candidate,f,cache=cache)
                    #try:
                    #    r.act_on_candidate(hdr,candidate,f,cache=cache)
                    #except Exception, e:
                    #    print "Exception raised while rating candidate %s: %s" % (candidate["pdm_cand_id"], e)
        finally:
            shutil.rmtree(d)

class DatabaseWalker:
    def __init__(self, DBconn, with_files=False, with_bestprof=False):
        self.DBconn = DBconn
        self.DBcursor = MySQLdb.cursors.DictCursor(self.DBconn)
        self.with_files = with_files
        self.with_bestprof = with_bestprof

    def run(self,where_clause=None):
        run(self.DBconn, [self], where_clause)

    def pre_check_candidate(self, hdr, candidate):
        """Called to check whether it's worth extracting the file for a candidate"""
        return True

    def act_on_candidate(self,hdr,candidate,pfd=None,cache=None):
        """Override to implement a particular database walker.

        pfd is a prepfold.pfd object, representing a .pfd file.
        This file contains a partly-folded, partly-dedispersed time
        series. 

        pfd.proflen : the length of each profile in bins
        pfd.npart : the number of time subintegrations
        pfd.nsub : the number of frequency subintegrations
        
        pfd.profiles : an array of shape (npart, nsub, proflen) containing the values

        pfd.dedisperse(DM=self.bestdm, interp=0) : shift the profiles
        
        """

        raise NotImplementedError

    

class DatabaseLister(DatabaseWalker):

    def __init__(self, DBconn):
        DatabaseWalker.__init__(self,DBconn,with_files=True)

    def act_on_candidate(self,hdr,candidate,pfd_file=None,cache=None):
        print hdr, candidate, pfd_file

# Table rating_type_current_versions
# Columns:
#   rating_id
#   name
#   current_version

# Table rating_types
# Columns:
#   rating_id
#   name
#   description
#   version

# Table ratings
# Columns:
#  rating_id
#  pdm_cand_id
#  value
class DatabaseRater(DatabaseWalker):

    def __init__(self, DBconn, name, version, description, with_files=True, with_bestprof=False):
        self.name = name
        self.version = version
        self.description = description
        DatabaseWalker.__init__(self,DBconn,with_files=with_files,
                                with_bestprof=with_bestprof)
        
    def setup_tables(self):
        self.DBcursor.execute("""CREATE TABLE IF NOT EXISTS 
            rating_type_current_versions(rating_id int(4) not null,
                                         name varchar(20) not null primary key,
                                         current_version int(4) not null)
            """)
        self.DBcursor.execute("""CREATE TABLE IF NOT EXISTS 
            rating_types(rating_id int(4) not null auto_increment primary key,
                         name varchar(20) not null,
                         description text,
                         version int(4) not null)
            """)
        self.DBcursor.execute("""CREATE TABLE IF NOT EXISTS 
            ratings(rating_id int(4) not null,
                    pdm_cand_id int(4) not null,
                    value float(8),
                    CONSTRAINT pk PRIMARY KEY (pdm_cand_id,rating_id))
            """)
        r = get_one(self.DBcursor,"SELECT * FROM rating_types WHERE name=%s AND version=%s", (self.name, self.version))
        if not r:
            print "Creating new rating type %s version %s" % (self.name, self.version)
            self.DBcursor.execute("INSERT INTO rating_types SET name=%s, description=%s, version=%s",(self.name,self.description,self.version))
            r = get_one(self.DBcursor,"SELECT * FROM rating_types WHERE name=%s AND version=%s", (self.name, self.version))
            print get_all(self.DBcursor,"SELECT * FROM rating_types")

        self.rating_id = r["rating_id"]

        cv = get_one(self.DBcursor,"SELECT * FROM rating_type_current_versions WHERE name=%s", self.name)
        if cv:
            if self.version<cv["current_version"]:
                warnings.warn("Newer version of statistic (%d>%d) already exists in database" % (cv["current_version"],self.version))
            elif self.version>cv["current_version"]:
                self.DBcursor.execute("UPDATE rating_type_current_versions SET rating_id=%s, current_version=%s WHERE name=%s", (self.rating_id, self.version, self.name))
        else:
            self.DBcursor.execute("INSERT INTO rating_type_current_versions SET rating_id=%s, current_version=%s, name=%s", (self.rating_id, self.version, self.name))

    def rate_candidate(self,hdr,candidate,pfd_file=None,cache=None):
        """Override to return the rating for a candidate"""
        raise NotImplementedError

    def run(self,where_clause=None):
        self.setup_tables() # Make sure the rating table exists
        DatabaseWalker.run(self,where_clause=where_clause)

    def act_on_candidate(self,hdr,candidate,pfd_file=None,cache=None):
        r = self.rate_candidate(hdr,candidate,pfd_file,cache)
        print "Candidate %d rated %f" % (candidate["pdm_cand_id"],r)
        self.DBcursor.execute("INSERT INTO ratings (rating_id,pdm_cand_id,value) VALUES (%s,%s,%s)",(self.rating_id,candidate["pdm_cand_id"],r))

    def pre_check_candidate(self,hdr,candidate):
        if get_one(self.DBcursor,"SELECT * FROM ratings WHERE rating_id=%s AND pdm_cand_id=%s", (self.rating_id, candidate["pdm_cand_id"])):
            # Already used this version on this candidate
            print "Candidate %d already rated" % candidate["pdm_cand_id"]
            return False
        else:
            return True

    def value(self,candidate):
        self.setup_tables()
        pdm_cand_id = candidate["pdm_cand_id"]
        r = get_one(self.DBcursor,"SELECT * FROM ratings WHERE pdm_cand_id=%s and rating_id=%s",(pdm_cand_id,self.rating_id))
        if r is None:
            return np.nan
        else:
            return r["value"]

def header_for_candidate(DBconn,candidate):
    return get_one(MySQLdb.cursors.DictCursor(DBconn),"SELECT * FROM headers WHERE header_id=%s", candidate["header_id"])

def candidate_by_id(DBconn,pdm_cand_id):
    return get_one(MySQLdb.cursors.DictCursor(DBconn),"SELECT * FROM pdm_candidates WHERE pdm_cand_id=%s", pdm_cand_id)

def manual_classification(DBconn,candidate):
    t = get_one(MySQLdb.cursors.DictCursor(DBconn),"SELECT * FROM pdm_classification_types WHERE description=%s","Human 8-Level Classification;0:Not Classified;1:Class 1;2:Class 2;3:Class 3;4:RFI;5:Not A Pulsar;6:Known;7:Harmonic")["pdm_class_type_id"]
    r = get_one(MySQLdb.cursors.DictCursor(DBconn),"SELECT * FROM pdm_classifications WHERE pdm_cand_id=%s AND pdm_class_type_id=%s",(candidate["pdm_cand_id"],t))
    if r is None:
        return 0
    else:
        return r["rank"]
    

def usual_database():
    import DRIFT_config as c
    return MySQLdb.connect(host=c.host,db=c.database_v2,user=c.usrname,passwd=c.pw)
