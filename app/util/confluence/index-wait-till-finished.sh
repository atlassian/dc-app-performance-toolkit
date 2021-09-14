#!/bin/bash

# Wait for full re index finished

SEARCH_LOG="/var/atlassian/application-data/confluence/logs/atlassian-confluence-index*"
CONFLUENCE_VERSION_FILE="/media/atl/confluence/shared-home/confluence.version"
PROGRESS="Re-index progress:.*"
FINISHED="Re-index progress: 100% complete"

CONFLUENCE_VERSION=$(sudo su confluence -c "cat ${CONFLUENCE_VERSION_FILE}")
if [[ -z "$CONFLUENCE_VERSION" ]]; then
  echo The $CONFLUENCE_VERSION_FILE file does not exists or emtpy. Please check if CONFLUENCE_VERSION_FILE variable \
  has a valid file path of the Confluence version file or set your Cluster CONFLUENCE_VERSION explicitly.
  exit 1
fi
echo "Confluence Version: ${CONFLUENCE_VERSION}"

if [ "$(sudo su confluence -c "ls -l ""$SEARCH_LOG"" 2>/dev/null | wc -l")" -gt 0 ]
then
  echo "Log files were found:"
  sudo su confluence -c "ls $SEARCH_LOG"
else
  echo "ERROR: There are no log files found like $SEARCH_LOG"
  echo "Make sure your Confluence version is 7.7.x or higher."
  exit 1
fi

TIMEOUT=21600    # 6 hour
COUNTER=0
SLEEP_TIME=60
ATTEMPTS=$((TIMEOUT / SLEEP_TIME))

while [ ${COUNTER} -lt ${ATTEMPTS} ];do
  grep_result=$(sudo su -c "grep -h -o \"$PROGRESS\" $SEARCH_LOG" 2>/dev/null | tail -1)
  echo "Status:"
  echo "$grep_result"
  if [ -z "$grep_result" ];then
    echo "ERROR: $PROGRESS was not found in $SEARCH_LOG"
    echo "Check if index process was started."
    exit 1
  fi
  finished=$(echo "$grep_result" | grep "$FINISHED")
  if [ -z "$finished" ];then
    echo "Waiting for index finished, attempt ${COUNTER}/${ATTEMPTS} at waiting ${SLEEP_TIME} seconds."
    echo # New line
    sleep ${SLEEP_TIME}
    (( COUNTER++ )) || true
  else
    echo "Index finished successfully."
    break
  fi
done

if [ "${COUNTER}" -eq ${ATTEMPTS} ]; then
  echo # move to a new line
  echo "ERROR: Wait for index finished failed"
  echo "See logs for more details:"
  sudo su -c "ls -a $SEARCH_LOG"
  exit 1
fi

echo "DCAPT util script execution is finished successfully."