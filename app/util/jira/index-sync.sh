#!/bin/bash

SEARCH_LOG="/var/atlassian/application-data/jira/log/atlassian-jira.log"
TIMEOUT=300

if sudo -u jira test -f $SEARCH_LOG; then
    echo "Found $SEARCH_LOG"
else
    echo "File $SEARCH_LOG does not exist"
    exit 1
fi

function find_word_in_log() {
        let COUNTER=0
        let SLEEP_TIME=2
        TOTAL_COUNT=$((TIMEOUT / SLEEP_TIME))
        while [ $COUNTER -lt $TOTAL_COUNT ];do
                check_grep=`sudo su jira -c "cat $SEARCH_LOG" | grep "$1" | awk '{print substr(\$0, index(\$0,\$6)) }' 2>&1`
                if [ -z "$check_grep" ];then
                        for i in {1..$COUNTER}; do echo -n .; done
                        sleep $SLEEP_TIME
                        let COUNTER=$COUNTER+1
                else
                        echo "$check_grep"
                        break
                fi

        done
        echo "Failed to find $1 in $SEARCH_LOG in $TIMEOUT seconds"
        exit 1
}

find_word_in_log "Index restore started"
find_word_in_log "indexes - 60%"
find_word_in_log "indexes - 80%"
find_word_in_log "indexes - 100%"
find_word_in_log "Index restore complete"
