#!/bin/bash

###################    Check if NFS exists        ###################
pgrep nfsd > /dev/null && echo "NFS found" || (echo "NFS process was not found. This script is intended to run only on the Bitbucket NFS Server machine."; exit 1)

###################    Variables section         ###################
# Command to install psql client for Amazon Linux 2.
# In case of different distributive, please adjust accordingly or install manually.
INSTALL_PSQL_CMD="amazon-linux-extras install -y postgresql10"

# DB config file location (dbconfig.xml)
DB_CONFIG="/media/atl/bitbucket/shared/bitbucket.properties"

# Depending on BITBUCKET installation directory
BITBUCKET_CURRENT_DIR="/opt/atlassian/bitbucket/current/"
BITBUCKET_VERSION_FILE="/media/atl/bitbucket/shared/bitbucket.version"

# DB admin user name, password and DB name
BITBUCKET_DB_NAME="bitbucket"
BITBUCKET_DB_USER="postgres"
BITBUCKET_DB_PASS="Password1!"

# BITBUCKET version variables
SUPPORTED_BITBUCKET_VERSIONS=(6.10.0 7.0.0)
BITBUCKET_VERSION=$(sudo su bitbucket -c "cat ${BITBUCKET_VERSION_FILE}")
echo "Bitbucket version: ${BITBUCKET_VERSION}"

# Datasets AWS bucket and db dump name
DATASETS_AWS_BUCKET="https://centaurus-datasets.s3.amazonaws.com/bitbucket"
DATASETS_SIZE="large"
DB_DUMP_NAME="db.dump"
DB_DUMP_URL="${DATASETS_AWS_BUCKET}/${BITBUCKET_VERSION}/${DATASETS_SIZE}/${DB_DUMP_NAME}"

###################    End of variables section  ###################


# Check if Bitbucket version is supported
if [[ ! "${SUPPORTED_BITBUCKET_VERSIONS[@]}" =~ "${BITBUCKET_VERSION}" ]]; then
  echo "Bitbucket Version: ${BITBUCKET_VERSION} is not officially supported by Data Center App Performance Toolkit."
  echo "Supported Bitbucket Versions: ${SUPPORTED_BITBUCKET_VERSIONS[@]}"
  echo "If you want to force apply an existing datasets to your Bitbucket, use --force flag with version of dataset you want to apply:"
  echo "e.g. ./populate_db.sh --force 6.10.0"
  echo "!!! Warning !!! This may break your Bitbucket instance. Also, note that downgrade is not supported by Bitbucket."
  # Check if --force flag is passed into command
  if [[ "$1" == "--force" ]]; then
    # Check if passed Bitbucket version is in list of supported
    if [[ "${SUPPORTED_BITBUCKET_VERSIONS[@]}" =~ "$2" ]]; then
      DB_DUMP_URL="${DATASETS_AWS_BUCKET}/$2/${DATASETS_SIZE}/${DB_DUMP_NAME}"
      echo "Force mode. Dataset URL: ${DB_DUMP_URL}"
    else
      echo "Correct dataset version was not specified after --force flag."
      echo "Available datasets: ${SUPPORTED_BITBUCKET_VERSIONS[@]}"
      exit 1
    fi
  else
    # No force flag
    exit 1
  fi
fi

echo "!!! Warning !!!"
echo # move to a new line
echo "This script restores Postgres DB from SQL DB dump for Bitbucket DC created with AWS Quickstart defaults."
echo "You can review or modify default variables in 'Variables section' of this script."
echo # move to a new line
echo "Variables:"
echo "BITBUCKET_CURRENT_DIR=${BITBUCKET_CURRENT_DIR}"
echo "DB_CONFIG=${DB_CONFIG}"
echo "BITBUCKET_DB_NAME=${BITBUCKET_DB_NAME}"
echo "BITBUCKET_DB_USER=${BITBUCKET_DB_USER}"
echo "BITBUCKET_DB_PASS=${BITBUCKET_DB_PASS}"
echo "DB_DUMP_URL=${DB_DUMP_URL}"
echo # move to a new line
read -p "I confirm that variables are correct and want to proceed (y/n)?  " -n 1 -r
echo # move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Script was canceled."
  exit 1
fi

echo "Step1: Check Postgres Client"
if ! [[ -x "$(command -v psql)" ]]; then
  echo "Install Postgres client"
  sudo su -c "${INSTALL_PSQL_CMD}"
  if [[ $? -ne 0 ]]; then
    echo "Postgres Client was NOT installed."
    echo "Check correctness of install command or install Postgres client manually."
    echo "INSTALL_PSQL_CMD=${INSTALL_PSQL_CMD}"
    exit 1
  fi
else
  echo "Postgres client is already installed"
fi

echo "Step2: Download DB dump"
DUMP_DIR='/media/atl/bitbucket/shared'
if [[ $? -ne 0 ]]; then
    echo "Directory ${DUMP_DIR} does not exist"
    exit 1
fi
sudo su -c "rm -rf ${DUMP_DIR}/${DB_DUMP_NAME}"
ARTIFACT_SIZE_BYTES=$(curl -sI ${DB_DUMP_URL} | grep "Content-Length" | awk {'print $2'} | tr -d '[:space:]')
ARTIFACT_SIZE_GB=$((${ARTIFACT_SIZE_BYTES}/1024/1024/1024))
FREE_SPACE_KB=$(sudo su bitbucket -c "df -k --output=avail $DUMP_DIR | tail -n1")
FREE_SPACE_GB=$((${FREE_SPACE_KB}/1024/1024))
REQUIRED_SPACE_GB=$((5 + ${ARTIFACT_SIZE_GB}))
if [[ ${FREE_SPACE_GB} -lt ${REQUIRED_SPACE_GB} ]]; then
   echo "Not enough free space for download."
   echo "Free space: ${FREE_SPACE_GB} GB"
   echo "Required space: ${REQUIRED_SPACE_GB} GB"
   exit 1
fi;
# use computer style progress bar
sudo su bitbucket -c "time wget --progress=dot:giga ${DB_DUMP_URL} -P ${DUMP_DIR}"
if [[ $? -ne 0 ]]; then
  echo "DB dump download failed! Pls check available disk space."
  exit 1
fi

echo "Step3: Get DB Host"
DB_HOST=$(sudo su -c "cat ${DB_CONFIG} | grep 'jdbc:postgresql' | cut -d'/' -f3 | cut -d':' -f1")
if [[ -z ${DB_HOST} ]]; then
  echo "DataBase URL was not found in ${DB_CONFIG}"
  exit 1
fi
echo "DB_HOST=${DB_HOST}"

echo "Step4: SQL Restore"
echo "Check DB connection"
PGPASSWORD=${BITBUCKET_DB_PASS} pg_isready -U ${BITBUCKET_DB_USER} -h ${DB_HOST}
if [[ $? -ne 0 ]]; then
  echo "Connection to DB failed. Please check correctness of following variables:"
  echo "BITBUCKET_DB_NAME=${BITBUCKET_DB_NAME}"
  echo "BITBUCKET_DB_USER=${BITBUCKET_DB_USER}"
  echo "BITBUCKET_DB_PASS=${BITBUCKET_DB_PASS}"
  echo "DB_HOST=${DB_HOST}"
  exit 1
fi
echo "Drop DB"
sudo su -c "PGPASSWORD=${BITBUCKET_DB_PASS} dropdb -U ${BITBUCKET_DB_USER} -h ${DB_HOST} ${BITBUCKET_DB_NAME}"
if [[ $? -ne 0 ]]; then
  echo "Drop DB failed. Please make sure you stop Bitbucket."
  exit 1
fi
sleep 5
echo "Create DB"
sudo su -c "PGPASSWORD=${BITBUCKET_DB_PASS} createdb -U ${BITBUCKET_DB_USER} -h ${DB_HOST} -T template0 ${BITBUCKET_DB_NAME}"
if [[ $? -ne 0 ]]; then
  echo "Create DB failed."
  exit 1
fi
sleep 5
echo "PG Restore"
sudo su -c "time PGPASSWORD=${BITBUCKET_DB_PASS} pg_restore -v -j 8 -U ${BITBUCKET_DB_USER} -h ${DB_HOST} -d ${BITBUCKET_DB_NAME} ${DUMP_DIR}/${DB_DUMP_NAME}"
if [[ $? -ne 0 ]]; then
  echo "SQL Restore failed!"
  exit 1
fi
sudo su -c "rm -rf ${DUMP_DIR}/${DB_DUMP_NAME}"

echo "Finished"
echo  # move to a new line

echo "Important: new admin user credentials are admin/admin"
echo "Important: do not start Bitbucket until attachments restore is finished"


