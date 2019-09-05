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

# DB admin user name, password and DB name
JIRA_DB_NAME="jira"
JIRA_DB_USER="postgres"
JIRA_DB_PASS="password"

# Datasets AWS bucket and db dupm name
DATASETS_AWS_BUCKET="https://centaurus-datasets.s3.amazonaws.com/jira/8.0.3/large"
DB_DUMP_NAME="db.dump"
###################    End of variables section  ###################


echo "!!! Warning !!!"
echo    # move to a new line
echo "This script restores Postgres DB from SQL DB dump for Jira DC created with AWS Quickstart defaults."
echo "You can review or modify default variables in 'Variables section' of this script."
echo    # move to a new line
echo "Variables:"
echo "JIRA_CURRENT_DIR=${JIRA_CURRENT_DIR}"
echo "DB_CONFIG=${DB_CONFIG}"
echo "JIRA_DB_NAME=${JIRA_DB_NAME}"
echo "JIRA_DB_USER=${JIRA_DB_USER}"
echo "JIRA_DB_PASS=${JIRA_DB_PASS}"
echo "DB_DUMP=${DATASETS_AWS_BUCKET}/${DB_DUMP_NAME}"
echo    # move to a new line
read -p "I confirm that variables are correct and want to proceed (y/n)?  " -n 1 -r
echo    # move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
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
rm -rf ${DB_DUMP_NAME}
wget ${DATASETS_AWS_BUCKET}/${DB_DUMP_NAME}
if [[ $? -ne 0 ]]; then
  echo "DB dump download failed! Pls check available disk space."
  exit 1
fi

echo "Step3: Stop Jira"
CATALINA_PID=$(pgrep -f "catalina")
if [[ -z ${CATALINA_PID} ]]; then
  echo "Jira is not running"
else
  echo "Stopping Jira"
  sudo su jira -c "echo ${CATALINA_PID} > ${CATALINA_PID_FILE}"
  sudo su jira -c "${STOP_JIRA}"
  sleep 5
fi

echo "Step4: Get DB_URL"
DB_URL=$(sudo su -c "cat ${DB_CONFIG} | grep 'jdbc:postgresql' | cut -d'/' -f3 | cut -d':' -f1")
if [[ -z ${DB_URL} ]]; then
  echo "DataBase URL was not found in ${DB_CONFIG}"
  exit 1
fi
echo "DB_URL=${DB_URL}"

echo "Step5: SQL Restore"
echo "Check DB connection"
PGPASSWORD=${JIRA_DB_PASS} pg_isready -U ${JIRA_DB_USER} -h ${DB_URL}
if [[ $? -ne 0 ]]; then
  echo "Connection to DB failed. Please check correctness of following variables:"
  echo "JIRA_DB_NAME=${JIRA_DB_NAME}"
  echo "JIRA_DB_USER=${JIRA_DB_USER}"
  echo "JIRA_DB_PASS=${JIRA_DB_PASS}"
  echo "DB_URL=${DB_URL}"
  exit 1
fi
echo "Drop DB"
PGPASSWORD=${JIRA_DB_PASS} dropdb -U ${JIRA_DB_USER} -h ${DB_URL} ${JIRA_DB_NAME}
sleep 5
echo "Create DB"
PGPASSWORD=${JIRA_DB_PASS} createdb -U ${JIRA_DB_USER} -h ${DB_URL} -T template0 ${JIRA_DB_NAME}
sleep 5
echo "PG Restore"
time PGPASSWORD=${JIRA_DB_PASS} pg_restore -v -U ${JIRA_DB_USER} -h ${DB_URL} -d ${JIRA_DB_NAME} ${DB_DUMP_NAME}
if [[ $? -ne 0 ]]; then
  echo "SQL Restore failed!"
  exit 1
fi

echo "Step6: Start Jira"
sudo su jira -c "${START_JIRA}"
rm -rf ${DB_DUMP_NAME}

echo "Important: new admin user credentials are admin/admin"
echo "Wait a couple of minutes until Jira is started."