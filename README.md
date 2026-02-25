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

## Multi-Site & Configuration

In this project, two sites were created on the same bench: `quickfix-dev.localhost` and `quickfix-prod.localhost`. This demonstrates Frappe’s multi-tenancy model, where multiple sites share the same application code but use separate databases, ensuring complete data isolation.

The `common_site_config.json` file is used for shared bench-level configuration such as `db_host`, which applies to all sites.

The `site_config.json` file is site-specific and stores values such as `db_name`, `db_password`, and environment-based settings like `developer_mode`.

`hooks.py` stores app's configurations 

Running `bench start` launches four processes:
- Web – Handles HTTP requests  
- Worker – Executes background jobs  
- Scheduler – Runs scheduled tasks  
- SocketIO – Manages real-time events
If the Worker process stops, the website will still load normally, but background tasks such as sending emails or scheduled jobs will not run until the Worker is restarted.

## Child Table Internals 

When you append a row to Job Card.parts_used and save, what 4 columns does
Frappe automatically set on the child table row?

1. parent – Stores the name of the parent document 
2. parenttype – Stores the parent DocType name 
3. parentfield – Stores the fieldname of the table in the parent 
4. idx – Stores the row position number inside the table 

These fields maintain the parent-child relationship and row ordering internally.

1) What is the DB table name for the Part Usage Entry DocType?

tabPart Usage Entry

2) If you delete row at idx=2 and re-save, what happens to idx values of remaining
rows?

Frappe automatically reorders the positions

## Renaming Task

1) Rename one of your test Technician records using the Rename Document feature.
Then check: does the assigned_technician field on linked Job Cards automatically
update? Why or why not? What does "track changes" mean in this context?

I renamed one of the Technician records using the Rename Document feature.

After renaming, the assigned_technician field in all linked Job Cards automatically updated to the new name.

This happens because assigned_technician is a Link field. Link fields store the document’s internal ID (name), and when a document is renamed, Frappe automatically updates all related references to keep the data consistent.

Track Changes simply records what was modified in a document. It keeps a history of changes (old value and new value) for auditing purposes. It does not handle the rename logic, it only logs that the rename happened.

2) Explain unique constraints: what is the difference between setting a field as "unique"
in the DocType vs doing a frappe.db.exists() check in validate()?

Marking a field as **Unique** creates a database-level constraint. The database itself prevents duplicate values, even if multiple users try to save at the same time. This is the safest way to enforce uniqueness.

Using `frappe.db.exists()` inside the `validate()` method only checks for duplicates in Python before saving. It throws an error if a matching record is found, but it does not create a database constraint.

Therefore, Using `frappe.db.exists()` only for additional business logic checks is best.
