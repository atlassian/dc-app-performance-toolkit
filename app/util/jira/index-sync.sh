#!/bin/bash

SEARCH_LOG="/var/atlassian/application-data/jira/log/*.log"
TIMEOUT=300
MIN_SNAPSHOT_SIZE=7140000

if [ "$(sudo su jira -c "ls -l ""$SEARCH_LOG"" 2>/dev/null | wc -l")" -gt 0 ]
then
  echo "Log files were found:"
  sudo su jira -c "ls $SEARCH_LOG"
else
  echo "There are no log files found like $SEARCH_LOG"
  exit 1
fi


function find_word_in_log() {
        COUNTER=0
        SLEEP_TIME=2
        ATTEMPTS=$((TIMEOUT / SLEEP_TIME))
        while [ ${COUNTER} -lt ${ATTEMPTS} ];do
                check_grep=`sudo su jira -c "cat $SEARCH_LOG" | grep -o "$1"`
                if [ -z "$check_grep" ];then
                        for i in {1..$COUNTER}; do echo -n .; done
                        sleep ${SLEEP_TIME}
                        let COUNTER=$COUNTER+1
                else
                        echo "$check_grep"
                        break
                fi

        done
        if [ ${COUNTER} -eq ${ATTEMPTS} ]; then
            echo # move to a new line
            echo "Failed to find $1 in $SEARCH_LOG in $TIMEOUT seconds"
            exit 1
        fi
}
# Check if is correct index snapshot for Jira DC is generated
function find_correct_snapshot() {
SLEEP_TIME=100
ATTEMPTS=$((TIMEOUT / SLEEP_TIME))
while [ ${COUNTER} -lt ${ATTEMPTS} ];do
  # Get the latest snapshot from the index-snapshots folder
  SNAPSHOT=$(sudo su -c "ls -tr /media/atl/jira/shared/export/indexsnapshots/IndexSnapshot*" 2>/dev/null | tail -1)
  if  sudo su -c "test -z ${SNAPSHOT}"; then
    echo "There is no snapshot file yet in /media/atl/jira/shared/export/indexsnapshots/ folder."
  else
    SNAPSHOT_SIZE=$(sudo su -c "du -s ${SNAPSHOT}" | cut -f1)
    echo "Current size of the snapshot file: ${SNAPSHOT_SIZE}"
    if sudo su -c "test -f ${SNAPSHOT} && [ ${SNAPSHOT_SIZE} -gt ${MIN_SNAPSHOT_SIZE} ]"; then
      break
    else
      sleep ${SLEEP_TIME}
      let COUNTER=$COUNTER+1
    fi
  fi
done

if [ ${COUNTER} -eq ${ATTEMPTS} ]; then
  echo # move to a new line
  echo "Failed to find correct snapshot file, please follow these steps for the index recovery:
        1. Scale back to the 1 node
        2. Go to Jira System settings
        3. Indexing page
        4. Make sure you have index on this node or run re-index (~30min)
        5. Set the recovery index schedule to 5min ahead of the current time
        6. Wait 10min until the index snapshot is created
        7. After scaling new nodes will get an index recovered from the index snapshot"
  exit 1
fi
}

find_word_in_log "Index restore complete\|Done recovering indexes from snapshot found in shared home"
find_correct_snapshot

echo "DCAPT util script execution is finished successfully."
