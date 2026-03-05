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

If a secret is placed in `common_site_config.json`, it becomes accessible to all sites in the bench. It breaks security 


The `site_config.json` file is site-specific and stores values such as `db_name`, `db_password`, and environment-based settings like `developer_mode`.

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

---
## What is the issues in using frappe.get_all in a whitelisted method that is exposed to guests or low-privilege users. Explain it in the context of permission_query_conditions

Using frappe.get_all() in a whitelisted method is unsafe because it bypasses permission_query_conditions and role-based restrictions. So, guests or low-privilege users can access all records directly from DB.

Therefore, frappe.get_list() should be used beacuse it checks permissions.

---
## Call self.save() inside on_update and see to the issues of it and explain them in the same readme_internals. Correct the pattern and explain it.

Calling `self.save()` inside `on_update()` causes infinite recursion because on_update() is already triggered during save lifecycle.
The correct approach is to update fields in validate(), before_save() to avoid re-triggering the lifecycle.

---
## If you override_doctype_class and forget to update super() - what breaks?

Calling super() is mandatory.
Even though CustomJobCard inherits from JobCard (which inherits from 
Document in Frappe core), if we override a method and don't call super(), 
the execution will not reach the parent implementation. So any core updates 
inside the parent method will not run.

---
## Why is doc_events safer than override_doctype_class for most use cases?

`doc_events` is safer than `override_doctype_calsss` because, it adds logic without replacing the core controller, so it will not block frappe core updates.

In contrast, `override_doctype_class` replaces the entire controller class. If not handled carefully (especially if `super()` is not called), it can block core behavior and increase the risk of upgrade friction.

---
## Which of the below pattern would you use and and explain why.
## doc = frappe.get_doc("QuickFix Settings", "QuickFix Settings")
## threshold = doc.low_stock_threshold
## threshold = frappe.db.get_value("QuickFix Settings", None,"low_stock_threshold")

`frappe.get_doc()` loads the full document as a Python object and fetches all fields.
It allows calling document methods and runs validations when doc.save() is used.
It is heavier and should be used when full document behavior is required.
`frappe.db.get_value()` fetches only specific field directly from the database and 
does not trigger validations or lifecycle hooks.
Since we only need one field (low_stock_threshold), `frappe.db.get_value("QuickFix Settings", "Quickfix Settings","low_stock_threshold")` is more efficient and appropriate.

---
## Multiple handler conflict:

## Register TWO validate handlers on Job Card - one in your main controller and one in doc_events. What order do they run? 

Execution Order:
1. The controller's validate() method runs first.
2. After it completes successfully, the doc_events validate handler execute.
-> Controller logic always has priority

## What happens if both raise a frappe.ValidationError?

If the controller raises a `ValidationError`, execution stops immediately and the `doc_events` handler will not run.

If the controller passes but the doc_events handler raises a ValidationError, the document will not be saved.

## Demonstrate: what happens when you register "*" AND a specific DocType handler for the same event? Do both run?

Both the handlers run.
Execution Order:
1. Controller validate()
2. Specific DocType validate handler
3. Wildcard validate handler

If any handler raises a `ValidationError`, execution stops immediately and the document will not be saved.

---

## Assest hooks
1. `app_include_js`
app_include_js loads JavaScript files globally in the Desk interface for logged-in users. It is used for navbar modifications.

2. `web_include_js`
web_include_js loads JavaScript files only on website and portal pages, including guest-access pages. It is used for frontend website behavior such as form validation, portal interactivity.

The key difference is that `app_include_js` applies to the backend Desk environment, while `web_include_js` applies to the public-facing website environment.

3. `doctype_js`
doctype_js is used to load a JavaScript file only when a specific DocType form is opened. It is used for DocType Form view customization.

3. `doctype_list_js`
doctype_list_js is used to load JavaScript only for a specific DocType’s List View.

4. `doctype_tree_js`
doctype_tree_js is used to customize the Tree View interface of hierarchical DocTypes.

5. `Build cache-busting` 
## Explain what bench build --app quickfix does and why assets need cache-busting after JS changes

bench build --app quickfix compiles and bundles frontend assets such as JavaScript and CSS files from the app’s public directory into the /assets directory used by the browser. The build process also implements cache busting by generating versioned asset files, ensuring browsers do not use outdated cached files. This is necessary after modifying JS or CSS files so that users receive the updated assets.

## Jinja Hooks
## Explain: what is the difference between a Jinja context available in Print Formats vs one available in Web Pages? Are they the same?

### Difference Between Jinja Context in Print Formats vs Website Pages

Both Print Formats and Website Pages use Jinja templates, but their context is different.

In **Print Formats**, Frappe automatically provides the document as `doc`. This allows the template to directly access fields like `doc.customer_name` or `doc.final_amount`.

In **Website Pages**, the context is **manually defined by the developer** using the `get_context()` function, where variables are added and then used in the template.

So, Print Formats get an **automatic document context**, while Website Pages use a **custom context defined by the developer**.

---

## what happens if your Custom Field has the same fieldname as a field added by a future Frappe update?

**Fieldname Collision Risk**

When creating Custom Fields in Frappe, we should use unique fieldnames. If our app creates a field with a certain name and a future Frappe update introduces a field with the same name, a conflict can occur.

For example, if our app adds a field called "device_serial" in Job Card and Frappe later adds a field with the same name, migrations may fail because two fields cannot share the same fieldname.

To avoid this, it is good practice to prefix custom fields with the app name, such as "qf_device_serial".

---
## Explain patching order: if Patch 1 creates a Custom Field and Patch 2 reads it, why must they be separate entries in patches.txt and never merged?

**Patch Ordering**

In Frappe, patches run in the sequential listed in patches.txt. If Patch 1 creates a Custom Field and Patch 2 tries to read or use that field, Patch 1 must run first.

If both changes are merged into a single patch or executed in the wrong order, Patch 2 may run before the field is created, which can cause errors like “Field not found”.

Keeping them as separate entries in patches.txt ensures that patches run step-by-step in the correct order and migrations remain stable.

---
## Making a frappe.call inside the validate client event (before_save handler) - explain why this does not work

`frappe.call` is asynchronous. However, client events like validate and before_save are synchronous, and Frappe does not wait for asynchronous responses during the save process. Because of this, the form may finish saving before the frappe.call response arrives, making the result ineffective.

For validations, it is better to use methods like `frappe.db.get_value` or `frm.set_query`.

---
## What to use: onload or refresh for async data fetches

onload  → use for one-time async setup 
refresh → use for UI updates that depend on current doc state

Both fire AFTER form is ready — so async calls work safely here.
frappe.call inside refresh is fine because user is just viewing,
not in the middle of a save operation.

---