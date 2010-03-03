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

class DatabaseWalker:
    def __init__(self, DBconn, with_files=False, with_bestprof=False):
        self.DBconn = DBconn
        self.DBcursor = MySQLdb.cursors.DictCursor(self.DBconn)
        self.with_files = with_files
        self.with_bestprof = with_bestprof

    def run(self,where_clause=None):
        self.DBcursor.execute("SELECT * FROM headers")
        for hdr in self.DBcursor.fetchall()[::-1]:
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
                                except Exception, e:
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
            if False:
                # FIXME: double-check none starts with /
                tar = tarfile.open(os.path.join(path,base+"_pfd.tgz"),"r")
                tar.extract_all(dir)
            else:
                subprocess.call(["tar","-C",dir,"-x","-z","-f",os.path.join(path,base+"_pfd.tgz")])
        if self.with_bestprof:
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
    

class Candidate:
    def __init__(self, header_db, candidate_db, pfd_dir):
        self.header_db = header_db
        self.candidate_db = candidate_db
        self.pfd_dir = pfd_dir

        self._pfd = None
        self._pfd_filename = None
        self._dedispersed_pfd = None
        self._bestprof = False
        self._best_profile = None
        self._profile_bin_var = None

    def _extract_file(self):
        dir = self.pfd_dir
        f = get_one(self.DBcursor,"SELECT * FROM pdm_plot_pointers WHERE pdm_cand_id = %s", candidate["pdm_cand_id"])
        if f is None:
            raise ValueError("Warning: candidate %d does not appear to have file information\n" % candidate['pdm_cand_id'])

        filename = f["filename"]
        pfd_filename = filename.split(".ps.gz")[0]

        path = f["path"]
        base, junk = filename.split('_DM')
        rfn = os.path.join(dir,pfd_filename)
        if not os.path.exists(rfn):
            subprocess.call(["tar","-C",dir,"-x","-z","-f",os.path.join(path,base+"_pfd.tgz")])

        self._pfd_filename = rfn

    def _generate_bestprof(self):
        if not os.path.exists(rfn+".bestprof"):
            # Create bestprof file using 'show_pfd'
            dir, pfdfn = os.path.split(rfn)
            retcode = subprocess.call(["show_pfd",rfn,"-noxwin"],stdout=subprocess.PIPE)
            #retcode = subprocess.call(["show_pfd",rfn,"-noxwin"])
            if retcode:
                raise ValueError("show_pfd failed with return code %d; pfd file is %s, directory contents are %s\n" % (retcode,rfn,sorted(os.listdir(dir))))
            shutil.move(pfdfn+".bestprof", dir)
            shutil.move(pfdfn+".ps", dir)

    def pfd(self, bestprof=False):
        change = False
        if self._pfd is None:
            self._extract_pfd()
            change = True
        if not self._bestprof:
            self._generate_bestprof()
            self._bestprof = True
            change = True
        if change:
            self._pfd = prepfold.pfd(self._pfd_filename)
        return self._pfd

    def dedispersed_pfd(self, bestprof=False):
        change = False
        if self._pfd is None:
            self.pfd(bestprof)
            change = True
        elif bestprof and not self._bestprof:
            self._generate_bestprof()
            self._bestprof = True
            self._pfd = prepfold.pfd(self._pfd_filename)
            change = True
        if change:
            self._dedispersed_pfd = prepfold.pfd(self._pfd_filename)
            self._dedispersed_pfd.dedisperse(self.candidate_db["bestdm"])

    def best_profile(self):
        p = self.pfd(bestprof=True)
        return p.bestprof

    def profile_bin_var(self):
        # Estimate this based on the data cube
        p = self.pfd().profs
        (n,m,r) = p.shape
        return np.mean(np.var(p,axis=-1))/(n*m)

    def subints_aligned(self,dm='best'):
        if dm=='zero':
            pass
        elif dm=='best':
            pass
        else:
            raise ValueError("Aligned subintegrations available only for dm 'zero' or 'best'")


def usual_database():
    import DRIFT_config as c
    return MySQLdb.connect(host=c.host,db=c.database_v2,user=c.usrname,passwd=c.pw)
