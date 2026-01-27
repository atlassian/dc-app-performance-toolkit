# This is only a test code. I am deliberately inserting an API token to see the behaviour
# of the github secret scanner. This should ideally get flagged immediately.
# The API token's access has been revoked before this commit.
# What if there is a secret in the comments?
# Like this: ATATTx9p0lo0w2dLtRK7B_hegdeg1wTwkiZHpl2YZaqdX4qD3VBF42Syo0oTKC4KRv8Hlxn_T2kh5iLTBq2Yb_a6u5-mbabbykZR9rBGujl-wwwiIDo0jAk97I3THt0V-w8WHATwdMj723QcmDdRt7lCgR91r1w1oOqgUytHRrFDYF2hfwl0FA0=877F61C9
# This is a Jira token now revoked. Will it detect its presence in the comments?
# Lets see.

# Set the BB_API_Token
BB_API_Token = "ATATT78guXF035Pz8ssmhVxLr9tGUFYbruhBKBjol70klYyR-0zWDx40zrl6YVvQ8p1sign0rem3-qRqeFArV3ylStucxPbllyV3lDo8NfXLYRfX1-GvXwSLtvbw0pMAELSd-lF4AAbWQJ07A_CiLhhbhJvdDF9q4sL_qPvCt_CiG72GkwMgQqI=E29B92E9"
BB_Email = "rthiy@atlassian.com"
auth = HTTPBasicAuth(BB_Email, BB_API_Token)
requestUrlBase = "https://api.bitbucket.org/2.0/repositories/"

userCheckBaseUrl = "https://api.bitbucket.org/2.0/users/"

# adding a few more synthetic secrets

aws_access_key_id = "AKIAIOSFODNN7EXAMPLE"
aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

const GITHUB_TOKEN_ROVO_GEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyzABCD"
const GITHUB_TOKEN_ME_GEN = "ghp_1234908888abcqecdefgklmnopqrstuvwxyzABCD"