package bamboogenerator;

import com.atlassian.bamboo.specs.api.builders.permission.PermissionType;
import com.atlassian.bamboo.specs.api.builders.permission.Permissions;
import com.atlassian.bamboo.specs.api.builders.permission.PlanPermissions;
import com.atlassian.bamboo.specs.api.builders.plan.Plan;
import com.atlassian.bamboo.specs.api.builders.plan.PlanIdentifier;
import com.atlassian.bamboo.specs.util.BambooServer;
import com.atlassian.bamboo.specs.util.Logger;
import com.atlassian.bamboo.specs.util.SimpleTokenCredentials;

import static org.apache.commons.lang3.StringUtils.isBlank;

public abstract class AbstractSpecPlan {
   public static final String BAMBOO_SERVER_URL = "http://0.0.0.0:8085";
   public static final String BAMBOO_TOKEN = "BAMBOO_TOKEN";


    protected Logger log = Logger.getLogger(this.getClass());

    abstract Plan createPlan(String name,
                             String planKey,
                             String projectName,
                             String projectKey,
                             Boolean isFailed);

    public void publishPlan(String planName,
                            String planKey,
                            String projectName,
                            String projectKey,
                            Boolean isFailed, BambooServer bambooServer) {



        Plan plan = createPlan(planName, planKey, projectName, projectKey, isFailed);
        bambooServer.publish(plan);
        PlanPermissions planPermission = createPlanPermission(plan.getIdentifier());
        bambooServer.publish(planPermission);
    }

    private static PlanPermissions createPlanPermission(PlanIdentifier planIdentifier) {
        Permissions permissions = new Permissions()
                .userPermissions("admin", PermissionType.ADMIN, PermissionType.EDIT)
                .loggedInUserPermissions(PermissionType.EDIT)
                .loggedInUserPermissions(PermissionType.BUILD);

        return new PlanPermissions(planIdentifier)
                .permissions(permissions);
    }

//    public BambooServer initBambooServer() {
//        String token = getToken();
//        if (token == null) {
//            return new BambooServer(BAMBOO_SERVER_URL);
//        }
//
//        return new BambooServer(BAMBOO_SERVER_URL, new SimpleTokenCredentials(token));
//    }

    private String getToken() {
        try {
            String token = System.getenv(BAMBOO_TOKEN);
            if (isBlank(token)) {
                throw new RuntimeException("Env variable " + BAMBOO_TOKEN + " is not set or empty");
            }

            return token;
        } catch (Throwable t) {
            log.info("Can't find token");
            log.debug("Error while getting token", t);
        }

        return null;
    }

    @Override
    public String toString() {
        return this.getClass().getCanonicalName();
    }
}
