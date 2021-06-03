#!/bin/bash

# Wait until index sync is finished on a new Confluence DC node

SEARCH_LOG="/var/atlassian/application-data/confluence/logs/*.log"
TIMEOUT=1200

if [ "$(sudo su confluence -c "ls -l ""$SEARCH_LOG"" 2>/dev/null | wc -l")" -gt 0 ]
then
  echo "Log files were found:"
  sudo su confluence -c "ls $SEARCH_LOG"
else
  echo "There are no log files found like $SEARCH_LOG"
  exit 1
fi

function find_word_in_log() {
        COUNTER=0
        SLEEP_TIME=10
        ATTEMPTS=$((TIMEOUT / SLEEP_TIME))
        while [ ${COUNTER} -lt ${ATTEMPTS} ];do
                check_grep=`sudo su confluence -c "cat $SEARCH_LOG" | grep -o "$1"`
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

find_word_in_log "Index recovery is required for main index, starting now"
find_word_in_log "main index recovered from shared home directory"

echo "DCAPT util script execution is finished successfully."