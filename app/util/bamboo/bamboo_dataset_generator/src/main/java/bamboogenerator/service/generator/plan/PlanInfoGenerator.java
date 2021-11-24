package bamboogenerator.service.generator.plan;

import bamboogenerator.model.PlanInfo;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.stream.Collectors;

import static java.lang.Boolean.FALSE;
import static java.lang.Boolean.TRUE;

public class PlanInfoGenerator {
    private static final Logger LOG = LoggerFactory.getLogger(PlanInfoGenerator.class);
    private static final Map<Integer, String> LETTERS_BY_NUMBER = prepareLettersByNumber();

    public static List<PlanInfo> generate(int projectsNumber, int plansNumber, int failedPercent) {
        List<ArrayList<String>> projectNamesKeys = generateProjectsNameKeys(projectsNumber, plansNumber);
        List<Integer> failedPlansIndexes = generateFailedPlansIndexes(plansNumber, failedPercent);
        LOG.info("Project name keys {}", projectNamesKeys);
        LOG.info("Indexes of failed plans {}", failedPlansIndexes);

        List<PlanInfo> plans = new ArrayList<>();
        for (int i = 0; i < plansNumber; i++) {
            String formatted = String.format("%03d", i);
            String planName = formatted + " - Plan Success";
            boolean planIsFailed = FALSE;
            if (failedPlansIndexes.contains(i)) {
                planIsFailed = TRUE;
                planName = formatted + " - Plan Fail";
            }
            String planKey = "PLANKEY" + generatePlanKeySuffix(i);
            String projectName = projectNamesKeys.get(i).get(0);
            String projectKey = projectNamesKeys.get(i).get(1);
            LOG.info("Generating plan: PlanName: " + planName + ". PlanKey: " + planKey + ". " +
                    "Into the project: ProjectName: " + projectName + ". ProjectKey: " + projectKey);
            plans.add(new PlanInfo(planName, planIsFailed, planKey, projectName, projectKey));
        }

        return plans;
    }

    private static List<ArrayList<String>> generateProjectsNameKeys(int projectsNumber, int plansToGenerate) {
        while (plansToGenerate % projectsNumber != 0) {
            projectsNumber = projectsNumber - 1;
        }

        int planPerProject = plansToGenerate / projectsNumber;
        List<ArrayList<String>> projectNameKey = new ArrayList<>();

        for (int i = 1; i < projectsNumber + 1; i++) {
            String projectName = "Project " + i;
            String projectKey = "PRJ" + i;
            ArrayList<String> arr = new ArrayList<>();
            arr.add(projectName);
            arr.add(projectKey);
            projectNameKey.add(arr);
        }

        // Copy projects data to create planPerProject logic
        List<ArrayList<String>> projectNameKeys = new ArrayList<>();
        for (ArrayList<String> element : projectNameKey) {
            for (int i = 0; i < planPerProject; i++) {
                projectNameKeys.add(element);
            }
        }

        return projectNameKeys;
    }

    private static List<Integer> generateFailedPlansIndexes(int planToGenerate, int percentOfFailed) {
        int numberOfFailed = Math.round((percentOfFailed * planToGenerate) / 100f);
        List<Integer> failedPlansIndexes = new ArrayList<>();
        for (int i = 0; i <= numberOfFailed; i++) {
            while (failedPlansIndexes.size() < numberOfFailed) {
                int randomIndex = new Random().nextInt(planToGenerate - 1) + 1;
                if (!failedPlansIndexes.contains(randomIndex)) {
                    failedPlansIndexes.add(randomIndex);
                }
            }
        }

        return failedPlansIndexes;
    }

    private static Map<Integer, String> prepareLettersByNumber() {
        Map<Integer, String> map = new HashMap<>();
        map.put(0, "A");
        map.put(1, "B");
        map.put(2, "C");
        map.put(3, "D");
        map.put(4, "E");
        map.put(5, "F");
        map.put(6, "G");
        map.put(7, "H");
        map.put(8, "I");
        map.put(9, "J");

        return map;
    }

    private static String generatePlanKeySuffix(int number) {
        return String.valueOf(number)
                .chars()
                .mapToObj(Character::getNumericValue)
                .map(LETTERS_BY_NUMBER::get)
                .collect(Collectors.joining());
    }
}
