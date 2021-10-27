package bamboogenerator;

import bamboogenerator.AbstractSpecPlan;
import bamboogenerator.BambooBaseDataset;
import com.atlassian.bamboo.specs.api.util.EntityPropertiesBuilders;
import com.google.common.collect.Lists;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import java.util.Collection;
import java.util.List;


@RunWith(Parameterized.class)
public class PlanSpecTest {

    private static final List<AbstractSpecPlan> SPEC_PLANS = Lists.newArrayList(
            new BambooBaseDataset()
    );

    @Parameters(name = "{0}")
    public static Collection<AbstractSpecPlan> data() {
        return SPEC_PLANS;
    }

    @Parameter
    public AbstractSpecPlan plan;

    }

