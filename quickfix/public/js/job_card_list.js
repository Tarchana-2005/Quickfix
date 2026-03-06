frappe.listview_settings["Job Card"] = {

    add_fields: ["status", "final_amount", "priority"],
    has_indicator_for_draft: true,

    get_indicator: function (doc) {

        if (doc.status === "Draft") {
            return ["Draft", "grey", "status", "Draft"];
        }
        if (doc.status === "Pending Diagnosis") {
            return ["Pending Diagnosis", "orange", "status", "Pending Diagnosis"];
        }
        if (doc.status === "Awaiting Customer Approval") {
            return ["Awaiting Customer Approval", "yellow", "status", "Awaiting Customer Approval"];
        }
        if (doc.status === "In Repair") {
            return ["In Repair", "blue", "status", "In Repair"];
        }
        if (doc.status === "Ready for Delivery") {
            return ["Ready for Delivery", "green", "status", "Ready for Delivery"];
        }
        if (doc.status === "Delivered") {
            return ["Delivered", "purple", "status", "Delivered"];
        }
        if (doc.status === "Cancelled") {
            return ["Cancelled", "red", "status", "Cancelled"];
        }

    },

    formatters: {
        final_amount: function(value, field, doc) {
            if (!value) {
                return "-"
            }
            return format_currency(value, "INR");
        },

        priority: function(value, field, doc) {
            const colors = {
                "Normal": "green",
                "High": "orange",
                "Urgent": "red"
            };

            const color = colors[value] || "grey";
            return `<span style="color: ${color}; font-weight: 600;">${value}</span>`;
        }
    },

    button: {
        show: function(doc) {
            return doc.status === "In Repair";
        },

        get_label: function() {
            return "Mark Ready";
        },

        get_description: function(doc) {
            return `Mark ${doc.name} as Ready for Delivery`
        },

        action: function(doc) {
            frappe.confirm(
                `Mark ${doc.name} as Ready for Delivery?`,
                
                function() {
                    frappe.call({
                        method: "frappe.client.set_value",
                        args: {
                            doctype: "Job Card",
                            name: doc.name,
                            fieldname: "status",
                            value: "Ready for Delivery"
                        },

                        callback: function(r) {
                            if (!r.exc) {

                                frappe.show_alert({
                                    message: `${doc.name} marked as Ready for Delivery`,
                                    indicator: "green"
                                }, 4);

                                cur_list.refresh();
                            }
                        }
                    })
                }
            )
        }
    }

};