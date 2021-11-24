## Bamboo dataset generator - a tool that generates plans on Bamboo instance

Before you start, make sure you have installed [Maven](https://maven.apache.org/install.html).

Configuration located inside: [src/main/java/bamboogenerator/Main.java](src/main/java/bamboogenerator/Main.java)

**Client Configuration**

- `BAMBOO_SERVER_URL` - the URL of Bamboo
- `ADMIN_USER_NAME` - the username of admin account


  **Generator Configuration**
- `PROJECTS_NUMBER` - the number of projects to generate
- `PLANS` - the number of plans to generate
- `PERCENT_OF_FAILED_PLANS` - the percent of plans to be generated as failed

---

**NOTE**

Please make sure you haven't changed `Generator Configuration` after initial generation.
In case you need another configuration you have to start from clean dataset.

The generator will check if you have plans on a Bamboo server that are out of the generated set,
it will fail execution if such plans exist.

---

**Run on Linux/Mac:**

    ./run.sh

**Run on Windows:**
    
    run



