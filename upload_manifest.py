"""
upload_manifest.py

Uploads the files in a manifest to Amazon Glacier. 

"""

import sys
import time
from Furtive import Furtive

try:
	import boto.glacier
	import boto.glacier.layer2
except ImportError:
	print "boto must be installed to use this script. Run one of the commands"
	print " below to install boto:\n"
	print "\"easy_install boto\""
	print "\"pip install boto\""

try:
    import argparse
except ImportError:
    print "argparse must be installed manually for Python 2.6 and earlier."
    print "please download argparse from http://pypi.python.org/pypi/argparse\n"
    print "Installation can also be attempted with:"
    print "\"easy_install argparse\""
    print "\"pip install argparse\""
    raise


def main():
    start_time = time.time()

    region_names = ""
    for i in boto.glacier.regions(): 
        region_names = region_names + i.name + " "

    parser = argparse.ArgumentParser(description='Upload a manifest to Amazon Glacier or S3')
    parser.add_argument('--dir', action="store", default=".", 
                         help='''Directory containing the manifest. Default: .''')
    parser.add_argument('--aws-secret-access-key', action="store", required=True, help="Your AWS Secret Key")
    parser.add_argument('--aws-access-key-id', action="store", required=True, help="Your AWS Access Key ID")
    parser.add_argument('--vault-name', action="store", required=True, help="Name of the new vault")
    parser.add_argument('--region', action="store", required=True, help="""Glacier region to connect to. 
    	                 Available regions: """ + region_names
    	                )
    parser.add_argument('--show-progress',action="store_true", 
                        default=False, help='''When this flag is present,
                                               a progress indicator will
                                               show on STDOUT. 
                                               Default: False''')
    parser.add_argument('--manifest', action="store", dest="manifest", 
    	                default='.manifest.db', 
                        help='''Location of the manifast file. Manifests may 
                                be located outside the directory indicated by 
                                --dir. Must provide path and filename of 
                                the manifest file. Default: DIR/.manifest.db''')
    args = parser.parse_args()

    layer2 = boto.glacier.layer2.Layer2(aws_access_key_id=args.aws_access_key_id, 
                                        aws_secret_access_key=args.aws_secret_access_key,
                                        region_name=args.region)

    try:
        fur = Furtive(args.dir)
    except:
        raise
    fur.set_manifest(args.manifest) 
    
    try:
        hashes = fur.get_previous_hashes()
    except:
        raise

    if len(hashes) == 0:
        print "No files in manifest. Perhaps you should run hashDir.py to create a manifest first." 
        raise Exception("no_manifest")

    vault = layer2.create_vault(args.vault_name)
    
    file_num = 0
    total_num_files = len(hashes)

    for file in hashes.keys():
        if args.show_progress:
            file_num = file_num + 1
            progress = round((float(file_num) / total_num_files) * 100,1)
            sys.stdout.write("\r" + str(progress) + "% " + 
                             str(file_num) + " of " + str(total_num_files))
            sys.stdout.flush()
        try:
            f = open(file,"r")
        except IOError, e:
        	print "Skipping %s due to error %s" % (file, e)
        else:
            vault.create_archive_from_file(file,f)
            f.close()
    
    #Upload Manifest DB
    f = open(fur.manifest_file,"r")
    vault.create_archive_from_file(fur.manifest_file,f)
    f.close()
    
    end_time = time.time()

    if args.show_progress:
        print "\n"
    
    print "Finished uploading files to the vault %s" % (args.vault_name)
    print "Time taken: %s seconds" % (str(end_time - start_time))

if __name__ == "__main__":
    main()