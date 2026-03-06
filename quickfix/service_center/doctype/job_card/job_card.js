// Copyright (c) 2026, Tarchana and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Job Card", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Job Card", {
    onload: function(frm){
        frappe.realtime.on("job_ready", function(data){
            if (data.job_card === frm.doc.name) {
                frappe.show_alert({
                    message: "Job Ready: " + data.job_card,
                    indicator: "green"
                }, 5);
            }
    })
    }
})


frappe.ui.form.on("Job Card", {

    onload: function(frm){

        frappe.call({
            method: "frappe.client.get_count",
            args: {
                doctype: "Job Card"
            },
            callback: function(r){
                console.log("Job Card Count:", r.message);
                frappe.msgprint("Job Card Count:"+ (r.message))
            }
        });

    }

})

frappe.ui.form.on("Job Card", {
    setup: function(frm) {
        frm.set_query("assigned_technician", function() {
            return {
                filters : {
                    specialization: frm.doc.device_type,
                    status: "Active"
                }
            }
        })
    },

    device_type(frm) {

        if (frm.doc.assigned_technician) {
            frm.set_value("assigned_technician", null);
        }

    }
})

frappe.ui.form.on("Job Card", {
    refresh(frm) {

        frm.dashboard.clear_headline();

        if (frm.doc.status === "Pending Diagnosis") {
            frm.dashboard.add_indicator("Pending Diagnosis", "orange");
        }

        if (frm.doc.status === "In Repair") {
            frm.dashboard.add_indicator("In Repair", "blue");
        }

        if (frm.doc.status === "Ready for Delivery") {
            frm.dashboard.add_indicator("Ready for Delivery", "green");
        }

        if (frm.doc.status === "Delivered") {
            frm.dashboard.add_indicator("Delivered", "purple");
        }

        if (frm.doc.status === "Cancelled") {
            frm.dashboard.add_indicator("Cancelled", "red");
        }

    }
});

frappe.ui.form.on("Job Card", {

    refresh(frm) {

        if (frm.doc.docstatus === 1 && frm.doc.status === "Ready for Delivery") {

            frm.add_custom_button("Mark as Delivered", () => {

                frm.set_value("status", "Delivered");
                frm.save();

            });

        }

    }

});

frappe.ui.form.on("Job Card", {

    refresh(frm) {

        if (frappe.boot.quickfix_shop_name) {

            frm.dashboard.set_headline(
                __("Shop: {0}", [frappe.boot.quickfix_shop_name])
            );

        }

    }

});

frappe.ui.form.on("Part Usage Entry", {
    quantity: function(frm, cdt, cdn) {
        calc_total_price(frm, cdt, cdn);
    },
    unit_price: function(frm, cdt, cdn) {
        calc_total_price(frm, cdt, cdn);
    }
})

function calc_total_price(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.quantity && row.unit_price) {
        frappe.model.set_value(cdt, cdn, "total_price", row.quantity * row.unit_price);
    }
}

frappe.ui.form.on("Job Card", {
    refresh(frm) {
    
    let blocked_status = ["Ready for Delivery", "Delivered", "Cancelled"]
    if (!frm.is_new() && !blocked_status.includes(frm.doc.status)) {

        frm.add_custom_button("Reject Job", function () {
            frm.trigger("reject_job");
        });

    }

    },

    reject_job(frm) {
        let dialog = new frappe.ui.Dialog({
            title: "Reject Job",
            fields: [
                {
                    label: "Rejection Reason",
                    fieldname: "reason",
                    fieldtype: "Small Text",
                    reqd: 1
                }
            ],
            primary_action_label: "Reject",
            primary_action(values) {
                frm.set_value("remarks", values.reason);
                frm.set_value("status", "Cancelled");
                frm.save();
                dialog.hide();
            }
        });

        dialog.show();
    }

})

frappe.ui.form.on("Job Card", {

    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button("Transfer Technician", function() {
                frm.trigger("transfer_technician");
            })
        }
    },

    transfer_technician(frm) {
        frappe.prompt(
            [
                {
                    label: "New Technician",
                    fieldname: "technician",
                    fieldtype: "Link",
                    options: "Technician",
                    filters: {
                        specialization: frm.doc.device_type,
                        status: "Active",
                        name: ["!=", frm.doc.assigned_technician]
                    },
                    reqd: 1
                }
            ],
            function(values) {
                frappe.confirm(
                    "Are you sure you want to transfer this job?",
                    function() {
                        frappe.call({
                            method: "quickfix.api.transfer_job",
                            args: {
                                job_card: frm.doc.name,
                                new_technician: values.technician
                            },
                            callback: function() {
                                frm.set_value("assigned_technician", values.technician);
                                frm.trigger("assigned_technician");
                                frappe.show_alert("Technician transferred successfully")
                            }
                        })
                    }
                )
            },
            "Transfer Technician",
            "Transfer"
        )
    }
})

frappe.ui.form.on("Job Card", {
    refresh(frm) {
        if (!frappe.user.has_role("QF Manager")) {
            frm.set_df_property("customer_phone", "hidden", 1);
        }
    }
});