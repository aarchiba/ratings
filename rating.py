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

class DatabaseWalker:
    def __init__(self, DBconn, with_files=False):
        self.DBconn = DBconn
        self.DBcursor = MySQLdb.cursors.DictCursor(self.DBconn)
        self.with_files = with_files

    def run(self,where_clause=None):
        self.DBcursor.execute("SELECT * FROM headers")
        for hdr in self.DBcursor.fetchall():
            if where_clause is None:
                self.DBcursor.execute("SELECT * FROM pdm_candidates WHERE header_id = %s",hdr["header_id"])
            else:
                self.DBcursor.execute("SELECT * FROM pdm_candidates WHERE header_id = %s AND ("+where_clause+")",hdr["header_id"])
            d = tempfile.mkdtemp()
            try:
                for candidate in self.DBcursor.fetchall():
                    if self.pre_check_candidate(hdr,candidate):
                        if self.with_files:
                                try:
                                    f = self.extract_file(d,candidate)
                                except ValueError, e:
                                    sys.stderr.write(str(e))
                                    continue
                                try:
                                    self.act_on_candidate(hdr,candidate,f)
                                except Exception, e:
                                    print "Exception raised while rating candidate %s: %s" % (candidate["pdm_cand_id"], e)
                        else:
                            try:
                                self.act_on_candidate(hdr,candidate)
                            except Exception, e:
                                print "Exception raised while rating candidate %s: %s" % (candidate, e)
            finally:
                shutil.rmtree(d)

    def extract_file(self,dir,candidate):
        f = get_one(self.DBcursor,"SELECT * FROM pdm_plot_pointers WHERE pdm_cand_id = %s", candidate["pdm_cand_id"])
        if f is None:
            raise ValueError("Warning: candidate %d does not appear to have file information\n" % candidate['pdm_cand_id'])

        filename = f["filename"]
        pfd_filename = filename.split(".ps.gz")[0]

        path = f["path"]
        base, junk = filename.split('_DM')
        rfn = os.path.join(dir,pfd_filename)
        if not os.path.exists(rfn):
            # FIXME: double-check none starts with /
            tgz_path = os.path.join(path,base+"_pfd.tgz")
            tar_path = os.path.join(path,base+"_pfd.tar")
            if os.path.exists(tar_path):
                subprocess.call(["tar","-C",dir,"-x","-f",tar_path])
            elif os.path.exists(tgz_path):
                subprocess.call(["tar","-C",dir,"-x","-z","-f",tgz_path])
            else:
                raise ValueError("Cannot find tar file")
        return prepfold.pfd(rfn)

    def run_by_cand_id(self,pdm_cand_id):

        candidate = candidate_by_id(self.DBconn,pdm_cand_id)
        hdr = header_for_candidate(self.DBconn,candidate)

        d = tempfile.mkdtemp()
        try:
            if self.with_files:
                    f = self.extract_file(d,candidate)
                    self.act_on_candidate(hdr,candidate,f)
            else:
                self.act_on_candidate(hdr,candidate)
        finally:
            shutil.rmtree(d)

    def pre_check_candidate(self, hdr, candidate):
        """Called to check whether it's worth extracting the file for a candidate"""
        return True

    def act_on_candidate(self,hdr,candidate,pfd=None):
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

    def act_on_candidate(self,hdr,candidate,pfd_file=None):
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

    def __init__(self, DBconn, name, version, description, with_files=True):
        self.name = name
        self.version = version
        self.description = description
        DatabaseWalker.__init__(self,DBconn,with_files=with_files)
        
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
            self.DBcursor.execute("INSERT INTO rating_types SET name=%s, description=%s, version=%s",(self.name,self.description,self.version))
            r = get_one(self.DBcursor,"SELECT * FROM rating_types WHERE name=%s AND version=%s", (self.name, self.version))

        self.rating_id = r["rating_id"]

        cv = get_one(self.DBcursor,"SELECT * FROM rating_type_current_versions WHERE name=%s", self.name)
        if cv:
            if self.version<cv["current_version"]:
                warnings.warn("Newer version of statistic (%d>%d) already exists in database" % (cv["current_version"],self.version))
            elif self.version>cv["current_version"]:
                self.DBcursor.execute("UPDATE rating_type_current_versions SET rating_id=%s, current_version=%s WHERE name=%s", (self.rating_id, self.version, self.name))
        else:
            self.DBcursor.execute("INSERT INTO rating_type_current_versions SET rating_id=%s, current_version=%s, name=%s", (self.rating_id, self.version, self.name))

    def rate_candidate(self,hdr,candidate,pfd_file=None):
        """Override to return the rating for a candidate"""
        raise NotImplementedError

    def run(self,where_clause=None):
        self.setup_tables() # Make sure the rating table exists
        DatabaseWalker.run(self,where_clause=where_clause)

    def rate_by_cand_id(self,pdm_cand_id):

        candidate = candidate_by_id(self.DBconn,pdm_cand_id)
        if candidate is None:
            raise ValueError("Candidate %s not found!" % pdm_cand_id)
        hdr = header_for_candidate(self.DBconn,candidate)

        d = tempfile.mkdtemp()
        try:
            if self.with_files:
                    f = self.extract_file(d,candidate)
                    return self.rate_candidate(hdr,candidate,f)
            else:
                return self.rate_candidate(hdr,candidate)
        finally:
            shutil.rmtree(d)
            
    def act_on_candidate(self,hdr,candidate,pfd_file=None):
        r = self.rate_candidate(hdr,candidate,pfd_file)
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
    import config as c
    return MySQLdb.connect(host=c.host,db=c.database_v2,user=c.usrname,passwd=c.pw)
