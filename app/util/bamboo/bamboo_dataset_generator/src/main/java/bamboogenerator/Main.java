package bamboogenerator;

import bamboogenerator.service.PlansPublisher;
import bamboogenerator.service.generator.plan.PlanGenerator;
import com.atlassian.bamboo.specs.api.BambooSpec;
import com.atlassian.bamboo.specs.api.builders.plan.Plan;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;

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

    // plans per project = PLANS/PROJECTS_NUMBER
    private static final int PROJECTS_NUMBER = 100;
    private static final int PLANS = 2000;
    private static final int PERCENT_OF_FAILED_PLANS = 20;

    public static void main(String[] args) {
        long start = currentTimeMillis();
        LOG.info("Started Bamboo dataset generator");

        LOG.info("{} build plans will be generated", PLANS);
        List<Plan> plans = PlanGenerator.generate(PROJECTS_NUMBER, PLANS, PERCENT_OF_FAILED_PLANS);
        PlansPublisher plansPublisher = new PlansPublisher(BAMBOO_SERVER_URL, ADMIN_USER_NAME);
        plansPublisher.publish(plans);

        LOG.info("----------------------------------------------------\n");
        LOG.info("Elapsed Time in seconds: {}", ((currentTimeMillis() - start) / 1000));
    }


}
