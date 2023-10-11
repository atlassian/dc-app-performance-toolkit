#!/bin/bash

# Read command line arguments
while [[ "$#" -gt 0 ]]; do case $1 in
  --jsm) jsm=1 ;;
  --small) small=1 ;;
  --custom) custom=1 ;;
  --force)
   if [ -n "$2" ] && [ "${2:0:1}" != "-" ]; then
     force=1
     version=${2}
     shift
   else
     force=1
   fi
   ;;
  *) echo "Unknown parameter passed: $1"; exit 1;;
esac; shift; done

if [[ ! $(systemctl status jira) ]]; then
 echo "The Jira service was not found on this host." \
 "Please make sure you are running this script on a host that is running Jira."
 exit 1
fi

###################    Variables section         ###################
# Jira version variables
JIRA_VERSION_FILE="/media/atl/jira/shared/jira-software.version"

# Jira/JSM supported versions

SUPPORTED_JIRA_VERSIONS=(8.20.26 9.4.10)
SUPPORTED_JSM_VERSIONS=(4.20.26 5.4.10)

SUPPORTED_VERSIONS=("${SUPPORTED_JIRA_VERSIONS[@]}")
if [[ ${jsm} == 1 ]]; then
  JIRA_VERSION_FILE="/media/atl/jira/shared/jira-servicedesk.version"
  SUPPORTED_VERSIONS=("${SUPPORTED_JSM_VERSIONS[@]}")
fi
JIRA_VERSION=$(sudo su jira -c "cat ${JIRA_VERSION_FILE}")
if [[ -z "$JIRA_VERSION" ]]; then
  echo "ERROR: Failed to get Jira version. If your application type is JSM use flag '--jsm'." \
       "Otherwise check if JIRA_VERSION_FILE variable (${JIRA_VERSION_FILE})" \
       "has a valid file path of the Jira version file or set your Cluster JIRA_VERSION explicitly."
  exit 1
fi
echo "Jira Version: ${JIRA_VERSION}"

DATASETS_AWS_BUCKET="https://centaurus-datasets.s3.amazonaws.com/jira"
if [[ ${jsm} == 1 ]]; then
  DATASETS_AWS_BUCKET="https://centaurus-datasets.s3.amazonaws.com/jsm"
fi
ATTACHMENTS_TAR="attachments.tar.gz"
ATTACHMENTS_DIR="attachments"
AVATARS_DIR="avatars"
DATASETS_SIZE="large"
if [[ ${jsm} == 1 && ${small} == 1 ]]; then
  # Only JSM supports "small" dataset
  DATASETS_SIZE="small"
fi
ATTACHMENTS_TAR_URL="${DATASETS_AWS_BUCKET}/${JIRA_VERSION}/${DATASETS_SIZE}/${ATTACHMENTS_TAR}"
TMP_DIR="/tmp"
EFS_DIR="/media/atl/jira/shared/data"
###################    End of variables section  ###################

# Custom version check
if [[ ${custom} == 1 ]]; then
  ATTACHMENTS_TAR_URL="${DATASETS_AWS_BUCKET}/$JIRA_VERSION/${DATASETS_SIZE}/${ATTACHMENTS_TAR}"
  if curl --output /dev/null --silent --head --fail "$ATTACHMENTS_TAR_URL"; then
    echo "Custom version $JIRA_VERSION dataset URL found: ${ATTACHMENTS_TAR_URL}"
  else
    echo "Error: there is no dataset for version $JIRA_VERSION"
    exit 1
  fi
# Check if Jira version is supported
elif [[ ! "${SUPPORTED_VERSIONS[*]}" =~ ${JIRA_VERSION} ]]; then
  echo "Jira Version: ${JIRA_VERSION} is not officially supported by Data Center App Performance Toolkit."
  echo "Supported Jira Versions: ${SUPPORTED_VERSIONS[*]}"
  echo "If you want to force apply an existing datasets to your Jira, use --force flag with version of dataset you want to apply:"
  echo "e.g. ./upload_attachments --force 8.5.0"
  echo "!!! Warning !!! This may broke your Jira instance."
  # Check if --force flag is passed into command
  if [[ ${force} == 1 ]]; then
    # Check if passed Jira version is in list of supported
    if [[ "${SUPPORTED_VERSIONS[*]}" =~ ${version} ]]; then
      ATTACHMENTS_TAR_URL="${DATASETS_AWS_BUCKET}/${version}/${DATASETS_SIZE}/${ATTACHMENTS_TAR}"
      echo "Force mode. Dataset URL: ${ATTACHMENTS_TAR_URL}"
    else
      LAST_DATASET_VERSION=${SUPPORTED_VERSIONS[${#SUPPORTED_VERSIONS[@]}-1]}
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
echo "This script restores attachments into Jira DC created with AWS Quickstart defaults."
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
cd ${TMP_DIR} || exit 1
if [[ -s msrsync ]]; then
  echo "msrsync already downloaded"
else
  sudo su jira -c "wget https://raw.githubusercontent.com/jbd/msrsync/master/msrsync && chmod +x msrsync"
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
sudo su jira -c "time wget --progress=dot:giga ${ATTACHMENTS_TAR_URL}"

echo "Step3: Untar attachments to tmp folder"
sudo su -c "rm -rf ${ATTACHMENTS_DIR}"
sudo su jira -c "tar -xzf ${ATTACHMENTS_TAR} --checkpoint=.10000"
if [[ $? -ne 0 ]]; then
  echo "Untar failed!"
  exit 1
fi
echo "Counting total files number:"
sudo su jira -c "find ${ATTACHMENTS_DIR} -type f -print | wc -l"
echo "Deleting ${ATTACHMENTS_TAR}"
sudo su -c "rm -rf ${ATTACHMENTS_TAR}"

echo "Step4: Copy attachments to EFS"
sudo su jira -c "time ./msrsync -P -p 100 -f 3000 ${ATTACHMENTS_DIR} ${EFS_DIR}"
sudo su -c "rm -rf ${ATTACHMENTS_DIR}"

if [[ ${jsm} == 1 ]]; then
  echo "Step5: Copy avatars to EFS"
  sudo su jira -c "time ./msrsync -P -p 100 -f 3000 ${AVATARS_DIR} ${EFS_DIR}"
  sudo su -c "rm -rf ${AVATARS_DIR}"
fi

echo "DCAPT util script execution is finished successfully."
echo  # move to a new line