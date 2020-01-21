#!/bin/bash

###################    Variables section         ###################
# Command to install psql client for Amazon Linux 2.
# In case of different distributive, please adjust accordingly or install manually.
INSTALL_PSQL_CMD="amazon-linux-extras install -y postgresql10"

# DB config file location (dbconfig.xml)
DB_CONFIG="/var/atlassian/application-data/confluence/confluence.cfg.xml"

# Depending on Confluence installation directory
CONFLUENCE_CURRENT_DIR="/opt/atlassian/confluence/current"
CONFLUENCE_VERSION_FILE="/media/atl/confluence/shared-home/confluence.version"

# DB admin user name, password and DB name
CONFLUENCE_DB_NAME="confluence"
CONFLUENCE_DB_USER="postgres"
CONFLUENCE_DB_PASS="Password1!"

# Confluence version variables
SUPPORTED_CONFLUENCE_VERSIONS=(6.13.8 7.0.4)
CONFLUENCE_VERSION=$(sudo su confluence -c "cat ${CONFLUENCE_VERSION_FILE}")
echo "Confluence Version: ${CONFLUENCE_VERSION}"

# Datasets AWS bucket and db dump name
DATASETS_AWS_BUCKET="https://centaurus-datasets.s3.amazonaws.com/confluence"
DATASETS_SIZE="large"
DB_DUMP_NAME="db.dump"
DB_DUMP_URL="${DATASETS_AWS_BUCKET}/${CONFLUENCE_VERSION}/${DATASETS_SIZE}/${DB_DUMP_NAME}"

###################    End of variables section  ###################


# Check if Confluence version is supported
if [[ ! "${SUPPORTED_CONFLUENCE_VERSIONS[@]}" =~ "${CONFLUENCE_VERSION}" ]]; then
  echo "Confluence Version: ${CONFLUENCE_VERSION} is not officially supported by Data Center App Performance Toolkit."
  echo "Supported Confluence Versions: ${SUPPORTED_CONFLUENCE_VERSIONS[@]}"
  echo "If you want to force apply an existing datasets to your Confluence, use --force flag with version of dataset you want to apply:"
  echo "e.g. ./populate_db.sh --force 6.13.8"
  echo "!!! Warning !!! This may break your Confluence instance. Also, note that downgrade is not supported by Confluence."
  # Check if --force flag is passed into command
  if [[ "$1" == "--force" ]]; then
    # Check if passed Confluence version is in list of supported
    if [[ "${SUPPORTED_CONFLUENCE_VERSIONS[@]}" =~ "$2" ]]; then
      DB_DUMP_URL="${DATASETS_AWS_BUCKET}/$2/${DATASETS_SIZE}/${DB_DUMP_NAME}"
      echo "Force mode. Dataset URL: ${DB_DUMP_URL}"
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
echo # move to a new line
echo "This script restores Postgres DB from SQL DB dump for Confluence DC created with AWS Quickstart defaults."
echo "You can review or modify default variables in 'Variables section' of this script."
echo # move to a new line
echo "Variables:"
echo "CONFLUENCE_CURRENT_DIR=${CONFLUENCE_CURRENT_DIR}"
echo "DB_CONFIG=${DB_CONFIG}"
echo "CONFLUENCE_DB_NAME=${CONFLUENCE_DB_NAME}"
echo "CONFLUENCE_DB_USER=${CONFLUENCE_DB_USER}"
echo "CONFLUENCE_DB_PASS=${CONFLUENCE_DB_PASS}"
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

echo "Step2: Stop Confluence"
sudo systemctl stop confluence
if [[ $? -ne 0 ]]; then
  echo "Confluence did not stop. Please try to rerun script."
  exit 1
fi

echo "Step3: Download DB dump"
rm -rf ${DB_DUMP_NAME}
ARTIFACT_SIZE_BYTES=$(curl -sI ${DB_DUMP_URL} | grep "Content-Length" | awk {'print $2'} | tr -d '[:space:]')
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
# use computer style progress bar
time wget --progress=dot:giga ${DB_DUMP_URL}
if [[ $? -ne 0 ]]; then
  echo "DB dump download failed! Pls check available disk space."
  exit 1
fi

echo "Step4: Get DB Host"
DB_HOST=$(sudo su -c "cat ${DB_CONFIG} | grep 'jdbc:postgresql' | cut -d'/' -f3 | cut -d':' -f1")
if [[ -z ${DB_HOST} ]]; then
  echo "DataBase URL was not found in ${DB_CONFIG}"
  exit 1
fi
echo "DB_HOST=${DB_HOST}"

echo "Step5: SQL Restore"
echo "Check DB connection"
PGPASSWORD=${CONFLUENCE_DB_PASS} pg_isready -U ${CONFLUENCE_DB_USER} -h ${DB_HOST}
if [[ $? -ne 0 ]]; then
  echo "Connection to DB failed. Please check correctness of following variables:"
  echo "CONFLUENCE_DB_NAME=${CONFLUENCE_DB_NAME}"
  echo "CONFLUENCE_DB_USER=${CONFLUENCE_DB_USER}"
  echo "CONFLUENCE_DB_PASS=${CONFLUENCE_DB_PASS}"
  echo "DB_HOST=${DB_HOST}"
  exit 1
fi
echo "Drop DB"
PGPASSWORD=${CONFLUENCE_DB_PASS} dropdb -U ${CONFLUENCE_DB_USER} -h ${DB_HOST} ${CONFLUENCE_DB_NAME}
if [[ $? -ne 0 ]]; then
  echo "Drop DB failed."
  exit 1
fi
sleep 5
echo "Create DB"
PGPASSWORD=${CONFLUENCE_DB_PASS} createdb -U ${CONFLUENCE_DB_USER} -h ${DB_HOST} -T template0 ${CONFLUENCE_DB_NAME}
if [[ $? -ne 0 ]]; then
  echo "Create DB failed."
  exit 1
fi
sleep 5
echo "PG Restore"
time PGPASSWORD=${CONFLUENCE_DB_PASS} pg_restore -v -j 8 -U ${CONFLUENCE_DB_USER} -h ${DB_HOST} -d ${CONFLUENCE_DB_NAME} ${DB_DUMP_NAME}
if [[ $? -ne 0 ]]; then
  echo "SQL Restore failed!"
  exit 1
fi

echo "Step6: Start Confluence"
sudo systemctl start confluence
rm -rf ${DB_DUMP_NAME}

echo "Finished"
echo  # move to a new line

echo "Important: new admin user credentials are admin/admin"
echo "Wait a couple of minutes until Confluence is started."