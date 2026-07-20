# Customizations Scanner Regression Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Customizations Scanner a reusable Jira performance-regression KPI: measure a complete scan under the normal Run 4 workload, while preserving the standard toolkit profile and offering a short, repeatable release-regression invocation.

**Architecture:** Keep the normal toolkit JMeter scenario as the concurrent user signal. Treat the scanner as a one-time Selenium administrative KPI rather than a weighted virtual-user action. The base Jira configuration remains the standard 45-minute Run 4; a second Taurus file replaces its execution list for a 25-minute scan-regression profile. Scanner UI code reads all status details from YAML, records a narrowly scoped `full_scan` timing metric, and does not control the JMeter workload.

**Tech Stack:** Python 3, pytest, Selenium 4.39, Taurus/BZT 1.16.51, JMeter 5.6.3, YAML

## Global Constraints

- Preserve the existing Jira host, deployment, snapshot, Chrome, and non-scanner user changes.
- Do not make scanner polling a JMeter request or normal user action. `standalone_extension` remains zero unless a separately validated end-user plugin action is added later.
- The normal JMeter workload must continue independently before, during, and after a scan. Scan success, failure, or timeout must not delay, stop, or gate it.
- The short profile must use Taurus merge replacement (`~execution`) so it contains exactly the intended JMeter and Selenium executions.
- Jira is the supported core profile. Confluence must opt out safely when the plugin is not installed.
- Delete only the known inactive, untracked `app/jmeter/modified_jira.jmx`; retain the active `app/jmeter/jira.jmx` and existing scanner tests.
- Compare scan times only against runs with the same dataset, topology, JVM, and workload profile.

---

## Task 1: Make the scanner status contract configurable and time only the full scan

**Files:**
- Modify: `app/util/conf.py`
- Modify: `app/extension/jira/extension_ui.py`
- Modify: `app/tests/test_jira_customizations_scanner.py`

- [ ] **Step 1: Write failing configuration and UI-unit tests.**

  Extend the existing scanner tests with lightweight fake WebDriver objects. Cover:

  - `CustomizationInsightsSettings` reading `status_selector_type` and `in_progress_text` from both supported YAML shapes, with explicit Jira-like values of `id`, `scan-panel-summary`, and `In progress`.
  - Scanner status lookup using the configured selector type and selector, rather than the hard-coded panel IDs or AUI CSS classes.
  - The happy path waiting until the configured in-progress text is observed and then until the configured completed text is observed.
  - A failed click/scan-start error and a completion timeout remaining failures (not silently reported as success).
  - The timing boundary: the `selenium_customizations_scanner:full_scan` timer encloses the new-scan click and completion wait, but not Jira login or navigation.

  Example fake-driver assertion:

  ```python
  assert driver.find_calls == [(By.ID, "scan-panel-summary")]
  ```

- [ ] **Step 2: Run the focused tests and confirm they fail for the intended missing behavior.**

  Run:

  ```bash
  python3 -m pytest -q app/tests/test_jira_customizations_scanner.py
  ```

  Expected before implementation: failures identify the missing settings, hard-coded status lookup, or timing boundary. If pytest is unavailable, record that environmental blocker and run `python3 -m compileall` while keeping the tests as the executable specification.

- [ ] **Step 3: Extend `CustomizationInsightsSettings`.**

  Add `status_selector_type` and `in_progress_text` fields. Parse them beside the existing `status_selector`, `completed_text`, and `scan_timeout` values in both flat and nested configuration styles. Use conservative defaults appropriate to the reusable helper (for example `css` and `In progress`); Jira supplies its exact selector type explicitly.

- [ ] **Step 4: Refactor Jira scanner status polling.**

  In `app/extension/jira/extension_ui.py`:

  - Convert configured selector type to a Selenium `By` value using the existing selector helper.
  - Read status text through `driver.find_element(by, config.status_selector)`.
  - Remove knowledge of `scan-panel-summary`, `scan-progress-container`, `aui-message-*`, and other page-specific fallback selectors from the generic polling path.
  - Wait for the configured in-progress text after clicking **New scan**, then wait for the configured completed text until `scan_timeout` expires.
  - Keep actionable exceptions that distinguish inability to start a scan from failure to complete it.

  Structure the scan body so the timer is exact:

  ```python
  @print_timing("selenium_customizations_scanner:full_scan")
  def _run_full_scan(driver, config):
      _click_new_scan(driver, config)
      _wait_until_started(driver, config)
      _wait_until_completed(driver, config)
  ```

  Keep the outer administrative timing if it is useful, but it must not replace this dedicated full-scan sample.

- [ ] **Step 5: Run focused tests and static checks.**

  Run:

  ```bash
  python3 -m pytest -q app/tests/test_jira_customizations_scanner.py
  python3 -m compileall -q app/util/conf.py app/extension/jira/extension_ui.py app/tests
  ```

  Expected: tests pass and Python compilation succeeds. Inspect `selenium.jtl` labels in a local Selenium smoke run only after the configuration wiring in Task 2 is complete.

- [ ] **Step 6: Commit the completed unit of work.**

  ```bash
  git add app/util/conf.py app/extension/jira/extension_ui.py app/tests/test_jira_customizations_scanner.py
  git commit -m "feat: measure full customizations scan duration"
  ```

## Task 2: Wire the standard Run 4 and short scan-regression Taurus profiles

**Files:**
- Modify: `app/jira.yml`
- Create: `app/jira-customizations-scanner.yml`
- Delete: `app/jmeter/modified_jira.jmx`
- Modify: `app/tests/test_jira_customizations_scanner.py`

- [ ] **Step 1: Add failing configuration-contract tests.**

  Add YAML-based tests that load the base and overlay files and assert:

  - Base Jira is the standard profile: `concurrency: 200`, `test_duration: 45m`, `ramp-up: 3m`.
  - Scanner is enabled for Jira, uses explicit `status_selector_type: id`, `status_selector: scan-panel-summary`, `in_progress_text: In progress`, `completed_text: Done`, and `scan_timeout: 1200`.
  - `standalone_extension` is `0`.
  - The overlay has a `~execution` key, `test_duration: 25m`, one standard load execution and one Selenium execution, with Selenium delayed by the base ramp-up.

- [ ] **Step 2: Run the configuration tests and confirm the current profile fails them.**

  ```bash
  python3 -m pytest -q app/tests/test_jira_customizations_scanner.py
  ```

- [ ] **Step 3: Restore the base Jira profile and clarify its scanner role.**

  Update `app/jira.yml` to set `test_duration: 45m` and `ramp-up: 3m`, leaving its deployment settings untouched. Set the configured scanner status fields from Step 1. Keep the Selenium scenario’s normal sequence and state in comments that the scanner is a one-time administrative KPI, not part of weighted normal-user traffic.

  Remove the unused scanner REST path/response assertion and corresponding JMeter properties from this file: the active `app/jmeter/jira.jmx` does not consume them, and retaining them suggests that the normal user workload polls scanner status.

- [ ] **Step 4: Add the opt-in regression overlay.**

  Create `app/jira-customizations-scanner.yml` with a Taurus merge replacement:

  ```yaml
  settings:
    env:
      test_duration: 25m

  ~execution:
    - scenario: ${load_executor}
      executor: ${load_executor}
      concurrency: ${concurrency}
      hold-for: ${test_duration}
      ramp-up: ${ramp-up}
    - scenario: selenium
      executor: selenium
      runner: pytest
      hold-for: ${test_duration}
      delay: ${ramp-up}
  ```

  Preserve any base executor fields that are required by the toolkit’s current `jira.yml`. This starts scanner Selenium after JMeter has ramped for three minutes, holds both executions for 25 minutes, and never introduces a scan-status dependency into JMeter.

- [ ] **Step 5: Remove the inactive JMX artifact safely.**

  Verify the target is the untracked `app/jmeter/modified_jira.jmx`, then delete that exact file. Do not edit or delete `app/jmeter/jira.jmx`.

- [ ] **Step 6: Validate merge and file shape.**

  Run:

  ```bash
  ruby -e 'require "yaml"; ARGV.each { |f| YAML.load_file(f) }' app/jira.yml app/jira-customizations-scanner.yml
  git diff --check
  git status --short
  ```

  If BZT is installed, inspect the merged run configuration with its non-destructive config/debug facility before starting a real environment. Confirm only the two intended executions exist and that the Selenium delay resolves to three minutes.

- [ ] **Step 7: Commit the configuration unit.**

  ```bash
  git add app/jira.yml app/jira-customizations-scanner.yml app/tests/test_jira_customizations_scanner.py
  git add -u app/jmeter/modified_jira.jmx
  git commit -m "feat: add customizations scanner regression profile"
  ```

## Task 3: Start the scanner immediately after Selenium login and make optional extensions safe

**Files:**
- Modify: `app/selenium_ui/jira_ui.py`
- Modify: `app/confluence.yml`
- Modify: `app/extension/confluence/extension_ui.py`
- Modify: `app/extension/jira/extension_locust.py`
- Create: `app/tests/test_customization_insights_extensions.py`

- [ ] **Step 1: Write failing sequence and safety tests.**

  Add tests that:

  - Stub Jira page actions and assert the scanner administrative action is invoked immediately after the standard Selenium login, before ordinary browsing actions.
  - Assert a disabled Confluence scanner action produces a pytest skip instead of attempting plugin navigation.
  - Fake a Jira Locust response and verify that, when its app-specific action is explicitly used, it accepts the configured response text and calls `failure()` when the response is not successful or the expected text is absent.

- [ ] **Step 2: Run the new tests and observe the pre-change failure.**

  ```bash
  python3 -m pytest -q app/tests/test_customization_insights_extensions.py
  ```

- [ ] **Step 3: Move the one-time scanner action to the correct Selenium position.**

  In `app/selenium_ui/jira_ui.py`, invoke the scanner test directly after the existing standard login test. Keep it a single Selenium test/action so it executes once per Selenium run. Ordinary Selenium actions can follow once the scan completes; JMeter remains the continuously active normal-user workload while scanning.

- [ ] **Step 4: Make Confluence explicitly opt out.**

  Set `customization_insights_enabled: false` in `app/confluence.yml`. In `app/extension/confluence/extension_ui.py`, check this setting before page navigation and use `pytest.skip` with a concise reason when disabled. This keeps standard Confluence runs viable without the plugin.

- [ ] **Step 5: Correct the Jira Locust optional assertion.**

  Update `app/extension/jira/extension_locust.py` to check the configured response assertion, mirroring the useful behavior already present in the Confluence extension. Treat non-200 responses or absent expected content as failures. This action remains inactive at weight zero in the supported JMeter profiles.

- [ ] **Step 6: Run extension tests and compilation.**

  ```bash
  python3 -m pytest -q app/tests/test_customization_insights_extensions.py app/tests/test_jira_customizations_scanner.py
  python3 -m compileall -q app/selenium_ui/jira_ui.py app/extension app/tests
  ```

- [ ] **Step 7: Commit the extension-safety unit.**

  ```bash
  git add app/selenium_ui/jira_ui.py app/confluence.yml app/extension/confluence/extension_ui.py app/extension/jira/extension_locust.py app/tests/test_customization_insights_extensions.py
  git commit -m "fix: isolate scanner checks from normal user load"
  ```

## Task 4: Document execution and comparison rules

**Files:**
- Modify: `docs/jira/README.md`

- [ ] **Step 1: Add operator-facing documentation.**

  Document both supported commands from the `app` directory:

  ```bash
  bzt jira.yml
  bzt jira.yml jira-customizations-scanner.yml
  ```

  Explain that the first command is normal Run 4 (200 users, 3-minute ramp, 45-minute hold) and the second is the short release-regression profile (25-minute hold, scanner Selenium delayed 3 minutes). State that it reports a one-time `selenium_customizations_scanner:full_scan` duration alongside uninterrupted JMeter availability and latency metrics.

  Include the comparison rule: use a prior release as baseline only when dataset, cluster topology, JVM, application version alignment, and selected profile are the same. Record the agreed scan-duration tolerance outside this repository or add it only once the team supplies a value.

- [ ] **Step 2: Validate the examples match configuration.**

  Re-read `app/jira.yml`, `app/jira-customizations-scanner.yml`, and the changed README together. Verify the durations, ramp, concurrency, label, and command order agree exactly.

- [ ] **Step 3: Commit the documentation unit.**

  ```bash
  git add docs/jira/README.md
  git commit -m "docs: describe customizations scanner regression run"
  ```

## Task 5: Perform end-to-end validation and handoff

**Files:**
- Verify: all files changed above

- [ ] **Step 1: Run repository-level static validation.**

  ```bash
  git diff --check
  python3 -m compileall -q app
  ruby -e 'require "yaml"; ARGV.each { |f| YAML.load_file(f) }' app/jira.yml app/jira-customizations-scanner.yml app/confluence.yml
  xmllint --noout app/jmeter/jira.jmx app/jmeter/confluence.jmx
  ```

- [ ] **Step 2: Run the focused test suite.**

  ```bash
  python3 -m pytest -q app/tests
  ```

  If the local interpreter does not have project test dependencies, use the repository’s approved Python environment if present. Otherwise report the missing dependency precisely rather than treating the tests as passed.

- [ ] **Step 3: Perform a configured-environment smoke run.**

  With a disposable Jira deployment and the Customizations Scanner plugin installed, run the short profile:

  ```bash
  cd app
  bzt jira.yml jira-customizations-scanner.yml
  ```

  Verify Selenium reports `selenium_customizations_scanner:full_scan`; scan transitions through the configured in-progress and Done texts; JMeter samples continue over the scan period; and neither scan failure nor timeout stops the JMeter execution.

- [ ] **Step 4: Inspect final scope before handoff.**

  Run `git status --short` and `git diff --check`. Confirm the inactive modified JMX is gone, all intended source/config/docs/tests are present, and unrelated user changes have not been reverted or absorbed accidentally.

- [ ] **Step 5: Request code review and present integration options.**

  Summarize the exact commands run, their results, any environment-limited checks, the scanner metric label, and the two supported BZT invocations. Use the repository’s normal review/PR flow only after the validation evidence is available.
