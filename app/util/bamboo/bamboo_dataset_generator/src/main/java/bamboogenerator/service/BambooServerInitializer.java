package bamboogenerator.service;

import com.atlassian.bamboo.specs.util.BambooServer;
import com.atlassian.bamboo.specs.util.SimpleTokenCredentials;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import static org.apache.commons.lang3.StringUtils.isBlank;

public class BambooServerInitializer {
    private static final Logger LOG = LoggerFactory.getLogger(BambooServerInitializer.class);
    private static final String BAMBOO_TOKEN = "BAMBOO_TOKEN";

    public static BambooServer initBambooServer(String serverUrl) {
        String token = getToken();
        if (token == null) {
            return new BambooServer(serverUrl);
        }

        return new BambooServer(serverUrl, new SimpleTokenCredentials(token));
    }

    public static String getToken() {
        String token = System.getenv(BAMBOO_TOKEN);
        if (isBlank(token)) {
            LOG.warn("Env variable " + BAMBOO_TOKEN + " is not set or empty");
            return null;
        }

        return token;

    }
}
