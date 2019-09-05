#!/bin/bash


###################    Variables section         ###################
DATASETS_AWS_BUCKET="https://centaurus-datasets.s3.amazonaws.com/jira/8.0.3/large"
ATTACHMENTS_TAR="attachments.tar.gz"
ATTACHMENTS_DIR="attachments"
TMP_DIR="/tmp"
EFS_DIR="/media/atl/jira/shared/data"
###################    End of variables section  ###################


echo "!!! Warning !!!"
echo    # move to a new line
echo "This script restores attachments into Jira DC created with AWS Quickstart defaults."
echo "You can review or modify default variables in 'Variables section' of this script."
echo    # move to a new line
echo "Variables:"
echo "EFS_DIR=${EFS_DIR}"
echo "ATTACHMENTS_TAR_URL=${DATASETS_AWS_BUCKET}/${ATTACHMENTS_TAR}"
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
  sudo su jira -c "wget https://raw.githubusercontent.com/jbd/msrsync/master/msrsync && chmod +x msrsync"
fi

echo "Step2: Download attachments"
sudo su -c "rm -rf ${ATTACHMENTS_TAR}"
sudo su jira -c "wget ${DATASETS_AWS_BUCKET}/${ATTACHMENTS_TAR}"

echo "Step3: Untar attachments to tmp folder"
sudo su -c "rm -rf ${ATTACHMENTS_DIR}"
sudo su jira -c "tar -xzvf ${ATTACHMENTS_TAR}"
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