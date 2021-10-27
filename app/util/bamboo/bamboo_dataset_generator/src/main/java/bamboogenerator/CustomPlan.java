package bamboogenerator;

public class CustomPlan {
    private final String planName;
    private final boolean planIsFailed;
    private final String planKey;
    private final String projectName;
    private final String projectKey;

    public CustomPlan(String planName, boolean planIsFailed, String planKey, String projectName, String projectKey) {
        this.planName = planName;
        this.planIsFailed = planIsFailed;
        this.planKey = planKey;
        this.projectName = projectName;
        this.projectKey = projectKey;
    }

    public String getPlanName() {
        return planName;
    }

    public boolean isPlanIsFailed() {
        return planIsFailed;
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
