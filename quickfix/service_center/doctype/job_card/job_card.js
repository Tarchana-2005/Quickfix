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