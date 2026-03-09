import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data()

    # Summary calculations
    total_parts = len(data)

    below_reorder = sum(
        1 for d in data if d["stock_qty"] <= d["reorder_level"]
    )

    total_inventory_value = sum(
        d["total_value"] for d in data
    )

    # Total row calculations
    total_stock = sum(d["stock_qty"] for d in data)
    total_value = sum(d["total_value"] for d in data)

    # Add TOTAL row
    data.append({
        "part_name": "TOTAL",
        "part_code": "",
        "compatible_device_type": "",
        "stock_qty": total_stock,
        "reorder_level": "",
        "unit_cost": "",
        "selling_price": "",
        "margin_percent": "",
        "total_value": total_value
    })

    report_summary = [
        {
            "label": "Total Parts",
            "value": total_parts,
            "indicator": "Blue"
        },
        {
            "label": "Below Reorder",
            "value": below_reorder,
            "indicator": "Red"
        },
        {
            "label": "Total Inventory Value",
            "value": total_inventory_value,
            "indicator": "Green",
            "datatype": "Currency"
        }
    ]

    return columns, data, None, None, report_summary


def get_columns():
    return [
        {
            "label": "Part Name",
            "fieldname": "part_name",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": "Part Code",
            "fieldname": "part_code",
            "fieldtype": "Data",
            "width": 110
        },
        {
            "label": "Device Type",
            "fieldname": "compatible_device_type",
            "fieldtype": "Link",
            "options": "Device Type",
            "width": 120
        },
        {
            "label": "Stock Qty",
            "fieldname": "stock_qty",
            "fieldtype": "Float",
            "width": 90
        },
        {
            "label": "Reorder Level",
            "fieldname": "reorder_level",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": "Unit Cost",
            "fieldname": "unit_cost",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": "Selling Price",
            "fieldname": "selling_price",
            "fieldtype": "Currency",
            "width": 110
        },
        {
            "label": "Margin %",
            "fieldname": "margin_percent",
            "fieldtype": "Percent",
            "width": 90
        },
        {
            "label": "Total Value",
            "fieldname": "total_value",
            "fieldtype": "Currency",
            "width": 120
        }
    ]


def get_data():

    parts = frappe.get_all(
        "Spare Part",
        fields=[
            "part_name",
            "part_code",
            "compatible_device_type",
            "stock_qty",
            "reorder_level",
            "unit_cost",
            "selling_price"
        ]
    )

    data = []

    for p in parts:

        margin = 0
        if p.unit_cost and p.selling_price:
            margin = ((p.selling_price - p.unit_cost) / p.unit_cost) * 100

        total_value = (p.stock_qty or 0) * (p.unit_cost or 0)

        data.append({
            "part_name": p.part_name,
            "part_code": p.part_code,
            "compatible_device_type": p.compatible_device_type,
            "stock_qty": p.stock_qty,
            "reorder_level": p.reorder_level,
            "unit_cost": p.unit_cost,
            "selling_price": p.selling_price,
            "margin_percent": round(margin, 2),
            "total_value": round(total_value, 2)
        })

    return data