package bamboogenerator;

import com.atlassian.bamboo.specs.api.builders.plan.Job;
import com.atlassian.bamboo.specs.api.builders.plan.artifact.Artifact;
import com.atlassian.bamboo.specs.builders.task.CheckoutItem;
import com.atlassian.bamboo.specs.builders.task.ScriptTask;
import com.atlassian.bamboo.specs.builders.task.VcsCheckoutTask;

import static bamboogenerator.Tasks.getTestParserTask;
import static bamboogenerator.Tasks.writeTestXMLResults;

public class Jobs {

    public static Job getDefaultJob(String jobName, String jobKey, boolean failed, int testCount) {
        return new Job(jobName, jobKey)
                .tasks(
                        new VcsCheckoutTask()
                                .description("Checkout repository task")
                                .cleanCheckout(true)
                                .checkoutItems(new CheckoutItem()
                                        .repository("dcapt-test-repo").path("dcapt-test-repo")),
                        new ScriptTask()
                                .description("Run Bash code")
                                .interpreterBinSh()
                                .inlineBody("for i in $(seq 1 1000); do date=`date -u`; echo $date >> results.log; echo $date; sleep 0.06; done"),
                        writeTestXMLResults(failed, testCount)
                )
                .finalTasks(getTestParserTask(failed))
                .artifacts(
                        new Artifact("Test Reports")
                                .location(".")
                                .copyPattern("*.log"));

    };
}
