# Customizations Scanner Load Synchronization Design

## Goal

Run the Customizations Scanner once through the standard `bzt jira.yml` command, record its full scan duration as a Selenium KPI, and collect normal Jira user-action KPIs only while that scan is in progress.

## Scope

This design changes the Jira Customizations Scanner integration and its test configuration. It keeps the existing Confluence integration opt-in and corrects its feature guard. It does not change the target environment, snapshots, Chrome version, or ordinary Jira workload settings already present in the working tree.

## Execution model

`bzt jira.yml` continues to start JMeter and Selenium in parallel.

1. Selenium logs in, obtains WebSudo, opens the scanner, starts a scan, and waits until the configured status reports `In progress`.
2. Selenium writes a `customizations-scanner.started` marker into Taurus's per-run artifacts directory.
3. JMeter's existing setUp Thread Group waits for that marker before it releases the normal Jira Thread Group. It fails with a clear diagnostic if the marker does not appear within `customization_insights_scan_start_timeout`.
4. The normal Jira Thread Group loops only while neither a `customizations-scanner.completed` nor `customizations-scanner.failed` marker exists. This prevents a new normal-user transaction from starting after the scan has ended or failed.
5. Selenium executes the standard Jira UI actions while the scan continues. Its final scanner action waits for completion, writes the completion or failure marker, and records the full scan time as `selenium_customizations_scanner:full_scan`.
6. JMeter threads finish the action already in progress and exit at their next loop boundary when the completion or failure marker appears. Taurus then completes the normal run and retains both JMeter and Selenium KPIs.

The synchronization marker is local to the Taurus artifacts directory. This design therefore supports the Toolkit's local JMeter and Selenium execution model, where both processes run on the same load-generator host. It deliberately does not claim to coordinate distributed load generators.

## Configuration

The Jira branch remains directly runnable with `bzt jira.yml` because the scanner is enabled in its Jira configuration. The following settings control synchronization:

- `customization_insights_enabled: true` enables the plugin scenario.
- `customization_insights_scan_timeout: 1200` is the maximum permitted full-scan duration in seconds.
- `customization_insights_scan_start_timeout: 300` is the maximum period JMeter waits for Selenium to confirm that the scan started.
- `customization_insights_load_hold_for: 25m` is the JMeter and Selenium execution ceiling. It exceeds the scan timeout so normal traffic can run for the complete measured scan window.
- `customization_insights_status_selector` and `customization_insights_status_selector_type` identify the status element.
- `customization_insights_in_progress_text` and `customization_insights_completed_text` define the status transitions.

The JMeter scenario receives only the enabled flag and start timeout as properties. It uses the Taurus-provided `TAURUS_ARTIFACTS_DIR` environment variable to locate markers, so no machine-specific path is committed.

## Components and responsibilities

### Jira Selenium extension

`app/extension/jira/extension_ui.py` exposes two focused functions:

- `start_customizations_scanner(webdriver, datasets)` performs the admin session, opens the scanner, starts the scan, verifies `In progress`, and writes the start marker.
- `wait_for_customizations_scanner(webdriver, datasets)` waits for the configured completion status, writes the completion or failure marker, and reports the full-scan timer.

Status lookup is driven exclusively by the configured selector and expected text. The extension no longer depends on hard-coded scan-panel IDs or CSS success classes.

### Jira Selenium scenario

`app/selenium_ui/jira_ui.py` invokes the start action immediately after login and the wait action immediately before logout. The ordinary Selenium Jira interactions therefore execute between them, while the scan is active.

### Jira JMeter plan

`app/jmeter/jira.jmx` extends its existing setUp Thread Group with a JSR223 marker wait. The existing `actions per login` loop becomes a marker-aware while loop. It performs normal Jira actions unchanged, but stops beginning new actions after Selenium signals scan completion or failure. The plan does not add a scanner endpoint sampler to normal user traffic.

### Shared configuration and Confluence guard

`app/util/conf.py` parses the additional Jira scanner settings. The Confluence UI extension checks the same `enabled` setting and skips cleanly when the plugin is not configured, preserving the default Toolkit behavior outside this plugin branch. Jira Locust verifies its configured response assertion when explicitly selected, but it is not required for the JMeter-based scan run.

## Failure handling

- Plugin disabled: Selenium skips its custom action; JMeter uses its ordinary loop without marker gating.
- Scan cannot be started: Selenium writes the failure marker and fails with the current URL and configuration context; JMeter's setup wait fails rather than issuing normal traffic outside the required scan window.
- Scan reaches the timeout: Selenium writes the failure marker and fails the full-scan KPI; JMeter exits at the next action boundary.
- Scan finishes before the configured maximum: Selenium writes the completion marker; JMeter exits at its next action boundary, so no subsequent normal-user transaction is measured outside the scan.

## Verification

Unit tests will cover marker lifecycle, configured status lookup, scan-start failure, scan-completion failure, and the existing login-redirect retry. Static checks will validate Python syntax, YAML, and JMX XML. A Toolkit run will be considered successful only when its artifacts include the full-scan Selenium label and normal JMeter samples whose timestamps fall between scan start and completion.
