# Customizations Scanner Regression and Run 4 Design

## Goal

Provide two reusable ways to assess Customizations Scanner performance:

1. a short release-regression run that measures one full scan while Jira receives the normal Toolkit workload; and
2. the unchanged full Run 4 scalability benchmark with the plugin and its Selenium app-specific action enabled.

The short run answers whether scan duration regressed between releases and whether ordinary Jira users can still use the platform while a scan is active. Run 4 remains the longer Marketplace-style scalability measurement.

## Scope

This design changes the Jira Customizations Scanner integration and its test configuration. It retains the current plugin-seeded Jira environment and does not alter snapshots, Chrome version, or unrelated deployment settings. It adds an opt-in guard to the Confluence UI action so a toolkit environment without that plugin does not fail unexpectedly.

## Standard Run 4

`bzt jira.yml` remains the standard app-partner entry point.

- JMeter runs the ordinary Jira workload at the standard enterprise-scale profile: 200 virtual users, three-minute ramp-up, and 45-minute hold.
- Selenium runs in parallel and invokes the scanner as the Jira app-specific action.
- The scanner begins immediately after Selenium login so its full duration is observed under the JMeter workload.
- The dedicated `selenium_customizations_scanner:full_scan` timer starts when Selenium clicks **New scan** and stops only when the configured completion state is visible. Login, WebSudo, and page navigation remain separate measurements.
- JMeter is not delayed, gated, or stopped by scanner state. Normal traffic retains the normal Toolkit behavior for the full Run 4 duration.

The scanner action is a one-time administrative KPI, not a weighted virtual-user action. `standalone_extension` therefore stays at zero unless a separately validated, normal-user plugin action is added later.

## Short scanner-under-load regression run

`bzt jira.yml jira-customizations-scanner.yml` runs the same JMeter scenario and Selenium suite with a dedicated overlay configuration.

1. JMeter begins its ordinary Jira workload and ramps to 200 virtual users over three minutes.
2. The overlay delays the Selenium scenario by three minutes. Selenium then logs in, starts one scan, and records its full duration while the load generator is already at target concurrency.
3. JMeter continues normally for a 25-minute hold. This provides a two-minute buffer beyond the 20-minute scan timeout without changing the workload composition.
4. Selenium fails the run if the scanner does not reach the configured completion text within 1,200 seconds. JMeter failures, response-time changes, and success rates remain the standard Toolkit results.

The run deliberately does not make JMeter start or stop according to scanner state. Its goal is to expose user-visible degradation under representative platform traffic, not to create a tightly synchronized synthetic window.

## Configuration

`app/jira.yml` supplies the normal Run 4 values and scanner settings:

- `test_duration: 45m`
- `ramp-up: 3m`
- `customization_insights_enabled: true`
- `customization_insights_scan_timeout: 1200`
- `customization_insights_status_selector` and `customization_insights_status_selector_type`
- `customization_insights_in_progress_text` and `customization_insights_completed_text`

`app/jira-customizations-scanner.yml` is a Taurus overlay for the release-regression profile. It replaces the execution list with the same JMeter and Selenium scenarios, sets the JMeter and Selenium holds to `25m`, and delays Selenium by `3m`. Its environment overrides set `test_duration: 25m` and retain the base workload percentages and scanner settings.

## Components and responsibilities

### Jira Selenium extension

`app/extension/jira/extension_ui.py` retains one `app_specific_action(webdriver, datasets)` entry point. It:

1. creates an authenticated administrator and WebSudo session;
2. opens the configured scanner servlet and verifies the ready selector;
3. clicks the configured scan button;
4. waits for configured `In progress` text;
5. records `selenium_customizations_scanner:full_scan` while it waits for the configured completion text.

Status lookup uses `customization_insights_status_selector` and its configured selector type. The extension does not hard-code scanner panel IDs or AUI success classes.

### Jira Selenium scenario

`app/selenium_ui/jira_ui.py` places the scanner action immediately after the standard login test. The JMeter workload proceeds while the scan is active; after the scan completes, the regular Selenium actions continue and then log out as usual.

### Shared configuration and Confluence guard

`app/util/conf.py` parses the additional status selector type and in-progress text. The Confluence UI extension skips when Customization Insights is disabled. Jira Locust validates its configured response assertion when a user explicitly chooses Locust, but it is not required for either JMeter-based profile.

## Success criteria

For a release-regression comparison, use a previous-release result from the same dataset, topology, JVM settings, and workload profile. The candidate release passes when:

- `selenium_customizations_scanner:full_scan` completes within 1,200 seconds and does not exceed the agreed baseline tolerance;
- normal Jira actions maintain the Toolkit success-rate threshold during the run; and
- JMeter action timings do not show an unexplained regression against the baseline.

Run 4 uses the normal Toolkit acceptance criteria and compares the two-node result with the corresponding one-node result.

## Verification

Unit tests cover configured status lookup, the exact full-scan timer boundary, scan-start failure, scan-completion timeout, and the existing login-redirect retry. Static checks validate Python syntax, YAML, and JMX XML. A smoke run of the short profile must produce a full-scan Selenium label alongside normal JMeter Jira samples.
