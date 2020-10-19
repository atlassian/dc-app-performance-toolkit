#!/bin/bash

JIRA_SUB_STRING="SUPPORTED_JIRA_VERSIONS=("
CONFLUENCE_SUB_STRING="SUPPORTED_CONFLUENCE_VERSIONS=("
BITBUCKET_SUB_STRING="SUPPORTED_BITBUCKET_VERSIONS=("

JIRA_FILE="dc-app-performance-toolkit/app/util/jira/populate_db.sh"
CONFLUENCE_FILE="dc-app-performance-toolkit/app/util/confluence/populate_db.sh"
BITBUCKET_FILE="dc-app-performance-toolkit/app/util/bitbucket/populate_db.sh"

JIRA_VERSIONS=$(grep "$JIRA_SUB_STRING" "$JIRA_FILE" | sed -e 's/[^0-9. ]*//g' -e 's/ \+/ /g')
CONFLUENCE_VERSIONS=$(grep "$CONFLUENCE_SUB_STRING" "$CONFLUENCE_FILE" | sed -e 's/[^0-9. ]*//g' -e 's/ \+/ /g')
BITBUCKET_VERSIONS=$(grep "$BITBUCKET_SUB_STRING" "$BITBUCKET_FILE" | sed -e 's/[^0-9. ]*//g' -e 's/ \+/ /g')

{
  echo "JIRA_VERSIONS=$JIRA_VERSIONS"
  echo "CONFLUENCE_VERSIONS=$CONFLUENCE_VERSIONS"
  echo "BITBUCKET_VERSIONS=$BITBUCKET_VERSIONS"
} >> .products_versions