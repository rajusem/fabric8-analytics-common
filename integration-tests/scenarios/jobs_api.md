# Feature: Jobs API
- Scenario: Check the /api/v1/readiness response
- Scenario: Check the /api/v1/liveness response
- Scenario: Check the API entry point
- Scenario: Check the API entry point
- Scenario: Check that job type 'all' is supported
- Scenario: Check that job type 'failed' is supported
- Scenario: Check that job type 'user' is supported
- Scenario: Check that improper job type is checked
- Scenario: Check initial number of jobs
- Scenario: Check that new job can be posted with state paused
- Scenario: Check that multiple jobs can be posted with state paused
- Scenario: Check that job with given ID can be posted via API
- Scenario: Check that job with given ID is really registered
- Scenario: Check that jobs are not replaced
- Scenario: Check that jobs can be deleted
- Scenario: Check that nonexistent job can't be deleted
- Scenario: Check that job w/o ID can't be deleted
- Scenario: Check that job status can be changed
- Scenario: Check wrong status behaviour
- Scenario: Check setting status for wrong job behaviour
- Scenario: Check job service state manipulation
- Scenario: Check job service state set to the same value
- Scenario: Check if improper job service state is detected properly
- Scenario: Check if new job service state is checked
- Scenario: Check the API call to clean all failed jobs
- Scenario: Check the logout endpoint accessed without authorization token
- Scenario: Check the logout endpoint accessed with authorization token
- Scenario: Check the redirection for the generate-token endpoint
