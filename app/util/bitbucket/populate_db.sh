#!/bin/bash

###################    Check if NFS exists        ###################
pgrep nfsd > /dev/null && echo "NFS found" || { echo NFS process was not found. This script is intended to run only on the Bitbucket NFS Server machine. && exit 1; }

# Read command line arguments
while [[ "$#" -gt 0 ]]; do case $1 in
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

###################    Variables section         ###################
# Command to install psql client for Amazon Linux 2.
# In case of different distributive, please adjust accordingly or install manually.
INSTALL_PSQL_CMD="amazon-linux-extras install -y postgresql11"

# DB config file location (dbconfig.xml)
DB_CONFIG="/media/atl/bitbucket/shared/bitbucket.properties"

# Depending on BITBUCKET installation directory
BITBUCKET_VERSION_FILE="/media/atl/bitbucket/shared/bitbucket.version"

# DB admin user name, password and DB name
BITBUCKET_DB_NAME="bitbucket"
BITBUCKET_DB_USER="postgres"
BITBUCKET_DB_PASS="Password1!"

# Bitbucket DC has auto PRs decline feature enabled by default from 7.7.X version
BITBUCKET_AUTO_DECLINE_VERSION="7.7.0"

# BITBUCKET version variables
SUPPORTED_BITBUCKET_VERSIONS=(7.17.11 7.21.5 8.0.4)

BITBUCKET_VERSION=$(sudo su bitbucket -c "cat ${BITBUCKET_VERSION_FILE}")
if [[ -z "$BITBUCKET_VERSION" ]]; then
  echo The $BITBUCKET_VERSION_FILE file does not exists or emtpy. Please check if BITBUCKET_VERSION_FILE variable \
  has a valid file path of the Bitbucket version file or set your Cluster BITBUCKET_VERSION explicitly.
  exit 1
fi
echo "Bitbucket version: ${BITBUCKET_VERSION}"

# Datasets AWS bucket and db dump name

DATASETS_SIZE="large"
if [[ ${small} == 1 ]]; then
  DATASETS_SIZE="small"
fi
DATASETS_AWS_BUCKET="https://centaurus-datasets.s3.amazonaws.com/bitbucket"
DB_DUMP_NAME="db.dump"
DB_DUMP_URL="${DATASETS_AWS_BUCKET}/${BITBUCKET_VERSION}/${DATASETS_SIZE}/${DB_DUMP_NAME}"

###################    End of variables section  ###################

# Custom version check
if [[ ${custom} == 1 ]]; then
  DB_DUMP_URL="${DATASETS_AWS_BUCKET}/$BITBUCKET_VERSION/${DATASETS_SIZE}/${DB_DUMP_NAME}"
  if curl --output /dev/null --silent --head --fail "$DB_DUMP_URL"; then
    echo "Custom version $BITBUCKET_VERSION dataset URL found: ${DB_DUMP_URL}"
  else
    echo "Error: there is no dataset for version $BITBUCKET_VERSION"
    exit 1
  fi
# Check if Bitbucket version is supported
elif [[ ! "${SUPPORTED_BITBUCKET_VERSIONS[*]}" =~ ${BITBUCKET_VERSION} ]]; then
  echo "Bitbucket Version: ${BITBUCKET_VERSION} is not officially supported by Data Center App Performance Toolkit."
  echo "Supported Bitbucket Versions: ${SUPPORTED_BITBUCKET_VERSIONS[*]}"
  echo "If you want to force apply an existing datasets to your Bitbucket, use --force flag with version of dataset you want to apply:"
  echo "e.g. ./populate_db.sh --force 6.10.0"
  echo "!!! Warning !!! This may break your Bitbucket instance. Also, note that downgrade is not supported by Bitbucket."
  # Check if --force flag is passed into command
  if [[ ${force} == 1 ]]; then
    # Check if version was specified after --force flag
    if [[ -z ${version} ]]; then
      echo "Error: --force flag requires version after it."
      echo "Specify one of these versions: ${SUPPORTED_BITBUCKET_VERSIONS[*]}"
      exit 1
    fi
    # Check if passed Bitbucket version is in list of supported
    if [[ " ${SUPPORTED_BITBUCKET_VERSIONS[@]} " =~ " ${version} " ]]; then
      DB_DUMP_URL="${DATASETS_AWS_BUCKET}/${version}/${DATASETS_SIZE}/${DB_DUMP_NAME}"
      echo "Force mode. Dataset URL: ${DB_DUMP_URL}"
    else
      LAST_DATASET_VERSION=${SUPPORTED_BITBUCKET_VERSIONS[${#SUPPORTED_BITBUCKET_VERSIONS[@]}-1]}
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
echo "This script restores Postgres DB from SQL DB dump for Bitbucket DC created with AWS Quickstart defaults."
echo "You can review or modify default variables in 'Variables section' of this script."
echo # move to a new line
echo "Variables:"
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
echo "Current PostgreSQL version is $(psql -V)"

echo "Step2: Get DB Host, check DB connection and permissions"
DB_HOST=$(sudo su -c "cat ${DB_CONFIG} | grep 'jdbc:postgresql' | cut -d'/' -f3 | cut -d':' -f1")
if [[ -z ${DB_HOST} ]]; then
  echo "DataBase URL was not found in ${DB_CONFIG}"
  exit 1
fi
echo "DB_HOST=${DB_HOST}"

echo "Check database permissions for user ${BITBUCKET_DB_USER}"
PGPASSWORD=${BITBUCKET_DB_PASS} createdb -U ${BITBUCKET_DB_USER} -h ${DB_HOST} -T template0 -E "UNICODE" -l "C" TEST
if [[ $? -ne 0 ]]; then
  echo "User ${BITBUCKET_DB_USER} doesn't have permission to create database."
  exit 1
else
  PGPASSWORD=${BITBUCKET_DB_PASS} dropdb -U ${BITBUCKET_DB_USER} -h ${DB_HOST} TEST
fi

PGPASSWORD=${BITBUCKET_DB_PASS} pg_isready -U ${BITBUCKET_DB_USER} -h ${DB_HOST}
if [[ $? -ne 0 ]]; then
  echo "Connection to DB failed. Please check correctness of following variables:"
  echo "BITBUCKET_DB_NAME=${BITBUCKET_DB_NAME}"
  echo "BITBUCKET_DB_USER=${BITBUCKET_DB_USER}"
  echo "BITBUCKET_DB_PASS=${BITBUCKET_DB_PASS}"
  echo "DB_HOST=${DB_HOST}"
  exit 1
fi

echo "Step3: Write 'instance.url' property to file"
BITBUCKET_BASE_URL_FILE="base_url"
if [[ -s ${BITBUCKET_BASE_URL_FILE} ]]; then
  echo "File ${BITBUCKET_BASE_URL_FILE} was found. Base url: $(cat ${BITBUCKET_BASE_URL_FILE})."
else
  PGPASSWORD=${BITBUCKET_DB_PASS} psql -h ${DB_HOST} -d ${BITBUCKET_DB_NAME} -U ${BITBUCKET_DB_USER} -Atc \
  "select prop_value from app_property where prop_key='instance.url';" > ${BITBUCKET_BASE_URL_FILE}
  if [[ ! -s ${BITBUCKET_BASE_URL_FILE} ]]; then
    echo "Failed to get Base URL value from database. Check DB configuration variables."
    exit 1
  fi
  echo "$(cat ${BITBUCKET_BASE_URL_FILE}) was written to the ${BITBUCKET_BASE_URL_FILE} file."
fi

echo "Step4: Write license to file"
BITBUCKET_LICENSE_FILE="license"
if [[ -s ${BITBUCKET_LICENSE_FILE} ]]; then
  echo "File ${BITBUCKET_LICENSE_FILE} was found. License: $(cat ${BITBUCKET_LICENSE_FILE})."
else
  PGPASSWORD=${BITBUCKET_DB_PASS} psql -h ${DB_HOST} -d ${BITBUCKET_DB_NAME} -U ${BITBUCKET_DB_USER} -tAc \
  "select prop_value from app_property where prop_key = 'license';" | sed "s/\r//g" > ${BITBUCKET_LICENSE_FILE}
  if [[ ! -s ${BITBUCKET_LICENSE_FILE} ]]; then
    echo "Failed to get bitbucket license from database. Check DB configuration variables."
    exit 1
  fi
  echo "$(cat ${BITBUCKET_LICENSE_FILE}) was written to the ${BITBUCKET_LICENSE_FILE} file."
fi

echo "Step5: Download DB dump"
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

echo "Step6: SQL Restore"
echo "Check DB connection"
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
sudo su -c "time PGPASSWORD=${BITBUCKET_DB_PASS} pg_restore --schema=public -v -j 8 -U ${BITBUCKET_DB_USER} -h ${DB_HOST} -d ${BITBUCKET_DB_NAME} ${DUMP_DIR}/${DB_DUMP_NAME}"
if [[ $? -ne 0 ]]; then
  echo "SQL Restore failed!"
  exit 1
fi
sudo su -c "rm -rf ${DUMP_DIR}/${DB_DUMP_NAME}"

echo "Step7: Update 'instance.url' property in database"
if [[ -s ${BITBUCKET_BASE_URL_FILE} ]]; then
  BASE_URL=$(cat ${BITBUCKET_BASE_URL_FILE})
  if [[ $(PGPASSWORD=${BITBUCKET_DB_PASS} psql -h ${DB_HOST} -d ${BITBUCKET_DB_NAME} -U ${BITBUCKET_DB_USER} -c \
    "UPDATE app_property SET prop_value = '${BASE_URL}' WHERE prop_key = 'instance.url';") != "UPDATE 1" ]]; then
    echo "Couldn't update database 'instance.url' property. Please check your database connection."
    exit 1
  else
    echo "The database 'instance.url' property was updated with ${BASE_URL}"
  fi
else
  echo "The ${BITBUCKET_BASE_URL_FILE} file doesn't exist or empty. Please check file existence or 'instance.url' property in the database."
  exit 1
fi

echo "Step8: Update license property in database"
if [[ -s ${BITBUCKET_LICENSE_FILE} ]]; then
  LICENSE=$(cat ${BITBUCKET_LICENSE_FILE})
  if [[ $(PGPASSWORD=${BITBUCKET_DB_PASS} psql -h ${DB_HOST} -d ${BITBUCKET_DB_NAME} -U ${BITBUCKET_DB_USER} -c \
    "update app_property set prop_value = '${LICENSE}' where prop_key = 'license';") != "UPDATE 1" ]]; then
    echo "Couldn't update database bitbucket license property. Please check your database connection."
    exit 1
  else
    echo "The database bitbucket license property was updated with ${LICENSE}"
  fi
else
  echo "The ${BITBUCKET_LICENSE_FILE} file doesn't exist or empty. Please check file existence or 'bitbucket license' property in the database."
  exit 1
fi

echo "Step9: Remove ${BITBUCKET_BASE_URL_FILE} file"
sudo rm ${BITBUCKET_BASE_URL_FILE}

echo "Step10: Remove ${BITBUCKET_LICENSE_FILE} file"
sudo rm ${BITBUCKET_LICENSE_FILE}

echo "DCAPT util script execution is finished successfully."
echo # move to a new line

echo "Important: new admin user credentials are admin/admin"
echo "Important: do not start Bitbucket until attachments restore is finished"

if [ "$(printf '%s\n' "$BITBUCKET_AUTO_DECLINE_VERSION" "$BITBUCKET_VERSION" | sort -V | head -n1)" = "$BITBUCKET_AUTO_DECLINE_VERSION" ]; then
       echo "Bitbucket ${BITBUCKET_VERSION} version has auto PRs decline feature enabled and it will be disabled in bitbucket.properties file."
       echo "feature.pull.request.auto.decline=false" | sudo tee -a ${DB_CONFIG}
fi
