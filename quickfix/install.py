import frappe

def after_install():
    create_default_device_types()
    create_default_quickfix_settings()
    quickfix_property_setter()
    frappe.msgprint("Quickfix installed successfully with default setup")

def create_default_device_types():
    device_types = ["SmartPhone", "Laptop", "Tablet"]

    for device in device_types:
        if not frappe.db.exists("Device Type", device):
            frappe.get_doc({
                "doctype": "Device Type",
                "device_type": device
            }).insert()

def create_default_quickfix_settings():
    if not frappe.db.exists("QuickFix Settings", "QuickFix Settings"):
        frappe.get_doc({
            "doctype": "QuickFix Settings",
            "shop_name": "Quickfix",
            "manager_email": "tarchana.tech@gmail.com",
            "default_labour_charge": 500,
            "low_stock_alert": 1
        }).insert()

def quickfix_property_setter():

    if not frappe.db.exists(
        "Property Setter",
        {"doc_type": "Job Card", "field_name": "remarks", "property": "bold"}
    ):
    
        frappe.make_property_setter({
            "doctype": "Property Setter",
            "doc_type": "Job Card",
            "field_name": "remarks",
            "property": "bold",
            "value": "1",
            "property_type": "Check"
        })

        frappe.db.commit()

    