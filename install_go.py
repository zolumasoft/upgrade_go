#!/usr/bin/env python3

import requests
import pathlib
import subprocess
import argparse
import sys


#----------------------------------------------------------------------------------------------
# SETUP Strings
#----------------------------------------------------------------------------------------------
RM_CMD = "sudo rm -rf {}"
GO_PATH = "/usr/local/go"
URL_TMPL = "https://dl.google.com/go/{}"
FILE_TMPL = "go{0}.linux-{1}.tar.gz"
INSTALL_CMD = "sudo tar -C /usr/local -xzf {}"

DEB_BASED = ["ubuntu", "debian"]
DEBIAN_CMD = "dpkg --print-architecture"

#----------------------------------------------------------------------------------------------
# Helper functions
#----------------------------------------------------------------------------------------------
def run_cmd(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    return process.communicate()[0].strip().decode('utf-8')

def download_go(version, arch):
    # Set download file and download URL
    download_file = FILE_TMPL.format(version, arch) 
    download_url = URL_TMPL.format(download_file) 
    
    # Download file with requests
    r = requests.get(download_url, stream=True)
    if r.status_code == 200:
        with open(download_file, 'wb') as f:
            f.write(r.raw.read())
        if not pathlib.Path(download_file):
            print("Download failed")
            sys.exit()
    return download_file


#----------------------------------------------------------------------------------------------
# Get arguments
#----------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="Download and Install latest Go")
parser.add_argument(
        '-v', 
        '--version', 
        dest='goversion', 
        help='version to download (1.12.7 etc)', 
        type=str, 
        required=True
)
parser.add_argument(
        '-a', 
        '--arch', 
        dest='goarch', 
        help='platform architecture (amd64, armv6l etc)', 
        type=str, 
        required=True
)
args = parser.parse_args()

# Set variables for architecture and go release version
go_version = args.goversion
linux_arch = args.goarch

# Check current linux distribution
os_family = run_cmd(cmd="lsb_release -i | awk '{print $3}'")
if os_family.lower() in DEB_BASED:
    os_arch = run_cmd(cmd=DEBIAN_CMD)
    if os_arch != linux_arch:
        print("Current linux arch: {}".format(os_arch))
        sys.exit(1)

# Download Go
downfile = download_go(version=go_version, arch=linux_arch)

# Check for old version currently installed. Remove and install
# latest version
delete_prev_go = RM_CMD.format(GO_PATH)
untar_cmd = INSTALL_CMD.format(downfile) 
if pathlib.Path(GO_PATH):
    install_go_cmd = "{} && {} && rm {}".format(delete_prev_go, untar_cmd, downfile)
else:
    install_go_cmd = "{} && rm {}".format(untar_cmd, downfile)

# Install Go
print("Installing {}...".format(downfile))
run_cmd(cmd=install_go_cmd)
print("{} has been installed".format(downfile))

