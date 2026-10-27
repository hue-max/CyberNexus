# CyberNexus
**An Intelligent Hybrid Cyber Defense Platform**

CyberNexus monitors authorized on-premises systems and AWS resources, correlates security telemetry, assesses risk, evaluates response options using a Security Decision Digital Twin, and verifies approved defense actions.

## Project areas
- `backend/` — FastAPI application and shared services
- `database/` — SQL Server schema, migrations, and procedures
- `cloud/aws/` — AWS telemetry collectors and authorized response integrations
- `agents/` — Windows, Linux, and network telemetry agents
- `ai/` — threat detection, classification, and prediction
- `digital-twin/` — asset model, simulations, and blast-radius analysis
- `defense/` — risk engine, response, verification, and optional deception
- `dashboard/` — user interface and visualization
- `backup-recovery/` — approved file, database, and server backup/recovery
- `tests/` — integration, security, and sample-event tests
- `docs/` — architecture, diagrams, API notes, and reports
- `scripts/` — development and maintenance scripts

## Team ownership
- Team leader: AWS integration, architecture, Digital Twin, adaptive defense, and integration
- Sinan: asset discovery and monitoring
- Sri Vijay: database, backup, and recovery
- Shahan: threat detection, AI, and forensics
- Nikil: dashboard, visualization, and reports

## Development rules
1. Work on a feature branch; do not push directly to `main`.
2. Open a pull request and test before merging.
3. Coordinate API contracts and database changes before implementing them.
4. Never commit passwords, AWS keys, `.env` files, real employee files, or other sensitive data.
5. Use only authorized systems for security testing.
6. Clearly label simulated AWS events/actions; simulation is not a real cloud response.
