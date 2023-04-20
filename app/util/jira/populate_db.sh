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
# Command to install psql client for Amazon Linux 2.
# In case of different distributive, please adjust accordingly or install manually.
INSTALL_PSQL_CMD="amazon-linux-extras install -y postgresql11"

# DB config file location (dbconfig.xml)
DB_CONFIG="/var/atlassian/application-data/jira/dbconfig.xml"

# Depending on Jira installation directory
JIRA_CURRENT_DIR="/opt/atlassian/jira-software/current"
JIRA_SETENV_FILE="${JIRA_CURRENT_DIR}/bin/setenv.sh"
JIRA_VERSION_FILE="/media/atl/jira/shared/jira-software.version"

# DB admin user name, password and DB name
JIRA_DB_NAME="jira"
JIRA_DB_USER="postgres"
JIRA_DB_PASS="Password1!"

# Jira/JSM supported versions

SUPPORTED_JIRA_VERSIONS=(8.20.20 9.4.4)
SUPPORTED_JSM_VERSIONS=(4.20.20 5.4.4)

SUPPORTED_VERSIONS=("${SUPPORTED_JIRA_VERSIONS[@]}")
# JSM section
if [[ ${jsm} == 1 ]]; then
  JIRA_CURRENT_DIR="/opt/atlassian/jira-servicedesk/current"
  JIRA_SETENV_FILE="${JIRA_CURRENT_DIR}/bin/setenv.sh"
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

# Datasets AWS bucket and db dump name
DATASETS_AWS_BUCKET="https://centaurus-datasets.s3.amazonaws.com/jira"
if [[ ${jsm} == 1 ]]; then
  DATASETS_AWS_BUCKET="https://centaurus-datasets.s3.amazonaws.com/jsm"
fi
DATASETS_SIZE="large"
if [[ ${jsm} == 1 && ${small} == 1 ]]; then
  # Only JSM supports "small" dataset
  DATASETS_SIZE="small"
fi
DB_DUMP_NAME="db.dump"
DB_DUMP_URL="${DATASETS_AWS_BUCKET}/${JIRA_VERSION}/${DATASETS_SIZE}/${DB_DUMP_NAME}"

###################    End of variables section  ###################

# Custom version check
if [[ ${custom} == 1 ]]; then
  DB_DUMP_URL="${DATASETS_AWS_BUCKET}/$JIRA_VERSION/${DATASETS_SIZE}/${DB_DUMP_NAME}"
  if curl --output /dev/null --silent --head --fail "$DB_DUMP_URL"; then
    echo "Custom version $JIRA_VERSION dataset URL found: ${DB_DUMP_URL}"
  else
    echo "Error: there is no dataset for version $JIRA_VERSION"
    exit 1
  fi
# Check if Jira version is supported
elif [[ ! "${SUPPORTED_VERSIONS[*]}" =~ ${JIRA_VERSION} ]]; then
  echo "Jira Version: ${JIRA_VERSION} is not officially supported by Data Center App Performance Toolkit."
  echo "Supported Jira Versions: ${SUPPORTED_VERSIONS[*]}"
  echo "If you want to force apply an existing datasets to your Jira, use --force flag with version of dataset you want to apply:"
  echo "e.g. ./populate_db.sh --force 8.5.0"
  echo "!!! Warning !!! This may break your Jira instance."
  # Check if --force flag is passed into command
  if [[ ${force} == 1 ]]; then
    # Check if version was specified after --force flag
    if [[ -z ${version} ]]; then
      echo "Error: --force flag requires version after it."
      echo "Specify one of these versions: ${SUPPORTED_VERSIONS[*]}"
      exit 1
    fi
    # Check if passed Jira version is in list of supported
    if [[ " ${SUPPORTED_VERSIONS[@]} " =~ " ${version} " ]]; then
      DB_DUMP_URL="${DATASETS_AWS_BUCKET}/${version}/${DATASETS_SIZE}/${DB_DUMP_NAME}"
      echo "Force mode. Dataset URL: ${DB_DUMP_URL}"
      # If there is no DOWNGRADE_OPT - set it
      DOWNGRADE_OPT="Djira.downgrade.allowed=true"
      if sudo su jira -c "! grep -q ${DOWNGRADE_OPT} $JIRA_SETENV_FILE"; then
        sudo sed -i "s/JVM_SUPPORT_RECOMMENDED_ARGS=\"/&-${DOWNGRADE_OPT} /" "${JIRA_SETENV_FILE}"
        echo "Flag -${DOWNGRADE_OPT} was set in ${JIRA_SETENV_FILE}"
      fi
    else
      LAST_DATASET_VERSION=${SUPPORTED_VERSIONS[${#SUPPORTED_VERSIONS[@]}-1]}
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
echo "This script restores Postgres DB from SQL DB dump for Jira DC created with AWS Quickstart defaults."
echo "You can review or modify default variables in 'Variables section' of this script."
echo # move to a new line
echo "Variables:"
echo "JIRA_CURRENT_DIR=${JIRA_CURRENT_DIR}"
echo "DB_CONFIG=${DB_CONFIG}"
echo "JIRA_DB_NAME=${JIRA_DB_NAME}"
echo "JIRA_DB_USER=${JIRA_DB_USER}"
echo "JIRA_DB_PASS=${JIRA_DB_PASS}"
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

echo "Check database connection"
PGPASSWORD=${JIRA_DB_PASS} pg_isready -U ${JIRA_DB_USER} -h ${DB_HOST}
if [[ $? -ne 0 ]]; then
  echo "Connection to database failed. Please check correctness of following variables:"
  echo "JIRA_DB_NAME=${JIRA_DB_NAME}"
  echo "JIRA_DB_USER=${JIRA_DB_USER}"
  echo "JIRA_DB_PASS=${JIRA_DB_PASS}"
  echo "DB_HOST=${DB_HOST}"
  exit 1
fi

echo "Check database permissions for user ${JIRA_DB_USER}"
PGPASSWORD=${JIRA_DB_PASS} createdb -U ${JIRA_DB_USER} -h ${DB_HOST} -T template0 -E "UNICODE" -l "C" TEST
if [[ $? -ne 0 ]]; then
  echo "User ${JIRA_DB_USER} doesn't have permission to create database."
  exit 1
else
  PGPASSWORD=${JIRA_DB_PASS} dropdb -U ${JIRA_DB_USER} -h ${DB_HOST} TEST
fi

echo "Step3: Write jira.baseurl property to file"
JIRA_BASE_URL_FILE="base_url"
if [[ -s ${JIRA_BASE_URL_FILE} ]]; then
  echo "File ${JIRA_BASE_URL_FILE} was found. Base url: $(cat ${JIRA_BASE_URL_FILE})."
else
  PGPASSWORD=${JIRA_DB_PASS} psql -h ${DB_HOST} -d ${JIRA_DB_NAME} -U ${JIRA_DB_USER} -Atc \
  "select propertyvalue from propertyentry PE
  join propertystring PS on PE.id=PS.id
  where PE.property_key = 'jira.baseurl';" > ${JIRA_BASE_URL_FILE}
  if [[ ! -s ${JIRA_BASE_URL_FILE} ]]; then
    echo "Failed to get Base URL value from database."
    exit 1
  fi
  echo "$(cat ${JIRA_BASE_URL_FILE}) was written to the ${JIRA_BASE_URL_FILE} file."
fi

echo "Step4: Write jira license to file"
JIRA_LICENSE_FILE="license"
if [[ -s ${JIRA_LICENSE_FILE} ]]; then
  echo "File ${JIRA_LICENSE_FILE} was found. License: $(cat ${JIRA_LICENSE_FILE})."
  else
    PGPASSWORD=${JIRA_DB_PASS} psql -h ${DB_HOST} -d ${JIRA_DB_NAME} -U ${JIRA_DB_USER} -Atc \
    "select license from productlicense;" > ${JIRA_LICENSE_FILE}
    if [[ ! -s ${JIRA_LICENSE_FILE} ]]; then
      echo "Failed to get jira license from database. Check DB configuration variables."
      exit 1
    fi
    echo "$(cat ${JIRA_LICENSE_FILE}) was written to the ${JIRA_LICENSE_FILE} file."
fi

echo "Step5: Stop Jira"
sudo systemctl stop jira
if [[ $? -ne 0 ]]; then
  echo "Jira did not stop. Please try to rerun script."
  exit 1
fi

echo "Step6: Download database dump"
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
time wget --progress=dot:giga "${DB_DUMP_URL}"
if [[ $? -ne 0 ]]; then
  echo "Database dump download failed! Pls check available disk space."
  exit 1
fi

echo "Step7: SQL Restore"
echo "Drop database"
PGPASSWORD=${JIRA_DB_PASS} dropdb -U ${JIRA_DB_USER} -h ${DB_HOST} ${JIRA_DB_NAME}
if [[ $? -ne 0 ]]; then
  echo "Drop DB failed."
  exit 1
fi
sleep 5
echo "Create database"
PGPASSWORD=${JIRA_DB_PASS} createdb -U ${JIRA_DB_USER} -h ${DB_HOST} -T template0 -E "UNICODE" -l "C" ${JIRA_DB_NAME}
if [[ $? -ne 0 ]]; then
  echo "Create database failed."
  exit 1
fi
sleep 5
echo "PG Restore"
time PGPASSWORD=${JIRA_DB_PASS} pg_restore --schema=public -v -U ${JIRA_DB_USER} -h ${DB_HOST} -d ${JIRA_DB_NAME} ${DB_DUMP_NAME}
if [[ $? -ne 0 ]]; then
  echo "SQL Restore failed!"
  exit 1
fi

echo "Step8: Update jira.baseurl property in database"
if [[ -s ${JIRA_BASE_URL_FILE} ]]; then
  BASE_URL=$(cat $JIRA_BASE_URL_FILE)
  if [[ $(PGPASSWORD=${JIRA_DB_PASS} psql -h ${DB_HOST} -d ${JIRA_DB_NAME} -U ${JIRA_DB_USER} -c \
    "update propertystring
    set propertyvalue = '${BASE_URL}'
    from propertyentry PE
    where PE.id=propertystring.id
    and PE.property_key = 'jira.baseurl';") != "UPDATE 1" ]]; then
    echo "Couldn't update database jira.baseurl property. Please check your database connection."
    exit 1
  else
    echo "The database jira.baseurl property was updated with ${BASE_URL}"
  fi
else
  echo "The ${JIRA_BASE_URL_FILE} file doesn't exist or empty. Please check file existence or 'jira.baseurl' property in the database."
  exit 1
fi

echo "Step9: Update jira license in database"
if [[ -s ${JIRA_LICENSE_FILE} ]]; then
  LICENSE=$(cat ${JIRA_LICENSE_FILE})
  LICENSE_ID=$(PGPASSWORD=${JIRA_DB_PASS} psql -h ${DB_HOST} -d ${JIRA_DB_NAME} -U ${JIRA_DB_USER} -Atc \
  "select id from productlicense;")
  if [[ -z "${LICENSE_ID}" ]]; then
    echo "License update failed. License id value in the database is empty."
    exit 1
  fi
  if [[ $(PGPASSWORD=${JIRA_DB_PASS} psql -h ${DB_HOST} -d ${JIRA_DB_NAME} -U ${JIRA_DB_USER} -c \
    "update productlicense
    set license = '${LICENSE}'
    where id = '${LICENSE_ID}';") != "UPDATE 1" ]]; then
    echo "Couldn't update database jira license. Please check your database connection."
    exit 1
  else
    echo "The database jira license was updated with ${LICENSE}"
  fi
else
  echo "The ${JIRA_LICENSE_FILE} file doesn't exist or empty. Please check file existence or jira license in the database."
  exit 1
fi

echo "Step10: Start Jira"
  sudo systemctl start jira

rm -rf ${DB_DUMP_NAME}

echo "Step11: Remove ${JIRA_BASE_URL_FILE} file"
sudo rm ${JIRA_BASE_URL_FILE}

echo "Step12: Remove ${JIRA_LICENSE_FILE} file"
sudo rm ${JIRA_LICENSE_FILE}

echo "DCAPT util script execution is finished successfully."
echo # move to a new line

echo "Important: new admin user credentials are admin/admin"
echo "Wait a couple of minutes until Jira is started."
