# Setup note (moved)

This file has been superseded by `SETUP.md` at the repository root.
If you are looking for setup-specific configuration or guidance, see
`SETUP.md`.
- Flask web server on port 5000
- Dependencies managed via uv package manager

## Dependencies
- Flask - Web framework for the dashboard
- pandas - Data manipulation
- loguru - Logging
- schedule - Task scheduling
- python-dotenv - Environment variable management
- pytest - Testing framework
- PySimpleGUI - GUI components

## Running the Application
The Flask dashboard is automatically started via the configured workflow and runs on port 5000. The dashboard displays:
- Account balance
- Active trades with profit/loss
- Market trends and payouts
- Bot logs

## Deployment
The application is configured for autoscale deployment, which is suitable for this stateless web dashboard.

## Recent Changes
- 2025-11-02: Initial Replit setup
  - Installed Python dependencies
  - Configured Flask app to bind to 0.0.0.0:5000
  - Set up workflow for Flask dashboard
  - Configured deployment settings
