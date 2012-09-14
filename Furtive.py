import argparse, os, hashlib, sys, sqlite3

class Furtive:
    verbose = False
    dir = ""
    hashList = {}
    sqliteFile = ".manifest.db"
    sqliteConnection = None
    sqliteCursor = None
    
    def __init__(self, dir, verbose = False):
        self.dir = dir
        self.verbose = verbose

    # Connect to sqlite3 database
    def __openDB(self):        
        try:
            self.sqliteCursor = sqlite3.connect(os.path.join(self.dir, self.sqliteFile))
            self.sqliteCursor = self.sqliteCursor.cursor()
            self.sqliteCursor.execute("CREATE TABLE IF NOT EXISTS filehashes(filename TEXT, hash TEXT)")
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)
    
    # close the DB connection
    def __closeDB(self):
        self.sqliteCursor = None
        
    def setVerbosity(self, verbosity):
        self.verbosity = verbosity

    def setDirectory(self, dir):
        self.dir = dir

    # Change DB
    def setSQLFile(self, sqliteFile):
        self.sqliteFile = sqliteFile

    # Generate a set consisting of files relative to the given dir 
    def getFiles(self,dir = None):
        # If no dir is provided when calling this method, use object's dir
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

    # Hash each file in the set fileSet. Returns a dict of reltive_path/file: hash    
    def hashFiles(self,fileSet):
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
     
    # Get hash dictionary from sqlite3 DB
    def getPreviousHashes(self,dir = None):
        self.__openDB()
        # If no dir is provided when calling this method, use object's dir
        if dir is None:
            dir = self.dir
       
        # Run SQL to pull stuff from the DB 
        try:
            self.sqliteCursor.execute("SELECT * FROM filehashes");
        except sqlite3.Error, e:
            sys.stderr.write("Error " + e.args[0] + ":\n")
            sys.exit(1)
        else:
            fetchedHashes = self.sqliteCursor.fetchall()
            # Fetch rows and place in a dict we can use
            hashes = {}
            for file, hash in fetchedHashes:
                hashes[file] = hash
            return hashes
        self.__closeDB()
    
    # Save hashes to sqlite3 DB
    def saveHashes(self, hashedFileList = None):
        self.__openDB()
        if hashedFileList is None:
            hashedFileList = self.hashList

        # Try to insert hashes in DB
        try:
            for file, hash in hashedFileList.iteritems():
                self.sqliteCursor.execute("INSERT OR REPLACE INTO filehashes VALUES (?,?)",(file, hash));
                if self.verbose == True:
                    sys.stderr.write("Inserted Hash in DB for: " + file + "\n")
        except sqlite3.Error, e:
            sys.stderr.write("Error " + e.args[0] + ":\n")
            sys.exit(1)
        self.__closeDB()

    # Compare the file lists and report the changes
    def compareFileLists(self, fileList1, fileList2):
        fileList1_set = set(fileList1.keys())
        fileList2_set = set(fileList2.keys())
        print "Set1: ",fileList1_set
        print "Set2: ",fileList2_set
        fileList_intersect = fileList1_set.intersection(fileList2_set)
        # First see what files been added
        added = fileList1_set - fileList2_set
        print added
        # Next, see what files been removed
        removed = fileList2_set - fileList1_set
        print removed
        # Check to see what has changed
        #changed = set(o for o in fileList_intersect if fileList1.[o] != fileList2[o])

        # Check to see what has not changed (might be a waste of resources)
        #unchanged = set(o for o in fileList_intersect if fileList1.[o] == fileList2[o])
        
        
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
    print "Previous Hashes: ",previousHashes
    hashes.compareFileLists(hashList,previousHashes)
    hashes.saveHashes(hashList)
    
# Check Python Version
if sys.hexversion < 0x02070000:
    raise SystemError("Python version 2.7.0 or greater is required. You are running " + sys.version)

if __name__ == "__main__":
    main()
