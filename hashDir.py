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
    	                default=False, help='''When this flag is present,
    	                                       update manifest with changes. 
    	                                       Default: False''')
    parser.add_argument('--show-progress',action="store_true", 
                        default=False, help='''When this flag is present,
                                               a progress indicator will
                                               show on STDOUT. 
                                               Default: False''')
    parser.add_argument('--report-added',action="store_true", 
                        default=False, help='''Report newly found files.
                                               Default: False''')
    parser.add_argument('--report-removed',action="store_true", 
                        default=False, help='''Report files that no longer exist.
                                               Default: False''')
    parser.add_argument('--report-changed',action="store_true", 
                        default=False, help='''Report files that have been changed.
                                               Default: False''')
    parser.add_argument('--report-unchanged',action="store_true", 
                        default=False, help='''Report files that are unchanged.
                                               Default: False''')
    parser.add_argument('--verbose',action="store_true", 
    	                default=False, help="Be verbose")
    parser.add_argument('--version', action='version', 
    	                version='%(prog)s 1.0')
    args = parser.parse_args()
    
    # Do Furtive stuff
    hashes = Furtive(args.dir, args.verbose) # Create new Furtive object with dir
    hashes.show_progress(args.show_progress) # Show progress while computing
    hashes.set_manifest(args.manifest) # Set manifest file. Optional
    hashes.compare() # Tell Furtive to compare hashes
    
    if args.show_progress:
        print "\n",

    # Print out report for possibly emailing
    if args.report_added:
       print "Added: "
       for file in hashes.added:
          print "    " + hashes.get_hash(file) + "  " + file
    
    if args.report_removed:
       print "Removed: "
       for file in hashes.removed:
          print "    " + hashes.get_previous_hash(file) + "  " + file

    if args.report_unchanged:
       print "Unchanged: "
       for file in hashes.unchanged:
          print "    " + hashes.get_previous_hash(file) + "  " + hashes.get_hash(file) + "  " + file

    if args.report_changed:
       print "Changed: "
       for file in hashes.changed:
          print "    " + hashes.get_previous_hash(file) + "  " + hashes.get_hash(file) + "  " + file

    # Save the computed hashes to the manifest
    if args.update_manifest == True: 
        hashes.update_manifest()


if __name__ == "__main__":
    main()
