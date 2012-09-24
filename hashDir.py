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
                        help="Hash algorithm to use. Currently supports sha1")
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
    hashes.setManifestFile(args.manifest)

    fileSet = hashes.getFiles()
    hashList = hashes.hashFiles(fileSet)
    previousHashes = hashes.getPreviousHashes()
    report = hashes.compareFileLists(hashList,previousHashes)
 
    print "Added: "
    for file in report['added']:
       print "    " + file
    print "Removed: "
    for file in report['removed']:
       print "    " + file
    print "Unchanged: "
    for file in report['unchanged']:
       print "    " + file
    print "Changed: "
    for file in report['changed']:
       print "    " + file
    
    if args.update_manifest == True: 
        hashes.saveHashes(hashList)


if __name__ == "__main__":
    main()