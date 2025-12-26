# Track Plan: Ensure the ingestion of BCV rates using GitHub Actions and Supabase Edge Functions is functional and operational.

## Phase 1: Supabase Edge Function Development

### Goal
Develop and test the core Supabase Edge Function responsible for fetching, parsing, and storing BCV exchange rates.

### Tasks
- [x] Task: Adapt existing Supabase Edge Function for BCV rates ingestion
    - [x] Task: Modify the existing `bcv-rates` function to align with the `spec.md`.
    - [x] Task: Update the data model to store rates per currency and date.
    - [x] Task: Refactor the code to support this new data model.
- [x] Task: Create tests for the Edge Function
    - [ ] Task: Create a new test file for the `bcv-rates` function.
    - [x] Task: Write tests for data fetching, parsing, and storage logic.
- [ ] Task: Implement data fetching from BCV source
    - [ ] Task: Research and identify the official BCV data source URL and structure.
    - [ ] Task: Write code to make HTTP requests and retrieve raw data.
    - [ ] Task: Conductor - User Manual Verification 'Implement data fetching from BCV source' (Protocol in workflow.md)
- [ ] Task: Implement data parsing and validation
    - [ ] Task: Write code to parse the raw data into structured exchange rate objects.
    - [ ] Task: Implement validation logic for parsed data (e.g., data types, ranges).
    - [ ] Task: Conductor - User Manual Verification 'Implement data parsing and validation' (Protocol in workflow.md)
- [ ] Task: Implement Supabase database integration
    - [ ] Task: Define and create the `bcv_rates` table schema in Supabase.
    - [ ] Task: Write code to insert processed exchange rates into the `bcv_rates` table, ensuring idempotency.
    - [ ] Task: Conductor - User Manual Verification 'Implement Supabase database integration' (Protocol in workflow.md)
- [ ] Task: Implement error handling and logging within the Edge Function
    - [ ] Task: Add try-catch blocks for all external calls and critical operations.
    - [ ] Task: Integrate logging for successful runs, warnings, and errors.
- [ ] Task: Conductor - User Manual Verification 'Supabase Edge Function Development' (Protocol in workflow.md)

## Phase 2: GitHub Actions Integration and Scheduling

### Goal
Configure a GitHub Actions workflow to schedule and trigger the Supabase Edge Function.

### Tasks
- [ ] Task: Create GitHub Actions workflow file
    - [ ] Task: Create a new `.yml` file in `.github/workflows/` for BCV rates ingestion.
    - [ ] Task: Define the workflow trigger (e.g., daily cron schedule).
- [ ] Task: Configure environment variables for GitHub Actions
    - [ ] Task: Securely add Supabase API key and other necessary secrets to GitHub Actions.
- [ ] Task: Implement workflow step to call Supabase Edge Function
    - [ ] Task: Write workflow step to invoke the deployed Supabase Edge Function.
- [ ] Task: Test GitHub Actions workflow
    - [ ] Task: Manually trigger the workflow to verify function invocation.
    - [ ] Task: Conductor - User Manual Verification 'GitHub Actions Integration and Scheduling' (Protocol in workflow.md)

## Phase 3: Monitoring and Refinements

### Goal
Ensure the entire ingestion pipeline is stable, observable, and performant.

### Tasks
- [ ] Task: Review and enhance error alerting
    - [ ] Task: Set up notifications for GitHub Actions workflow failures.
    - [ ] Task: Implement additional alerts for Edge Function failures (if not covered by Supabase defaults).
- [ ] Task: Documentation
    - [ ] Task: Document the BCV rates ingestion process, including setup, maintenance, and troubleshooting.
- [ ] Task: Conductor - User Manual Verification 'Monitoring and Refinements' (Protocol in workflow.md)
