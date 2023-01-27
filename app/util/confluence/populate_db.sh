#!/bin/bash

###################    Variables section         ###################
# Command to install psql client for Amazon Linux 2.
# In case of different distributive, please adjust accordingly or install manually.
INSTALL_PSQL_CMD="amazon-linux-extras install -y postgresql10"

# DB config file location (dbconfig.xml)
DB_CONFIG="/var/atlassian/application-data/confluence/confluence.cfg.xml"

# Depending on Confluence installation directory
CONFLUENCE_VERSION_FILE="/media/atl/confluence/shared-home/confluence.version"

# DB admin user name, password and DB name
CONFLUENCE_DB_NAME="confluence"
CONFLUENCE_DB_USER="postgres"
CONFLUENCE_DB_PASS="Password1!"

# Confluence DB requests
SELECT_CONFLUENCE_SETTING_SQL="select BANDANAVALUE from BANDANA where BANDANACONTEXT = '_GLOBAL' and BANDANAKEY = 'atlassian.confluence.settings';"

# Confluence version variables
SUPPORTED_CONFLUENCE_VERSIONS=(7.13.7 7.19.2 8.0.0)

if [[ ! $(systemctl status confluence) ]]; then
  echo "The Confluence service was not found on this host." \
  "Please make sure you are running this script on a host that is running Confluence."
  exit 1
fi

CONFLUENCE_VERSION=$(sudo su confluence -c "cat ${CONFLUENCE_VERSION_FILE}")
if [[ -z "$CONFLUENCE_VERSION" ]]; then
  echo The $CONFLUENCE_VERSION_FILE file does not exists or emtpy. Please check if CONFLUENCE_VERSION_FILE variable \
  has a valid file path of the Confluence version file or set your Cluster CONFLUENCE_VERSION explicitly.
  exit 1
fi
echo "Confluence Version: ${CONFLUENCE_VERSION}"

# Datasets AWS bucket and db dump name
DATASETS_AWS_BUCKET="https://centaurus-datasets.s3.amazonaws.com/confluence"
DATASETS_SIZE="large"
DB_DUMP_NAME="db.dump"
DB_DUMP_URL="${DATASETS_AWS_BUCKET}/${CONFLUENCE_VERSION}/${DATASETS_SIZE}/${DB_DUMP_NAME}"

###################    End of variables section  ###################

# Custom version check
if [[ "$1" == "--custom" ]]; then
  DB_DUMP_URL="${DATASETS_AWS_BUCKET}/$CONFLUENCE_VERSION/${DATASETS_SIZE}/${DB_DUMP_NAME}"
  if curl --output /dev/null --silent --head --fail "$DB_DUMP_URL"; then
    echo "Custom version $CONFLUENCE_VERSION dataset URL found: ${DB_DUMP_URL}"
  else
    echo "Error: there is no dataset for version $CONFLUENCE_VERSION"
    exit 1
  fi
# Check if Confluence version is supported
elif [[ ! "${SUPPORTED_CONFLUENCE_VERSIONS[*]}" =~ ${CONFLUENCE_VERSION} ]]; then
  echo "Confluence Version: ${CONFLUENCE_VERSION} is not officially supported by Data Center App Performance Toolkit."
  echo "Supported Confluence Versions: ${SUPPORTED_CONFLUENCE_VERSIONS[*]}"
  echo "If you want to force apply an existing datasets to your Confluence, use --force flag with version of dataset you want to apply:"
  echo "e.g. ./populate_db.sh --force 7.4.5"
  echo "!!! Warning !!! This may break your Confluence instance. Also, note that downgrade is not supported by Confluence."
  # Check if --force flag is passed into command
  if [[ "$1" == "--force" ]]; then
    # Check if version was specified after --force flag
    if [[ -z "$2" ]]; then
      echo "Error: --force flag requires version after it."
      echo "Specify one of these versions: ${SUPPORTED_CONFLUENCE_VERSIONS[*]}"
      exit 1
    fi
    # Check if passed Confluence version is in list of supported
    if [[ " ${SUPPORTED_CONFLUENCE_VERSIONS[@]} " =~ " ${2} " ]]; then
      DB_DUMP_URL="${DATASETS_AWS_BUCKET}/$2/${DATASETS_SIZE}/${DB_DUMP_NAME}"
      echo "Force mode. Dataset URL: ${DB_DUMP_URL}"
    else
      LAST_DATASET_VERSION=${SUPPORTED_CONFLUENCE_VERSIONS[${#SUPPORTED_CONFLUENCE_VERSIONS[@]}-1]}
      DB_DUMP_URL="${DATASETS_AWS_BUCKET}/$LAST_DATASET_VERSION/${DATASETS_SIZE}/${DB_DUMP_NAME}"
      echo "Specific dataset version was not specified after --force flag, using the last available: ${LAST_DATASET_VERSION}"
      echo "Dataset URL: ${DB_DUMP_URL}"
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
echo "Current PostgreSQL version is $(psql -V)"

echo "Step2: Get DB Host, check DB connection and user permissions"
DB_HOST=$(sudo su -c "cat ${DB_CONFIG} | grep 'jdbc:postgresql' | cut -d'/' -f3 | cut -d':' -f1")
if [[ -z ${DB_HOST} ]]; then
  echo "DataBase URL was not found in ${DB_CONFIG}"
  exit 1
fi
echo "DB_HOST=${DB_HOST}"

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

echo "Check database permissions for user ${CONFLUENCE_DB_USER}"
PGPASSWORD=${CONFLUENCE_DB_PASS} createdb -U ${CONFLUENCE_DB_USER} -h ${DB_HOST} -T template0 -E "UNICODE" -l "C" TEST
if [[ $? -ne 0 ]]; then
  echo "User ${CONFLUENCE_DB_USER} doesn't have permission to create database."
  exit 1
else
  PGPASSWORD=${CONFLUENCE_DB_PASS} dropdb -U ${CONFLUENCE_DB_USER} -h ${DB_HOST} TEST
fi

echo "Step3: Write confluence baseUrl to file"
CONFLUENCE_BASE_URL_FILE="base_url"
if [[ -s ${CONFLUENCE_BASE_URL_FILE} ]];then
  echo "File ${CONFLUENCE_BASE_URL_FILE} was found. Base url: $(cat ${CONFLUENCE_BASE_URL_FILE})."
else
  PGPASSWORD=${CONFLUENCE_DB_PASS} psql -h ${DB_HOST} -d ${CONFLUENCE_DB_NAME} -U ${CONFLUENCE_DB_USER} -Atc "${SELECT_CONFLUENCE_SETTING_SQL}" \
  | grep -i "<baseurl>" > ${CONFLUENCE_BASE_URL_FILE}
  if [[ ! -s ${CONFLUENCE_BASE_URL_FILE} ]]; then
    echo "Failed to get Base URL value from database. Check DB configuration variables."
    exit 1
  fi
  echo "$(cat ${CONFLUENCE_BASE_URL_FILE}) was written to the ${CONFLUENCE_BASE_URL_FILE} file."
fi

echo "Step4: Stop Confluence"
sudo systemctl stop confluence
if [[ $? -ne 0 ]]; then
  echo "Confluence did not stop. Please try to rerun script."
  exit 1
fi

echo "Step5: Download DB dump"
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

echo "Step6: SQL Restore"
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
time PGPASSWORD=${CONFLUENCE_DB_PASS} pg_restore --schema=public -v -j 8 -U ${CONFLUENCE_DB_USER} -h ${DB_HOST} -d ${CONFLUENCE_DB_NAME} ${DB_DUMP_NAME}
if [[ $? -ne 0 ]]; then
  echo "SQL Restore failed!"
  exit 1
fi

echo "Step7: Update confluence baseUrl value in database"
BASE_URL_TO_REPLACE=$(PGPASSWORD=${CONFLUENCE_DB_PASS} psql -h ${DB_HOST} -d ${CONFLUENCE_DB_NAME} -U ${CONFLUENCE_DB_USER} -Atc \
"${SELECT_CONFLUENCE_SETTING_SQL}" | grep -i "<baseurl>")

if [[ -z "${BASE_URL_TO_REPLACE}" ]]; then
  echo "The BASE_URL_TO_REPLACE variable is empty. Please check that the confluence baseUrl value is exist in the database."
  exit 1
fi

if [[ -s ${CONFLUENCE_BASE_URL_FILE} ]]; then
  BASE_URL=$(cat ${CONFLUENCE_BASE_URL_FILE})
  if [[ $(PGPASSWORD=${CONFLUENCE_DB_PASS} psql -h ${DB_HOST} -d ${CONFLUENCE_DB_NAME} -U ${CONFLUENCE_DB_USER} -c \
    "update BANDANA
      set BANDANAVALUE = replace(BANDANAVALUE, '${BASE_URL_TO_REPLACE}', '${BASE_URL}')
      where BANDANACONTEXT = '_GLOBAL'
      and BANDANAKEY = 'atlassian.confluence.settings';") != "UPDATE 1" ]]; then
    echo "Couldn't update database baseUrl value. Please check your DB configuration variables."
    exit 1
  else
    echo "The database baseUrl value was updated with ${BASE_URL}"
  fi
else
  echo "The ${CONFLUENCE_BASE_URL_FILE} file doesn't exist or empty. Check DB configuration variables."
  exit 1
fi

echo "Step8: Start Confluence"
sudo systemctl start confluence
rm -rf ${DB_DUMP_NAME}

echo "Step9: Remove ${CONFLUENCE_BASE_URL_FILE} file"
sudo rm ${CONFLUENCE_BASE_URL_FILE}

echo "DCAPT util script execution is finished successfully."
echo  # move to a new line

echo "Important: new admin user credentials are admin/admin"
echo "Wait a couple of minutes until Confluence is started."
