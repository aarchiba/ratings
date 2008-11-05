import numpy as np
import MySQLdb
import config as c
import tempfile
import shutil
import os.path
import subprocess
import prepfold

def usual_database():
    return MySQLdb.connect(host=c.host,db=c.database_v2,user=c.usrname,passwd=c.pw)

def get_data(query, dictcursor=False, debug=0):
    """
    Generic function to get data from database given a query.
    """
    if debug:
	print query
    try:
	DBconn = usual_database()
	if dictcursor:
	    DBcursor = MySQLdb.cursors.DictCursor(DBconn)
	else:
	    DBcursor = DBconn.cursor()
	DBcursor.execute(query)
	data = DBcursor.fetchall()
	DBconn.close()
    except MySQLdb.ProgrammingError:
	DBconn.close()
	sys.stderr.write("\nOffending query:\n %s\n\n" % query)
	raise
    if debug:
	print "num entries returned: ", len(data)
    return data

def get_one(DBcursor,cmd,arg=None):
    DBcursor.execute(cmd,arg)
    return DBcursor.fetchone()

def candidate_by_id(DBconn,pdm_cand_id):
    return get_one(MySQLdb.cursors.DictCursor(DBconn),"SELECT * FROM pdm_candidates WHERE pdm_cand_id=%s", pdm_cand_id) 

def header_for_candidate(DBconn,candidate):
    return get_one(MySQLdb.cursors.DictCursor(DBconn),"SELECT * FROM headers WHERE header_id=%s", candidate["header_id"])

def get_pfd_by_cand_id(pdm_cand_id):
    DBconn = usual_database()
    candidate = candidate_by_id(DBconn,pdm_cand_id)
    if candidate is None:
        raise ValueError("Candidate %s not found!" % pdm_cand_id)
    hdr = header_for_candidate(DBconn,candidate)

    d = tempfile.mkdtemp()
    try:
        f = extract_file(d,candidate)
    finally:
	DBconn.close()
        shutil.rmtree(d)
    return f

def extract_file(dir,candidate):
    DBconn = usual_database()
    f = get_one(MySQLdb.cursors.DictCursor(DBconn),"SELECT * FROM pdm_plot_pointers WHERE pdm_cand_id = %s", candidate["pdm_cand_id"])
    DBconn.close()
    if f is None:
        raise ValueError("Warning: candidate %d does not appear to have file information\n" % candidate['pdm_cand_id'])

    filename = f["filename"]
    pfd_filename = filename.split(".ps.gz")[0]

    path = f["path"]
    base, junk = filename.split('_DM')
    if c.survey=="PALFA":
        beam = base.split("_")[-1][0] # PALFA beam number
        rfn = os.path.join(dir,beam,pfd_filename) # PALFA pfd files are inside subdirectory in tarball
    elif c.survey=="DRIFT":
        rfn = os.path.join(dir,pfd_filename)
    else:
        raise ValueError("Unknown survey '%s'" % c.survey)
    if not os.path.exists(rfn):
        # FIXME: double-check none starts with /
        
        # PALFA tarballs don't have _pfd in the filename
        tgz_path = os.path.join(path,base+".tgz")
        tar_path = os.path.join(path,base+".tar")
        tar_gz_path = os.path.join(path,base+".tar.gz")
        pfd_tgz_path = os.path.join(path,base+"_pfd.tgz")
        pfd_tar_path = os.path.join(path,base+"_pfd.tar")
        pfd_tar_gz_path = os.path.join(path,base+"_pfd.tar.gz")
        if os.path.exists(tar_path):
            subprocess.call(["tar","-C",dir,"--wildcards","-x","*.pfd","-f",tar_path])
        elif os.path.exists(tgz_path):
            subprocess.call(["tar","-C",dir,"--wildcards","-x","*.pfd","-z","-f",tgz_path])
        elif os.path.exists(tar_gz_path):
            subprocess.call(["tar","-C",dir,"--wildcards","-x","*.pfd","-z","-f",tar_gz_path])
        elif os.path.exists(pfd_tar_path):
            subprocess.call(["tar","-C",dir,"--wildcards","-x","*.pfd","-f",pfd_tar_path])
        elif os.path.exists(pfd_tgz_path):
            subprocess.call(["tar","-C",dir,"--wildcards","-x","*.pfd","-z","-f",pfd_tgz_path])
        elif os.path.exists(pfd_tar_gz_path):
            subprocess.call(["tar","-C",dir,"--wildcards","-x","*.pfd","-z","-f",pfd_tar_gz_path])
        else:
            raise ValueError("Cannot find tar file")
    return prepfold.pfd(rfn)

def prep_profile(pfd_file):
    pfd_file.dedisperse(pfd_file.bestdm)
    prof = pfd_file.combine_profs(1,1)[0,0]
    prof -= np.mean(prof)
    return prof

def get_default_pdm_class_type_id():
    DBconn = usual_database()
    t = get_one(MySQLdb.cursors.DictCursor(DBconn),"SELECT * FROM pdm_classification_types WHERE description=%s","Human 8-Level Classification;0:Not Classified;1:Class 1;2:Class 2;3:Class 3;4:RFI;5:Not A Pulsar;6:Known;7:Harmonic")["pdm_class_type_id"]
    DBconn.close()
    return t
