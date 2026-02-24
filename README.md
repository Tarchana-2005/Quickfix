### Quickfix

An frappe based app for a small electronics repair shop Quickfix

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app quickfix
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/quickfix
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

mit

## A1 & A2 – Multi-Site & Configuration

In this project, two sites were created on the same bench: `quickfix-dev.localhost` and `quickfix-prod.localhost`. This demonstrates Frappe’s multi-tenancy model, where multiple sites share the same application code but use separate databases, ensuring complete data isolation.

The `common_site_config.json` file is used for shared bench-level configuration such as `db_host`, which applies to all sites.

The `site_config.json` file is site-specific and stores values such as `db_name`, `db_password`, and environment-based settings like `developer_mode`.

Running `bench start` launches four processes:
- Web – Handles HTTP requests  
- Worker – Executes background jobs  
- Scheduler – Runs scheduled tasks  
- SocketIO – Manages real-time events
If the Worker process stops, the website will still load normally, but background tasks such as sending emails or scheduled jobs will not run until the Worker is restarted.