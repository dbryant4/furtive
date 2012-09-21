import argparse
import os
import hashlib
import sys
import sqlite3

class Furtive:
    verbose = False
    dir = ""
    hashList = {}
    manifestFile = ".manifest.db"
    conn = None
    cur = None
    
    def __init__(self, dir, verbose = False):
        self.dir = dir
        self.verbose = verbose
    
    def __openDB(self):        
        """Open sqlite database"""
        try:
            self.conn = sqlite3.connect(os.path.join(self.dir, self.manifestFile))
            self.cur = self.conn.cursor()
            self.cur.execute("CREATE TABLE IF NOT EXISTS filehashes(filename TEXT, hash TEXT)")
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)
    
    def __closeDB(self):
        """Close sqlite database"""
        self.conn.commit()
        self.cur = None
    
    def __truncateDB(self):
        """Truncate (delete) manifest file """
        self.cur.execute("DELETE FROM filehashes")
    
    def setVerbosity(self, verbosity):
        self.verbosity = verbosity
    
    def setDirectory(self, dir):
        self.dir = dir
    
    def setSQLFile(self, manifestFile):
        """Set manifest file to another file"""
        self.manifestFile = manifestFile
    
    def getFiles(self,dir = None):
        """Generate a set consisting of files relative to the given dir."""
        if dir is None:
            dir = self.dir
        
        fileSet = set()
        for root, dirs, files in os.walk(dir):
            for file in files:
                # Full file path (ex. /etc/rc.d/rc.1/test)
                full_path = os.path.join(root, file)
                # Reative to dir (ex rc.d/rc.1/test)
                relative_path = os.path.relpath(full_path, dir)
                if self.verbose == True:
                    sys.stderr.write("Found File: " + relative_path + "\n")
                fileSet.add(relative_path)
        return fileSet
    
    def hashFiles(self,fileSet):
        """Hash each file in the set fileSet. Returns a dict of reltive_path/file: hash"""
        hashList = {}
        for file in fileSet:
            if self.verbose == True:
                sys.stderr.write("Hashing: " + os.path.join(self.dir, file) + "\n")
 
            # Full file path (ex. /etc/rc.d/rc.1/test)
	    full_path = os.path.join(self.dir, file)

	    # Open file, read it, hash it, place hash in 
	    f = open(full_path, "r")
	    hash = hashlib.sha1("".join(f.readlines())).hexdigest()
	    if self.verbose == True:
	        sys.stderr.write(hash + " " + file + "\n")
	    #Put hash in dictionary
	    hashList[file]=hash
            f.close()
        return hashList
     
    def getPreviousHashes(self,dir = None):
        """Get hash dictionary from sqlite3 DB"""
        self.__openDB()
        # If no dir is provided when calling this method, use object's dir
        if dir is None:
            dir = self.dir
       
        # Run SQL to pull stuff from the DB 
        try:
            self.cur.execute("SELECT * FROM filehashes");
        except sqlite3.Error, e:
            sys.stderr.write("Error " + e.args[0] + ":\n")
            sys.exit(1)
        else:
            fetchedHashes = self.cur.fetchall()
            # Fetch rows and place in a dict we can use
            hashes = {}
            for file, hash in fetchedHashes:
                hashes[file] = hash
            return hashes
        self.__closeDB()
    
    def saveHashes(self, hashedFileList = None):
        """Save hashes to manifest file"""
        self.__openDB()
        self.__truncateDB()
        if hashedFileList is None:
            hashedFileList = self.hashList

        # Try to insert hashes in DB
        try:
            for file, hash in hashedFileList.iteritems():
                self.cur.execute('INSERT INTO filehashes VALUES (?,?)',(file, hash));
                if self.verbose == True:
                    sys.stderr.write("Inserted Hash in DB for: " + file + "\n")
        except sqlite3.Error, e:
            sys.stderr.write("Error " + e.args[0] + ":\n")
            sys.exit(1)
        self.__closeDB()

    def compareFileLists(self, fileList1, fileList2):
        """Compare the file lists and report the changes"""
        fileList1_set = set(fileList1.keys())
        fileList2_set = set(fileList2.keys())
        report = {}

        # Find Intersection
        report['intersect'] = fileList1_set.intersection(fileList2_set)

        # Find files added
        report['added'] = fileList1_set - fileList2_set

        # Next, see what files been removed
        report['removed'] = fileList2_set - fileList1_set
        # Check to see what has changed
        #changed = set(o for o in fileList_intersect if fileList1.[o] != fileList2[o])

        # Check to see what has not changed (might be a waste of resources)
        #unchanged = set(o for o in fileList_intersect if fileList1.[o] == fileList2[o])
        return report
        
        
def main():
    parser = argparse.ArgumentParser(description='Get Hash Values of Files within a directory.')
    parser.add_argument('--dir', action="store", default=".", help='Directory containing files that will be checked')
    parser.add_argument('--hashes', action="store", dest="hashes", default=[''], 
                        help="Hash algorithm to use. Currently supports sha1")
    parser.add_argument('--verbose',action="store_true", default=False, help="Be verbose")
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()
    
    hashes = Furtive(args.dir, args.verbose)
    fileSet = hashes.getFiles()
    hashList = hashes.hashFiles(fileSet)
    previousHashes = hashes.getPreviousHashes()
    hashes.compareFileLists(hashList,previousHashes)
    hashes.saveHashes(hashList)
    
# Check Python Version
if sys.hexversion < 0x02070000:
    raise SystemError("Python version 2.7.0 or greater is required. You are running " + sys.version)

if __name__ == "__main__":
    main()
