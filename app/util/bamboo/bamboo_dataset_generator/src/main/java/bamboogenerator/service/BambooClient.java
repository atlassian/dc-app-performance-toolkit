package bamboogenerator.service;

import com.jayway.jsonpath.DocumentContext;
import com.jayway.jsonpath.JsonPath;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.utils.URIBuilder;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;

import java.net.URI;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.List;

public class BambooClient {
    private static final String AUTH_TEMPLATE = "Bearer %s";
    private static final int MAX_RESULT = 25;

    private final String serverUrl;
    private final String token;
    private final CloseableHttpClient client = HttpClients.createDefault();

    public BambooClient(String serverUrl, String token) {
        this.serverUrl = serverUrl;
        this.token = token;
    }

    public List<String> getAllPlanKeys() throws Exception {
        List<String> keys = new ArrayList<>();
        int index = 0;
        boolean hasMore = true;
        while (hasMore) {
            HttpGet request = preparePlanRequest(index);
            String body = EntityUtils.toString(client.execute(request).getEntity());

            DocumentContext context = JsonPath.parse(body);
            int size = context.read("$.plans.size");
            keys.addAll(context.read("$.plans..shortKey"));

            hasMore = keys.size() < size;
            if (hasMore) {
                index += MAX_RESULT;
            }
        }

        return keys;
    }

    private HttpGet preparePlanRequest(int index) throws URISyntaxException {
        HttpGet request = new HttpGet(buildPlanURI(index));
        request.addHeader("Authorization", String.format(AUTH_TEMPLATE, token));
        request.addHeader("Accept", "application/json");
        return request;
    }

    private URI buildPlanURI(int value) throws URISyntaxException {
        return new URIBuilder(serverUrl + "/rest/api/latest/plan")
                .addParameter("start-index", String.valueOf(value))
                .addParameter("max-result", String.valueOf(MAX_RESULT))
                .build();
    }
}
