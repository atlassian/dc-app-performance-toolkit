# Overview

To run this you must add valid admin credentials to `app/jira.yml`

See https://developer.atlassian.com/platform/marketplace/dc-apps-performance-toolkit-user-guide-jira-cf/ for what to do with this repo. You can skip to Step 5 titled `Enterprise-scale Environment`

As of 9/8/2023 there is a bug with bzt that prevents using versions of Chrome newer than `114.0.5735.90`. Check the upstream repo to see if this is fixed, custom changes to resolve this problem have been added with comments in the `Dockerfile` and in `app/jira.yml`.

## Testing
After Run 1 of Step 8 our Jira app must be installed. See instructions [here](https://docs.google.com/document/d/188wLOuTHduoCjFQUFN6srxRV2sQRKDbcx2mjEl0wAqU/edit#heading=h.8sx1wi5oltrp). The jar files are stored in [Artifactory](https://unitq.jfrog.io/ui/native/libs-release-local/com/unitq/jira-server-plugin/)

Before running scalability testing, create at least 5 tickets in Jira with the summary field containing `Appissue`, such as `Appissue 1, Appissue 2, etc`. Once these tickets are created, add them to the unitQ Jira plugin in unitQ Monitor, this can be done by searching for the issue name or via a direct link. 