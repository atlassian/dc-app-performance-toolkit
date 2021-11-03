#!/bin/bash

# Script to monitor in a real time the number of free bamboo agents running on the host by parsing agents log files.

AGENT_LOG="atlassian-bamboo-agent.log"
FREE_MSG="ready to take build from queue"
BUSY_MSG="taken from queue"
AGENT_JAR="agentInstaller.jar"
SLEEP=1

running_agents_count=$(pgrep -f "$AGENT_JAR" | wc -l)
if [[ "$running_agents_count" -eq 0 ]]; then
   echo "ERROR: There are no running agents found by 'pgrep -f $AGENT_JAR' command."
   exit 1
fi

mapfile -t array < <(find ./ -name ${AGENT_LOG})
total_agents_count=${#array[@]}
if [[ "$total_agents_count" -eq 0 ]]; then
   echo "ERROR: Agents log files ($AGENT_LOG) were not found in $PWD directory."
   exit 1
fi

while true
do
  free_agents_count=0
  for i in "${array[@]}"
  do
    last_status=$(grep -E "$FREE_MSG|$BUSY_MSG" "$i" | tail -1)
    if [[ $last_status =~ $FREE_MSG ]]; then
      ((free_agents_count++))
    fi
  done

  echo "$(date +'%Y-%m-%d %T')    Free agents count: $free_agents_count/$total_agents_count"
  sleep $SLEEP
done