#!/bin/bash

###################    Variables section         ###################
# Command to install psql client for Amazon Linux 2.
# In case of different distributive, please adjust accordingly or install manually.
INSTALL_PSQL_CMD="amazon-linux-extras install -y postgresql11"

# DB config file location (dbconfig.xml)
DB_CONFIG="/usr/lib/systemd/system/crowd.service"

# Depending on Crowd installation directory
CROWD_VERSION_FILE="/media/atl/crowd/shared/crowd.version"

# DB admin user name, password and DB name
CROWD_DB_NAME="crowd"
CROWD_DB_USER="postgres"
CROWD_DB_PASS="Password1!"

# Crowd version variables
SUPPORTED_CROWD_VERSIONS=(4.3.0)

if [[ ! $(systemctl status crowd) ]]; then
  echo "The Crowd service was not found on this host." \
  "Please make sure you are running this script on a host that is running Crowd."
  exit 1
fi

CROWD_VERSION=$(sudo su crowd -c "cat ${CROWD_VERSION_FILE}")
if [[ -z "$CROWD_VERSION" ]]; then
  echo The $CROWD_VERSION_FILE file does not exists or emtpy. Please check if CROWD_VERSION_FILE variable \
  has a valid file path of the Crowd version file or set your Cluster CROWD_VERSION explicitly.
  exit 1
fi
echo "Crowd Version: ${CROWD_VERSION}"

# Datasets AWS bucket and db dump name
DATASETS_AWS_BUCKET="https://centaurus-datasets.s3.amazonaws.com/crowd"
DATASETS_SIZE="large"
DB_DUMP_NAME="db.dump"

###################    End of variables section  ###################

# Check if Crowd version is supported
if [[ ! "${SUPPORTED_CROWD_VERSIONS[*]}" =~ ${CROWD_VERSION} ]]; then
  echo "Crowd Version: ${CROWD_VERSION} is not officially supported by Data Center App Performance Toolkit."
  echo "Supported Crowd Versions: ${SUPPORTED_CROWD_VERSIONS[*]}"
  echo "!!! Warning !!! Dump from version ${SUPPORTED_CROWD_VERSIONS[0]} would be used"
fi

DB_DUMP_URL="${DATASETS_AWS_BUCKET}/${SUPPORTED_CROWD_VERSIONS[0]}/${DATASETS_SIZE}/${DB_DUMP_NAME}"

echo "!!! Warning !!!"
echo # move to a new line
echo "This script restores Postgres DB from SQL DB dump for Сrowd DC created with AWS Quickstart defaults."
echo "You can review or modify default variables in 'Variables section' of this script."
echo # move to a new line
echo "Variables:"
echo "DB_CONFIG=${DB_CONFIG}"
echo "CROWD_DB_NAME=${CROWD_DB_NAME}"
echo "CROWD_DB_USER=${CROWD_DB_USER}"
echo "CROWD_DB_PASS=${CROWD_DB_PASS}"
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
echo "Current PostgreSQL version is $(psql -V)"

echo "Step2: Get DB Host and check DB connection"
DB_HOST=$(sudo su -c "cat ${DB_CONFIG} | grep 'jdbc:postgresql' | cut -d'/' -f3 | cut -d':' -f1")
if [[ -z ${DB_HOST} ]]; then
  echo "DataBase URL was not found in ${DB_CONFIG}"
  exit 1
fi
echo "DB_HOST=${DB_HOST}"

echo "Check DB connection"
PGPASSWORD=${CROWD_DB_PASS} pg_isready -U ${CROWD_DB_USER} -h ${DB_HOST}
if [[ $? -ne 0 ]]; then
  echo "Connection to DB failed. Please check correctness of following variables:"
  echo "CROWD_DB_NAME=${CROWD_DB_NAME}"
  echo "CROWD_DB_USER=${CROWD_DB_USER}"
  echo "CROWD_DB_PASS=${CROWD_DB_PASS}"
  echo "DB_HOST=${DB_HOST}"
  exit 1
fi

echo "Step3: Stop Crowd"
sudo systemctl stop crowd
if [[ $? -ne 0 ]]; then
  echo "Crowd did not stop. Please try to rerun script."
  exit 1
fi

echo "Step4: Download DB dump"
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
fi
# use computer style progress bar
time wget --progress=dot:giga ${DB_DUMP_URL}
if [[ $? -ne 0 ]]; then
  echo "DB dump download failed! Pls check available disk space."
  exit 1
fi

echo "Step5: SQL Restore"
echo "Drop DB"
PGPASSWORD=${CROWD_DB_PASS} dropdb -U ${CROWD_DB_USER} -h ${DB_HOST} ${CROWD_DB_NAME}
if [[ $? -ne 0 ]]; then
  echo "Drop DB failed."
  exit 1
fi
sleep 5
echo "Create DB"
PGPASSWORD=${CROWD_DB_PASS} createdb -U ${CROWD_DB_USER} -h ${DB_HOST} -T template0 ${CROWD_DB_NAME}
if [[ $? -ne 0 ]]; then
  echo "Create DB failed."
  exit 1
fi
sleep 5
echo "PG Restore"
time PGPASSWORD=${CROWD_DB_PASS} pg_restore --schema=public -v -j 8 -U ${CROWD_DB_USER} -h ${DB_HOST} -d ${CROWD_DB_NAME} ${DB_DUMP_NAME}
if [[ $? -ne 0 ]]; then
  echo "SQL Restore failed!"
  exit 1
fi

echo "Step6: Start Crowd"
sudo systemctl start crowd
rm -rf ${DB_DUMP_NAME}

echo "DCAPT util script execution is finished successfully."
echo  # move to a new line

echo "Important: new admin user credentials are admin/admin"
echo "Wait a couple of minutes until Crowd is started."
