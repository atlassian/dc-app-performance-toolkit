package bamboogenerator;

import bamboogenerator.model.PlanInfo;
import bamboogenerator.service.BambooClient;
import bamboogenerator.service.PlansPublisher;
import bamboogenerator.service.generator.plan.PlanGenerator;
import bamboogenerator.service.generator.plan.PlanInfoGenerator;
import com.atlassian.bamboo.specs.api.BambooSpec;
import com.atlassian.bamboo.specs.api.builders.plan.Plan;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

import static bamboogenerator.service.BambooServerInitializer.getToken;
import static java.lang.System.currentTimeMillis;


/**
 * Plan configuration for Bamboo.
 *
 * @see <a href="https://confluence.atlassian.com/display/BAMBOO/Bamboo+Specs">Bamboo Specs</a>
 */
@BambooSpec
public class Main {
    private static final Logger LOG = LoggerFactory.getLogger(Main.class);

    private static final String BAMBOO_SERVER_URL = "http://0.0.0.0:8085";
    private static final String ADMIN_USER_NAME = "admin";

    // NOTE: Please make sure you haven't changed these values after initial run
    // in case you need another configuration you have to start from clean dataset
    private static final int PROJECTS_NUMBER = 100;
    private static final int PLANS = 2000; // plans per project = PLANS/PROJECTS_NUMBER
    private static final int PERCENT_OF_FAILED_PLANS = 20;

    public static void main(String[] args) throws Exception {
        long start = currentTimeMillis();
        LOG.info("Started Bamboo dataset generator");
        LOG.info("{} build plans will be generated", PLANS);

        List<PlanInfo> planInfoList = PlanInfoGenerator.generate(PROJECTS_NUMBER, PLANS, PERCENT_OF_FAILED_PLANS);
        checkIfThereAreOtherPlansOnServer(planInfoList);
        List<Plan> plans = PlanGenerator.generate(planInfoList);

        PlansPublisher plansPublisher = new PlansPublisher(BAMBOO_SERVER_URL, ADMIN_USER_NAME);
        plansPublisher.publish(plans);

        LOG.info("----------------------------------------------------\n");
        LOG.info("Elapsed Time in seconds: {}", ((currentTimeMillis() - start) / 1000));
    }

    private static void checkIfThereAreOtherPlansOnServer(List<PlanInfo> planInfoList) throws Exception {
        Set<String> generatedKeys = planInfoList.stream()
                .map(PlanInfo::getPlanKey)
                .collect(Collectors.toSet());

        List<String> keysFromServer = new BambooClient(BAMBOO_SERVER_URL, getToken()).getAllPlanKeys();
        if (keysFromServer.isEmpty()) {
            return;
        }

        keysFromServer.removeAll(generatedKeys);
        if (!keysFromServer.isEmpty()) {
            throw new RuntimeException("There are " + keysFromServer.size()
                    + " plans on server that were not generated."
                    + " Keys " + keysFromServer);
        }
    }

}
