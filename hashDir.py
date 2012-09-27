import argparse
import sys
from Furtive import Furtive

''' '''

def main():
	# If Python 2.6 or lower, should import optparse but erroring out now
    if sys.hexversion < 0x02070000:
        raise SystemError("Python version 2.7.0 or greater is required. You are running " + sys.version)

    parser = argparse.ArgumentParser(description='Get Hash Values of Files within a directory.')
    parser.add_argument('--dir', action="store", default=".", 
    	                 help='''Directory containing files that will be 
    	                         checked. Default: .''')
    parser.add_argument('--hashes', action="store", dest="hashes", default=[''], 
                        help="Hash algorithm to use. Currently supports sha1 only.")
    parser.add_argument('--exclude', action="store", dest="excludes", default=[''], 
                        help="Patterns to exclude files and directories from manifest.")
    parser.add_argument('--manifest', action="store", dest="manifest", 
    	                default='.manifest.db', 
                        help='''Location of the manifast file. Manifests may 
                                be located outside the directory indicated by 
                                --dir. Must provide path and filename of 
                                the manifest file. Default: DIR/.manifest.db''')
    parser.add_argument('--update-manifest',action="store_true", 
    	                default=False, help='''When this flag is present
    	                                       update manifest with changes. 
    	                                       Default: False''')
    parser.add_argument('--verbose',action="store_true", 
    	                default=False, help="Be verbose")
    parser.add_argument('--version', action='version', 
    	                version='%(prog)s 1.0')
    args = parser.parse_args()
    
    hashes = Furtive(args.dir, args.verbose)
    
    # Setting manifest file is optional. Defaults to ./manifest.db
    hashes.set_manifest(args.manifest)

    hashes.compare()
    #hashList = hashes.hashFiles(fileSet)
    #previousHashes = hashes.getPreviousHashes()
    #report = hashes.compareFileLists(hashList,previousHashes)
 
    print "Added: "
    for file in hashes.added:
       print "    " + hashes.get_hash(file) + "  " + file
    print "Removed: "
    for file in hashes.removed:
       print "    " + hashes.get_previous_hash(file) + "  " + file
    print "Unchanged: "
    for file in hashes.unchanged:
       print "    " + hashes.get_previous_hash(file) + "  " + hashes.get_hash(file) + "  " + file
    print "Changed: "
    for file in hashes.changed:
       print "    " + hashes.get_previous_hash(file) + "  " + hashes.get_hash(file) + "  " + file
    
    if args.update_manifest == True: 
        hashes.update_manifest()


if __name__ == "__main__":
    main()
