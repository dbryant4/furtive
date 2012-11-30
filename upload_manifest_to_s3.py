'''
Uploads a manifest to s3
'''
import os
import sys
import time
from Furtive import Furtive

try:
    import boto
    from boto.s3.connection import S3Connection
    from boto.s3.connection import Location
    from boto.s3.key import Key
    from boto.s3.lifecycle import Lifecycle
except ImportError:
    print "boto must be installed to use this script. Run one of the commands"
    print " below to install boto:\n"
    print "\"easy_install boto\""
    print "\"pip install boto\""
    raise

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
    old_cwd = os.getcwd()

    parser = argparse.ArgumentParser(description='Upload a manifest to Amazon Glacier or S3')
    parser.add_argument('--dir', action="store", default=".", 
                         help='''Directory containing the manifest. Default: .''')
    parser.add_argument('--aws-secret-access-key', action="store", required=True, help="Your AWS Secret Key")
    parser.add_argument('--aws-access-key-id', action="store", required=True, help="Your AWS Access Key ID")
    parser.add_argument('--bucket-name', action="store", required=True, help="Name of the new S3 bucket")
    parser.add_argument('--show-progress',action="store_true", 
                        default=False, help='''When this flag is present,
                                               a progress indicator will
                                               show on STDOUT. 
                                               Default: False''')
    parser.add_argument('--region',action='store', default="DEFAULT", help="""Region to store manifest. 
    	                 APNortheast', 'APSoutheast', 'DEFAULT', 'EU', 'SAEast', 'USWest', 'USWest2'""")
    parser.add_argument('--manifest', action="store", dest="manifest", 
                        default='.manifest.db', 
                        help='''Location of the manifast file. Manifests may 
                                be located outside the directory indicated by 
                                --dir. Must provide path and filename of 
                                the manifest file. Default: DIR/.manifest.db''')
    parser.add_argument('--storage-class', action="store", 
                        default='REDUCED_REDUNDANCY', 
                        help='''Storage class to use. Available options: STANDARD and REDUCED_REDUNDANCY
                                Default: REDUCED_REDUNDANCY''')
    parser.add_argument('--lifecycle', action="store", 
                        default='0', 
                        help='''Number of days until this bucket automatically removes itself from S3. 
                                Default: Never''')

    args = parser.parse_args()

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

    # CreateS3 bucket
    try:
        conn = S3Connection(args.aws_access_key_id, args.aws_secret_access_key)
    except boto.exception.S3CreateError, e:
    	raise
    try:
        #bucket = conn.create_bucket(args.bucket_name, location=Location.USWest)
        bucket = conn.create_bucket(args.bucket_name)
    except boto.exception.S3CreateError, e:
    	print "Bucket already exists. Adding files to existing bucket."
    	bucket = conn.lookup(args.bucket_name)
    	pass

    # Staticly set ACL
    bucket.set_acl('private')

    # Set lifecycle if lifecycle is provided as an command line argument
    try:
        int(args.lifecycle)
    except ValueError, e:
        print "--lifecycle must be an integer greater than 0"
        raise

    if int(args.lifecycle) > 0:
        lifecycle_config = Lifecycle()
        bucket.configure_lifecycle(lifecycle_config)
        lifecycle_config.add_rule('furtive_del_rule_1', '', 'Enabled', int(args.lifecycle))

    file_num = 0
    total_num_files = len(hashes)
    os.chdir(args.dir)
    failed_uploads = []
    for file in hashes.keys():
        if args.show_progress:
            file_num = file_num + 1
            print "\n",file, os.path.getsize(file)
            progress = round((float(file_num) / total_num_files) * 100,1)
            sys.stdout.write("\r" + str(progress) + "% " + 
                             str(file_num) + " of " + str(total_num_files))
            sys.stdout.flush()
        attempt = 0
       
        # Try to upload 5 times, then skip file but report later.
        while attempt < 5:
            try:
                k = Key(bucket)
                k.key = file
                k.set_contents_from_filename(file)
            except Exception as e: # catch *all* exceptions 
                attempt = attempt + 1
                print "Error Uploading %s. Retry %s. Error Details: %s" % (file,str(attempt), e)
                continue
            if attempt >= 5:
                print " Tried to upload %s times. Too many errors. Bailing out. (%s)." % (str(attempt),file),
                failed_uploads.append(file)
                raise
            # Try to change storage class. Skip on error
            try:
                k.change_storage_class(args.storage_class)
            except:
                print "Error setting storage class for %s" % (file)
                continue
            break

    
    #Upload Manifest DB
    k = Key(bucket)
    k.key = fur.manifest_file
    k.set_contents_from_filename(fur.manifest_file)
    k.change_storage_class(args.storage_class)

    end_time = time.time()

    if args.show_progress:
        print "\n"
    
    print "Finished uploading files to the vault %s" % (args.bucket_name)
    print "Time taken: %s seconds" % (str(end_time - start_time))
    if len(failed_uploads) > 0:
        print "Failed to upload the following files:"
        for file in failed_uploads:
            print "    %s" % file
if __name__ == "__main__":
    main()
