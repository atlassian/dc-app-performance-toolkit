#!/bin/bash

###################    Variables section         ###################
# Command to install psql client for Amazon Linux 2.
# In case of different distributive, please adjust accordingly or install manually.
INSTALL_PSQL_CMD="amazon-linux-extras install -y postgresql10"

# DB config file location (dbconfig.xml)
DB_CONFIG="/var/atlassian/application-data/jira/dbconfig.xml"

# Depending on Jira installation directory
JIRA_CURRENT_DIR="/opt/atlassian/jira-software/current"
STOP_JIRA="${JIRA_CURRENT_DIR}/bin/stop-jira.sh"
START_JIRA="${JIRA_CURRENT_DIR}/bin/start-jira.sh"
CATALINA_PID_FILE="${JIRA_CURRENT_DIR}/work/catalina.pid"
JIRA_SETENV_FILE="${JIRA_CURRENT_DIR}/bin/setenv.sh"
JIRA_VERSION_FILE="/media/atl/jira/shared/jira-software.version"
SHUT_DOWN_TOMCAT="${JIRA_CURRENT_DIR}/bin/shutdown.sh"

# DB admin user name, password and DB name
JIRA_DB_NAME="jira"
JIRA_DB_USER="postgres"
JIRA_DB_PASS="Password1!"

# Jira version variables
SUPPORTED_JIRA_VERSIONS=(8.0.3 7.13.6 8.5.0)
JIRA_VERSION=$(sudo su jira -c "cat ${JIRA_VERSION_FILE}")
echo "Jira Version: ${JIRA_VERSION}"

# Datasets AWS bucket and db dump name
DATASETS_AWS_BUCKET="https://centaurus-datasets.s3.amazonaws.com/jira"
DATASETS_SIZE="large"
DB_DUMP_NAME="db.dump"
DB_DUMP_URL="${DATASETS_AWS_BUCKET}/${JIRA_VERSION}/${DATASETS_SIZE}/${DB_DUMP_NAME}"

###################    End of variables section  ###################


# Check if Jira version is supported
if [[ ! "${SUPPORTED_JIRA_VERSIONS[@]}" =~ "${JIRA_VERSION}" ]]; then
  echo "Jira Version: ${JIRA_VERSION} is not officially supported by Data Center App Performance Toolkit."
  echo "Supported Jira Versions: ${SUPPORTED_JIRA_VERSIONS[@]}"
  echo "If you want to force apply an existing datasets to your Jira, use --force flag with version of dataset you want to apply:"
  echo "e.g. ./populate_db.sh --force 8.0.3"
  echo "!!! Warning !!! This may break your Jira instance."
  # Check if --force flag is passed into command
  if [[ "$1" == "--force" ]]; then
    # Check if passed Jira version is in list of supported
    if [[ "${SUPPORTED_JIRA_VERSIONS[@]}" =~ "$2" ]]; then
      DB_DUMP_URL="${DATASETS_AWS_BUCKET}/$2/${DATASETS_SIZE}/${DB_DUMP_NAME}"
      echo "Force mode. Dataset URL: ${DB_DUMP_URL}"
      # If there is no DOWNGRADE_OPT - set it
      DOWNGRADE_OPT="Djira.downgrade.allowed=true"
      if sudo su jira -c "! grep -q ${DOWNGRADE_OPT} $JIRA_SETENV_FILE"; then
        sudo sed -i "s/JVM_SUPPORT_RECOMMENDED_ARGS=\"/&-${DOWNGRADE_OPT} /" "${JIRA_SETENV_FILE}"
        echo "Flag -${DOWNGRADE_OPT} was set in ${JIRA_SETENV_FILE}"
      fi
    else
      echo "Correct dataset version was not specified after --force flag."
      echo "Available datasets: ${SUPPORTED_JIRA_VERSIONS[@]}"
      exit 1
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

echo "Step2: Stop Jira"
CATALINA_PID=$(pgrep -f "catalina")
echo "CATALINA_PID=${CATALINA_PID}"
if [[ -z ${CATALINA_PID} ]]; then
  echo "Jira is not running"
  sudo su -c "rm -rf ${CATALINA_PID_FILE}"
else
  echo "Stopping Jira"
  if [[ ! -f "${CATALINA_PID_FILE}" ]]; then
    echo "File created: ${CATALINA_PID_FILE}"
    sudo su -c "echo ${CATALINA_PID} > ${CATALINA_PID_FILE}"
  fi
  sudo su -c "${SHUT_DOWN_TOMCAT}"
  COUNTER=0
  TIMEOUT=5
  ATTEMPTS=30
  while [[ "${COUNTER}" -lt "${ATTEMPTS}" ]]; do
    if [[ -z $(pgrep -f "catalina") ]]; then
      echo Jira is stopped
      break
    fi
    echo "Waiting for Jira stop, attempt ${COUNTER}/${ATTEMPTS} at waiting ${TIMEOUT} seconds."
    sleep ${TIMEOUT}
    let COUNTER++
  done
  if [ ${COUNTER} -eq ${ATTEMPTS} ]; then
    echo "Jira stop was not finished in $ATTEMPTS attempts with $TIMEOUT sec timeout."
    echo "Try to rerun script."
    exit 1
  fi
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
PGPASSWORD=${JIRA_DB_PASS} pg_isready -U ${JIRA_DB_USER} -h ${DB_HOST}
if [[ $? -ne 0 ]]; then
  echo "Connection to DB failed. Please check correctness of following variables:"
  echo "JIRA_DB_NAME=${JIRA_DB_NAME}"
  echo "JIRA_DB_USER=${JIRA_DB_USER}"
  echo "JIRA_DB_PASS=${JIRA_DB_PASS}"
  echo "DB_HOST=${DB_HOST}"
  exit 1
fi
echo "Drop DB"
PGPASSWORD=${JIRA_DB_PASS} dropdb -U ${JIRA_DB_USER} -h ${DB_HOST} ${JIRA_DB_NAME}
if [[ $? -ne 0 ]]; then
  echo "Drop DB failed."
  exit 1
fi
sleep 5
echo "Create DB"
PGPASSWORD=${JIRA_DB_PASS} createdb -U ${JIRA_DB_USER} -h ${DB_HOST} -T template0 -E "UNICODE" -l "C" ${JIRA_DB_NAME}
if [[ $? -ne 0 ]]; then
  echo "Create DB failed."
  exit 1
fi
sleep 5
echo "PG Restore"
time PGPASSWORD=${JIRA_DB_PASS} pg_restore -v -U ${JIRA_DB_USER} -h ${DB_HOST} -d ${JIRA_DB_NAME} ${DB_DUMP_NAME}
if [[ $? -ne 0 ]]; then
  echo "SQL Restore failed!"
  exit 1
fi

echo "Step6: Start Jira"
sudo su jira -c "${START_JIRA}"
rm -rf ${DB_DUMP_NAME}

echo "Finished"
echo  # move to a new line

echo "Important: new admin user credentials are admin/admin"
echo "Wait a couple of minutes until Jira is started."