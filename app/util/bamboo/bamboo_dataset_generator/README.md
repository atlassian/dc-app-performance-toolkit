## Bamboo dataset generator - a tool that generates plans on Bamboo instance

Before you start, make sure you have installed [Maven](https://maven.apache.org/install.html).

Configuration located inside: [src/main/java/bamboogenerator/Main.java](src/main/java/bamboogenerator/Main.java)

**Configuration**

- `BAMBOO_SERVER_URL` - the URL of Bamboo
- `ADMIN_USER_NAME` - the username of admin account
- `PROJECTS_NUMBER` - the number of projects to generate
- `PLANS` - the number of plans to generate
- `PERCENT_OF_FAILED_PLANS` - the percent of plans to be generated as failed

**Run on Linux/Mac:**

    ./run.sh

**Run on Windows:**
    
    run



