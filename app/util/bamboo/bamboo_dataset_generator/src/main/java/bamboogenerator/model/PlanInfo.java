package bamboogenerator.model;

public class PlanInfo {
    private final String planName;
    private final boolean failed;
    private final String planKey;
    private final String projectName;
    private final String projectKey;

    public PlanInfo(String planName, boolean failed, String planKey, String projectName, String projectKey) {
        this.planName = planName;
        this.failed = failed;
        this.planKey = planKey;
        this.projectName = projectName;
        this.projectKey = projectKey;
    }

    public String getPlanName() {
        return planName;
    }
    public boolean isFailed() {
        return failed;
    }

    public String getPlanKey() {
        return planKey;
    }

    public String getProjectName() {
        return projectName;
    }

    public String getProjectKey() {
        return projectKey;
    }
}
