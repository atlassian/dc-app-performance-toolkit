#!/bin/bash


###################    Variables section         ###################
# Confluence version variables
CONFLUENCE_VERSION_FILE="/media/atl/confluence/shared-home/confluence.version"
SUPPORTED_CONFLUENCE_VERSIONS=(6.13.8 7.0.4)
CONFLUENCE_VERSION=$(sudo su confluence -c "cat ${CONFLUENCE_VERSION_FILE}")
echo "Confluence Version: ${CONFLUENCE_VERSION}"

DATASETS_AWS_BUCKET="https://centaurus-datasets.s3.amazonaws.com/confluence"
ATTACHMENTS_TAR="attachments.tar.gz"
ATTACHMENTS_DIR="attachments"
DATASETS_SIZE="large"
ATTACHMENTS_TAR_URL="${DATASETS_AWS_BUCKET}/${CONFLUENCE_VERSION}/${DATASETS_SIZE}/${ATTACHMENTS_TAR}"
TMP_DIR="/tmp"
EFS_DIR="/media/atl/confluence/shared-home"
###################    End of variables section  ###################

# Check if Confluence version is supported
if [[ ! "${SUPPORTED_CONFLUENCE_VERSIONS[@]}" =~ "${CONFLUENCE_VERSION}" ]]; then
  echo "Confluence Version: ${CONFLUENCE_VERSION} is not officially supported by Data Center App Peformance Toolkit."
  echo "Supported Confluence Versions: ${SUPPORTED_CONFLUENCE_VERSIONS[@]}"
  echo "If you want to force apply an existing datasets to your CONFLUENCE, use --force flag with version of dataset you want to apply:"
  echo "e.g. ./upload_attachments --force 6.13.8"
  echo "!!! Warning !!! This may broke your Confluence instance."
  # Check if --force flag is passed into command
  if [[ "$1" == "--force" ]]; then
    # Check if passed Confluence version is in list of supported
    if [[ "${SUPPORTED_CONFLUENCE_VERSIONS[@]}" =~ "$2" ]]; then
      ATTACHMENTS_TAR_URL="${DATASETS_AWS_BUCKET}/$2/${DATASETS_SIZE}/${ATTACHMENTS_TAR}"
      echo "Force mode. Dataset URL: ${ATTACHMENTS_TAR_URL}"
    else
      echo "Correct dataset version was not specified after --force flag."
      echo "Available datasets: ${SUPPORTED_CONFLUENCE_VERSIONS[@]}"
      exit 1
    fi
  else
    # No force flag
    exit 1
  fi
fi

echo "!!! Warning !!!"
echo    # move to a new line
echo "This script restores attachments into Confluence DC created with AWS Quickstart defaults."
echo "You can review or modify default variables in 'Variables section' of this script."
echo    # move to a new line
echo "Variables:"
echo "EFS_DIR=${EFS_DIR}"
echo "ATTACHMENTS_TAR_URL=${ATTACHMENTS_TAR_URL}"
echo    # move to a new line
read -p "I confirm that variables are correct and want to proceed (y/n)?  " -n 1 -r
echo    # move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Script was canceled."
    exit 1
fi


echo "Step1: Download msrcync"
# https://github.com/jbd/msrsync
cd ${TMP_DIR}
if [[ -s msrsync ]]; then
  echo "msrsync already downloaded"
else
  sudo su confluence -c "wget https://raw.githubusercontent.com/jbd/msrsync/master/msrsync && chmod +x msrsync"
fi

echo "Step2: Download attachments"
sudo su -c "rm -rf ${ATTACHMENTS_TAR}"
ARTIFACT_SIZE_BYTES=$(curl -sI ${ATTACHMENTS_TAR_URL} | grep "Content-Length" | awk {'print $2'} | tr -d '[:space:]')
ARTIFACT_SIZE_GB=$((${ARTIFACT_SIZE_BYTES}/1024/1024/1024))
FREE_SPACE_KB=$(df -k --output=avail "$PWD" | tail -n1)
FREE_SPACE_GB=$((${FREE_SPACE_KB}/1024/1024))
REQUIRED_SPACE_GB=$((5 + ${ARTIFACT_SIZE_GB}))
if [[ ${FREE_SPACE_GB} -lt ${REQUIRED_SPACE_GB} ]]; then
   echo "Not enough free space for download."
   echo "Free space: ${FREE_SPACE_GB} GB"
   echo "Required space: ${REQUIRED_SPACE_GB} GB"
   exit 1
fi;
sudo su confluence -c "time wget --progress=dot:giga ${ATTACHMENTS_TAR_URL}"

echo "Step3: Untar attachments to tmp folder"
sudo su -c "rm -rf ${ATTACHMENTS_DIR}"
sudo su confluence -c "time tar -xzf ${ATTACHMENTS_TAR} --checkpoint=.10000"
if [[ $? -ne 0 ]]; then
  echo "Untar failed!"
  exit 1
fi
echo "Counting total files number:"
sudo su confluence -c "find ${ATTACHMENTS_DIR} -type f -print | wc -l"
echo "Deleting ${ATTACHMENTS_TAR}"
sudo su -c "rm -rf ${ATTACHMENTS_TAR}"

echo "Step4: Copy attachments to EFS"
sudo su confluence -c "time ./msrsync -P -p 100 -f 3000 ${ATTACHMENTS_DIR} ${EFS_DIR}"
sudo su -c "rm -rf ${ATTACHMENTS_DIR}"

echo "Finished"
echo  # move to a new line