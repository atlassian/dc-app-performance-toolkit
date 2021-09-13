#!/bin/bash

###################    Check if NFS exists        ###################
pgrep nfsd > /dev/null && echo "NFS found" || { echo NFS process was not found. This script is intended to run only on the Bitbucket NFS Server machine. && exit 1; }

###################    Variables section         ###################
# Bitbucket version variables
BITBUCKET_VERSION_FILE="/media/atl/bitbucket/shared/bitbucket.version"
SUPPORTED_BITBUCKET_VERSIONS=(6.10.11 7.0.5 7.6.7)
BITBUCKET_VERSION=$(sudo su bitbucket -c "cat ${BITBUCKET_VERSION_FILE}")
if [[ -z "$BITBUCKET_VERSION" ]]; then
        echo The $BITBUCKET_VERSION_FILE file does not exists or emtpy. Please check if BITBUCKET_VERSION_FILE variable \
         has a valid file path of the Bitbucket version file or set your Cluster BITBUCKET_VERSION explicitly.
        exit 1
fi
echo "Bitbucket Version: ${BITBUCKET_VERSION}"

DATASETS_AWS_BUCKET="https://centaurus-datasets.s3.amazonaws.com/bitbucket"
ATTACHMENTS_TAR="attachments.tar.gz"
DATASETS_SIZE="large"
ATTACHMENTS_TAR_URL="${DATASETS_AWS_BUCKET}/${BITBUCKET_VERSION}/${DATASETS_SIZE}/${ATTACHMENTS_TAR}"
NFS_DIR="/media/atl/bitbucket/shared"
ATTACHMENT_DIR_DATA="data"
###################    End of variables section  ###################

# Check if Bitbucket version is supported
if [[ ! "${SUPPORTED_BITBUCKET_VERSIONS[*]}" =~ ${BITBUCKET_VERSION} ]]; then
  echo "Bitbucket Version: ${BITBUCKET_VERSION} is not officially supported by Data Center App Peformance Toolkit."
  echo "Supported Bitbucket Versions: ${SUPPORTED_BITBUCKET_VERSIONS[*]}"
  echo "If you want to force apply an existing datasets to your BITBUCKET, use --force flag with version of dataset you want to apply:"
  echo "e.g. ./upload_attachments --force 6.10.0"
  echo "!!! Warning !!! This may broke your Bitbucket instance."
  # Check if --force flag is passed into command
  if [[ "$1" == "--force" ]]; then
    # Check if passed Bitbucket version is in list of supported
    if [[ "${SUPPORTED_BITBUCKET_VERSIONS[*]}" =~ ${2} ]]; then
      ATTACHMENTS_TAR_URL="${DATASETS_AWS_BUCKET}/$2/${DATASETS_SIZE}/${ATTACHMENTS_TAR}"
      echo "Force mode. Dataset URL: ${ATTACHMENTS_TAR_URL}"
    else
      LAST_DATASET_VERSION=${SUPPORTED_BITBUCKET_VERSIONS[${#SUPPORTED_BITBUCKET_VERSIONS[@]}-1]}
      ATTACHMENTS_TAR_URL="${DATASETS_AWS_BUCKET}/$LAST_DATASET_VERSION/${DATASETS_SIZE}/${ATTACHMENTS_TAR}"
      echo "Specific dataset version was not specified after --force flag, using the last available: ${LAST_DATASET_VERSION}"
      echo "Dataset URL: ${ATTACHMENTS_TAR_URL}"
    fi
  else
    # No force flag
    exit 1
  fi
fi

echo "!!! Warning !!!"
echo    # move to a new line
echo "This script restores attachments into Bitbucket DC created with AWS Quickstart defaults."
echo "You can review or modify default variables in 'Variables section' of this script."
echo    # move to a new line
echo "Variables:"
echo "NFS_DIR=${NFS_DIR}"
echo "ATTACHMENTS_TAR_URL=${ATTACHMENTS_TAR_URL}"
echo    # move to a new line
read -p "I confirm that variables are correct and want to proceed (y/n)?  " -n 1 -r
echo    # move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Script was canceled."
    exit 1
fi


echo "Step1: Download and untar attachments"
sudo su -c "rm -rf ${ATTACHMENTS_TAR}"
ARTIFACT_SIZE_BYTES=$(curl -sI ${ATTACHMENTS_TAR_URL} | grep "Content-Length" | awk {'print $2'} | tr -d '[:space:]')
ARTIFACT_SIZE_GB=$((${ARTIFACT_SIZE_BYTES}/1024/1024/1024))
FREE_SPACE_KB=$(sudo su bitbucket -c "df -k --output=avail $NFS_DIR | tail -n1")
FREE_SPACE_GB=$((${FREE_SPACE_KB}/1024/1024))
REQUIRED_SPACE_GB=$((5 + ${ARTIFACT_SIZE_GB}))
if [[ ${FREE_SPACE_GB} -lt ${REQUIRED_SPACE_GB} ]]; then
   echo "Not enough free space for download."
   echo "Free space: ${FREE_SPACE_GB} GB"
   echo "Required space: ${REQUIRED_SPACE_GB} GB"
   exit 1
fi;

sudo su -c "time wget -qO- ${ATTACHMENTS_TAR_URL} -P ${NFS_DIR} | tar -xz --checkpoint=.10000 -C ${NFS_DIR}/${ATTACHMENT_DIR_DATA} --strip-components 1"
if [[ $? -ne 0 ]]; then
  echo "Untar failed!"
  exit 1
fi
echo "DCAPT util script execution is finished successfully."
echo "Important: do not forget to start Bitbucket"
echo  # move to a new line