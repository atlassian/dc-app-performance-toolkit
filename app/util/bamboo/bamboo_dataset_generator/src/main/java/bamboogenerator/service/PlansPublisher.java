package bamboogenerator.service;

import com.atlassian.bamboo.specs.api.builders.permission.PermissionType;
import com.atlassian.bamboo.specs.api.builders.permission.Permissions;
import com.atlassian.bamboo.specs.api.builders.permission.PlanPermissions;
import com.atlassian.bamboo.specs.api.builders.plan.Plan;
import com.atlassian.bamboo.specs.api.builders.plan.PlanIdentifier;
import com.atlassian.bamboo.specs.util.BambooServer;

import java.util.List;

import static bamboogenerator.service.BambooServerInitializer.initBambooServer;

public class PlansPublisher {
    private final BambooServer bambooServer;
    private final String userName;

    public PlansPublisher(String serverUrl, String userName) {
        this.bambooServer = initBambooServer(serverUrl);
        this.userName = userName;
    }

    public void publish(List<Plan> plans) {
        plans.forEach(this::publishPlan);
    }

    private void publishPlan(Plan plan) {
        bambooServer.publish(plan);
        PlanPermissions planPermission = createPlanPermission(plan.getIdentifier());
        bambooServer.publish(planPermission);
    }

    private PlanPermissions createPlanPermission(PlanIdentifier planIdentifier) {
        Permissions permissions = new Permissions()
                .userPermissions(userName, PermissionType.ADMIN, PermissionType.EDIT)
                .loggedInUserPermissions(PermissionType.EDIT)
                .loggedInUserPermissions(PermissionType.BUILD);

        return new PlanPermissions(planIdentifier)
                .permissions(permissions);
    }
}
