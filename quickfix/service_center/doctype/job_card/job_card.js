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
                })
            }
    })
    }
})