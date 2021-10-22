package bamboogenerator;

import com.atlassian.bamboo.specs.api.BambooSpec;
import com.atlassian.bamboo.specs.api.builders.Variable;
import com.atlassian.bamboo.specs.api.builders.plan.Plan;
import com.atlassian.bamboo.specs.api.builders.plan.Stage;
import com.atlassian.bamboo.specs.api.builders.project.Project;
import com.atlassian.bamboo.specs.util.BambooServer;
import com.atlassian.bamboo.specs.util.SimpleTokenCredentials;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.*;

import static bamboogenerator.Jobs.getDefaultJob;
import static org.apache.commons.lang3.StringUtils.isBlank;


/**
 * Plan configuration for Bamboo.
 *
 * @see <a href="https://confluence.atlassian.com/display/BAMBOO/Bamboo+Specs">Bamboo Specs</a>
 */
@BambooSpec
public class BambooBaseDataset extends AbstractSpecPlan {

    /**
     * Run 'main' to publish your plan.
     */
    public static void main(String[] args) throws IOException {
        long start = System.currentTimeMillis();
        int planToGenerate = Integer.parseInt(args[0]);
        boolean startGenerationFromScratch = Boolean.TRUE;
        if (!startGenerationFromScratch){
            int existingPlansNumber = getExistingPlans();
            System.out.println("Bamboo instance already has "+ existingPlansNumber);
            planToGenerate = planToGenerate - existingPlansNumber;
        }
        System.out.println(planToGenerate + " build plans will be generated");
        int percentOfFailed = 20;
        List<ArrayList<String>> projectNamesKeys = generateProjectsNameKeys(100, planToGenerate);
        List<Integer> failedPlansIndexes = generateFailedPlansIndexes(planToGenerate, percentOfFailed);
        System.out.println("Indexes of failed plans to debug: " + failedPlansIndexes);
        System.out.println(projectNamesKeys);
        List<CustomPlan> plans = new ArrayList<>();
        for(int i = 0; i < planToGenerate; i++) {
            String formatted = String.format("%03d", i);
            String planName = formatted + " - Plan Success";
            boolean planIsFailed = Boolean.FALSE;
            if (failedPlansIndexes.contains(i)) {
                planIsFailed = Boolean.TRUE;
                planName = formatted + " - Plan Fail";
            }
            String planKey = generateRandomString(7);
            String projectName = projectNamesKeys.get(i).get(0);
            String projectKey = projectNamesKeys.get(i).get(1);
            System.out.println("\nPublishing plan: PlanName: " + planName + ". PlanKey: " + planKey + ". " +
                    "Into the project: ProjectName: " + projectName + ". ProjectKey: " + projectKey);
            plans.add(new CustomPlan(planName, planIsFailed, planKey, projectName, projectKey));
        }
        BambooServer bambooServer = initBambooServer();
        plans.forEach(plan -> new BambooBaseDataset().publishPlan(plan.getPlanName(),
                plan.getPlanKey(), plan.getProjectName(), plan.getProjectKey(), plan.isPlanIsFailed(), bambooServer));

        long end = System.currentTimeMillis();
        System.out.println("----------------------------------------------------\n");
        System.out.println("Elapsed Time in seconds: "+ ((end-start)/1000));
    }


    public static BambooServer initBambooServer() {
        String token = getToken();
        if (token == null) {
            return new BambooServer(BAMBOO_SERVER_URL);
        }

        return new BambooServer(BAMBOO_SERVER_URL, new SimpleTokenCredentials(token));
    }

    private static String getToken() {
        try {
            String token = System.getenv(BAMBOO_TOKEN);
            if (isBlank(token)) {
                throw new RuntimeException("Env variable " + BAMBOO_TOKEN + " is not set or empty");
            }

            return token;
        } catch (Throwable t) {
            System.out.println("Can't find token");
            System.out.println("Error while getting token"+ t);
        }

        return null;
    }

    private static int getExistingPlans() throws IOException {
        URL url = new URL(AbstractSpecPlan.BAMBOO_SERVER_URL+"/rest/api/latest/search/plans");
        System.out.println(url);
        HttpURLConnection con = (HttpURLConnection) url.openConnection();
        String auth = "admin:admin";
        byte[] encodedAuth = Base64.getEncoder().encode(auth.getBytes(StandardCharsets.UTF_8));
        String authHeaderValue = "Basic " + new String(encodedAuth);
        con.setRequestProperty("Authorization", authHeaderValue);
        con.setRequestProperty("Accept", "application/json");
        InputStream inputStream = con.getInputStream();
        ObjectMapper objectmapper = new ObjectMapper();
        Map<?, ?> map = objectmapper.readValue(inputStream, Map.class);
        Integer size = (Integer) map.get("size");
        return size;
    }

    private static List<Integer> generateFailedPlansIndexes(int planToGenerate, int percentOfFailed) {
        int numberOfFailed = Math.round(percentOfFailed*planToGenerate/100);
        List<Integer> failedPlansIndexes = new ArrayList<>();
        for (int i=0; i<=numberOfFailed; i++) {
            while (failedPlansIndexes.size() < numberOfFailed) {
                Random rand = new Random();
                int randomIndex = rand.nextInt(planToGenerate-1) + 1;
                if (!failedPlansIndexes.contains(randomIndex) ) {
                    failedPlansIndexes.add(randomIndex);
                }
            }
        }
        return failedPlansIndexes;
    }

    private static String generateRandomString(int length) {
        String AlphaNumericString = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        String letters = "";
        for (int i = 0; i < length; i++) {
            int index = (int)(AlphaNumericString.length() * Math.random());
            letters = letters + AlphaNumericString.charAt(index);
        }
        return letters;
    }

    private static List<ArrayList<String>> generateProjectsNameKeys(int projectsNumber, int plansToGenerate) {
        while (plansToGenerate % projectsNumber != 0) {
            projectsNumber = projectsNumber - 1;
        }
        int planPerProject = plansToGenerate / projectsNumber;
        List<ArrayList<String>> projectNameKey = new ArrayList<ArrayList<String>>();

        for (int i = 1; i < projectsNumber+1; i++) {
            String projectName = "Project " + Integer.toString(i);
            String projectKey = "PRJ"+Integer.toString(i);
            ArrayList<String> arr = new ArrayList<String>();
            arr.add(projectName);
            arr.add(projectKey);
            projectNameKey.add(arr);
        }
        // Copy projects data to create planPerProject logic
        List<ArrayList<String>> projectNameKeys = new ArrayList<ArrayList<String>>();
        for (ArrayList element: projectNameKey) {
            for (int i = 0; i<planPerProject; i++) {
                projectNameKeys.add(element);
            }
        }

        return projectNameKeys;

    }

    @Override
    public Plan createPlan(String planName,
                           String planKey,
                           String projectName,
                           String projectKey,
                           Boolean isFailed) {
        return new Plan(new Project().name(projectName).key(projectKey.toUpperCase(Locale.ROOT)), planName, planKey)
                .description("DCAT Bamboo test build plan")
                .linkedRepositories("dcapt-test-repo")
                .variables(new Variable("stack_name", ""))
                .stages(
                        new Stage("Stage 1")
                                .jobs(
                                        getDefaultJob("Job 1", "JB1", isFailed, 1000)
                                )
);
    }

}
