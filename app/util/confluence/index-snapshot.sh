#!/bin/bash

# Wait until index snapshot for Confluence DC is generated

SNAPSHOT="/media/atl/confluence/shared-home/index-snapshots/IndexSnapshot_main_index_*zip"

TEMP_DIR="/var/atlassian/application-data/confluence/temp"
TEMP_ZIP="/var/atlassian/application-data/confluence/index/*main_index*zip"
MIN_SNAPSHOT_SIZE=5242880

TIMEOUT=3600    # 1 hour
COUNTER=0
SLEEP_TIME=20
ATTEMPTS=$((TIMEOUT / SLEEP_TIME))
FAIL_FAST_COUNTER=0
FAIL_FAST_ATTEMPTS=15


while [ ${COUNTER} -lt ${ATTEMPTS} ];do
    SNAPSHOT_SIZE=`sudo su -c "du -s ${SNAPSHOT}" | cut -f1`
    if sudo su -c "test -f ${SNAPSHOT} && [ ${SNAPSHOT_SIZE} -gt ${MIN_SNAPSHOT_SIZE} ]"; then
        echo # New line
        echo "Snapshot was created successfully."
        break
    fi

    if [ ${FAIL_FAST_COUNTER} -eq ${FAIL_FAST_ATTEMPTS} ]; then
        echo # move to a new line
        echo "Snapshot generation did not started."
        echo "Try to create a new Confluence page in UI and run 'General configuration' > 'Scheduled Jobs' > 'Clean Journal Entries' job again."
        exit 1
    fi

    if sudo su -c "test -d ${TEMP_DIR}"; then
        TEMP_DIR_SIZE=`sudo su -c "du -s ${TEMP_DIR}" | cut -f1`
        if [[ ${TEMP_DIR_SIZE} -gt 0 ]]; then
            echo "Temp dir found. Current temp dir size: ${TEMP_DIR_SIZE}"
        else
            let FAIL_FAST_COUNTER=$FAIL_FAST_COUNTER+1
        fi
    fi

    if sudo su -c "test -f ${TEMP_ZIP}"; then
        TEMP_ZIP_SIZE=`sudo su -c "du -s ${TEMP_ZIP}" | cut -f1`
        echo "Temp ZIP file found. Current temp ZIP file size: ${TEMP_ZIP_SIZE}"
    fi

    echo "Waiting for Snapshot generation, attempt ${COUNTER}/${ATTEMPTS} at waiting ${SLEEP_TIME} seconds."
    echo # New line
    echo # New line
    sleep ${SLEEP_TIME}
    let COUNTER=$COUNTER+1
done

if [ ${COUNTER} -eq ${ATTEMPTS} ]; then
    echo # move to a new line
    echo "Snapshot generation fails."
    echo "Try to create a new Confluence page in UI and run 'General configuration' > 'Scheduled Jobs' > 'Clean Journal Entries' job again."
    exit 1
fi