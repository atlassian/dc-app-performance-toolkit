package bamboogenerator.service.generator.plan;

import bamboogenerator.model.PlanInfo;
import com.atlassian.bamboo.specs.api.builders.Variable;
import com.atlassian.bamboo.specs.api.builders.plan.Job;
import com.atlassian.bamboo.specs.api.builders.plan.Plan;
import com.atlassian.bamboo.specs.api.builders.plan.Stage;
import com.atlassian.bamboo.specs.api.builders.plan.artifact.Artifact;
import com.atlassian.bamboo.specs.api.builders.project.Project;
import com.atlassian.bamboo.specs.builders.repository.git.GitRepository;
import com.atlassian.bamboo.specs.builders.task.CheckoutItem;
import com.atlassian.bamboo.specs.builders.task.ScriptTask;
import com.atlassian.bamboo.specs.builders.task.TestParserTask;
import com.atlassian.bamboo.specs.builders.task.VcsCheckoutTask;
import com.atlassian.bamboo.specs.model.task.TestParserTaskProperties;

import java.util.List;
import java.util.stream.Collectors;

import static bamboogenerator.service.generator.plan.InlineBodies.BODY_FAIL;
import static bamboogenerator.service.generator.plan.InlineBodies.BODY_SUCCESS;

public class PlanGenerator {
    private static final int TEST_COUNT = 1000;
    private static final String RESULT_NAME_FAIL = "failed.xml";
    private static final String RESULT_NAME_SUCCESS = "success.xml";

    public static List<Plan> generate(List<PlanInfo> planInfoList) {
        return planInfoList.stream()
                .map(PlanGenerator::createPlan)
                .collect(Collectors.toList());
    }

    private static Plan createPlan(PlanInfo planInfo) {
        boolean isFailedPlan = planInfo.isFailed();
        return new Plan(new Project().name(planInfo.getProjectName())
                .key(planInfo.getProjectKey()), planInfo.getPlanName(), planInfo.getPlanKey())
                .description("DCAPT Bamboo test build plan")
                .planRepositories(new GitRepository()
                        .name("dcapt-test-repo")
                        .url("https://bitbucket.org/atlassianlabs/dcapt-bamboo-test-repo.git")
                        .branch("master"))
                .variables(new Variable("stack_name", ""))
                .stages(new Stage("Stage 1")
                        .jobs(new Job("Job 1", "JB1")
                                .tasks(
                                        new VcsCheckoutTask()
                                                .description("Checkout repository task")
                                                .cleanCheckout(true)
                                                .checkoutItems(new CheckoutItem()
                                                        .repository("dcapt-test-repo").path("dcapt-test-repo")),
                                        new ScriptTask()
                                                .description("Run Bash code")
                                                .interpreterBinSh()
                                                .inlineBody("for i in $(seq 1 1000); do date=$(date -u); echo $date >> results.log; echo $date; sleep 0.06; done"),
                                        new ScriptTask()
                                                .description("Write XML test results")
                                                .interpreterBinSh()
                                                .inlineBody(isFailedPlan
                                                        ? String.format(BODY_FAIL, TEST_COUNT, TEST_COUNT, TEST_COUNT)
                                                        : String.format(BODY_SUCCESS, TEST_COUNT, TEST_COUNT))
                                )
                                .finalTasks(new TestParserTask(TestParserTaskProperties.TestType.JUNIT)
                                        .description("Unit test results parser task")
                                        .resultDirectories(isFailedPlan ? RESULT_NAME_FAIL : RESULT_NAME_SUCCESS)
                                )
                                .artifacts(new Artifact("Test Reports")
                                        .location(".")
                                        .copyPattern("*.log"))));
    }
}
