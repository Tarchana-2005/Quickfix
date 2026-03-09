import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data)

    return columns, data, None, chart, summary


def get_columns():

    columns = [
        {
            "label": "Technician",
            "fieldname": "technician",
            "fieldtype": "Link",
            "options": "Technician",
            "width": 180
        },
        {
            "label": "Total Jobs",
            "fieldname": "total_jobs",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "label": "Completed",
            "fieldname": "completed",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "label": "Avg Turnaround Days",
            "fieldname": "avg_turnaround",
            "fieldtype": "Float",
            "width": 150
        },
        {
            "label": "Revenue",
            "fieldname": "revenue",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "Completion Rate %",
            "fieldname": "completion_rate",
            "fieldtype": "Percent",
            "width": 150
        }
    ]

    # Dynamic device columns
    device_types = frappe.get_all("Device Type", fields=["name"])

    for dt in device_types:
        columns.append({
            "label": dt.name,
            "fieldname": dt.name.lower().replace(" ", "_"),
            "fieldtype": "Int",
            "width": 120
        })

    return columns


def get_data(filters):

    jobs = frappe.get_list(
        "Job Card",
        fields=[
            "assigned_technician",
            "status",
            "creation",
            "delivery_date",
            "final_amount",
            "device_type"
        ],
        filters={
            "creation": ["between", [filters.get("from_date"), filters.get("to_date")]]
        },
        limit_page_length=0
    )

    device_types = frappe.get_all("Device Type", fields=["name"])

    technician_map = {}

    for job in jobs:

        tech = job.assigned_technician

        if not tech:
            continue

        if tech not in technician_map:

            technician_map[tech] = {
                "technician": tech,
                "total_jobs": 0,
                "completed": 0,
                "turnaround_days": [],
                "revenue": 0
            }

            # initialize device counters
            for dt in device_types:
                field = dt.name.lower().replace(" ", "_")
                technician_map[tech][field] = 0

        technician_map[tech]["total_jobs"] += 1

        # device type count
        if job.device_type:
            field = job.device_type.lower().replace(" ", "_")
            if field in technician_map[tech]:
                technician_map[tech][field] += 1

        # completed jobs
        if job.status == "Delivered":
            technician_map[tech]["completed"] += 1

            if job.delivery_date:
                days = (job.delivery_date - job.creation.date()).days
                technician_map[tech]["turnaround_days"].append(days)

        technician_map[tech]["revenue"] += job.final_amount or 0

    data = []

    for tech in technician_map.values():

        avg_days = 0
        if tech["turnaround_days"]:
            avg_days = sum(tech["turnaround_days"]) / len(tech["turnaround_days"])

        completion_rate = 0
        if tech["total_jobs"]:
            completion_rate = (tech["completed"] / tech["total_jobs"]) * 100

        row = {
            "technician": tech["technician"],
            "total_jobs": tech["total_jobs"],
            "completed": tech["completed"],
            "avg_turnaround": avg_days,
            "revenue": tech["revenue"],
            "completion_rate": completion_rate
        }

        # add device counts
        for dt in device_types:
            field = dt.name.lower().replace(" ", "_")
            row[field] = tech[field]

        data.append(row)

    return data


def get_chart(data):

    technicians = []
    total_jobs = []
    completed_jobs = []

    for row in data:
        technicians.append(row["technician"])
        total_jobs.append(row["total_jobs"])
        completed_jobs.append(row["completed"])

    chart = {
        "data": {
            "labels": technicians,
            "datasets": [
                {"name": "Total Jobs", "values": total_jobs},
                {"name": "Completed Jobs", "values": completed_jobs}
            ]
        },
        "type": "bar"
    }

    return chart


def get_summary(data):

    total_jobs = sum(d["total_jobs"] for d in data)
    total_revenue = sum(d["revenue"] for d in data)

    best_tech = None
    best_rate = 0

    for d in data:
        if d["completion_rate"] > best_rate:
            best_rate = d["completion_rate"]
            best_tech = d["technician"]

    summary = [
        {
            "label": "Total Jobs",
            "value": total_jobs,
            "indicator": "Blue"
        },
        {
            "label": "Total Revenue",
            "value": total_revenue,
            "indicator": "Green"
        },
        {
            "label": "Best Technician",
            "value": best_tech,
            "indicator": "Purple"
        }
    ]

    return summary