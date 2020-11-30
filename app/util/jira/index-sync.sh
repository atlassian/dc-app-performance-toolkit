#!/bin/bash

SEARCH_LOG="/var/atlassian/application-data/jira/log/atlassian-jira.log"
TIMEOUT=300

if sudo -u jira test -f $SEARCH_LOG; then
    echo "Log file: $SEARCH_LOG"
else
    echo "File $SEARCH_LOG does not exist"
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

find_word_in_log "Index restore started"
find_word_in_log "indexes - 60%"
find_word_in_log "indexes - 80%"
find_word_in_log "indexes - 100%"
find_word_in_log "Index restore complete"

echo "DCAPT util script execution is finished successfully."