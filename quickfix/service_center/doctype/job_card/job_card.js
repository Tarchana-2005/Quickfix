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

// frappe.listview_settings["Job Card"] = {
//     add_fields: ["final_amount", "priority"],
//     get_indicator(doc){
//         // if (doc.status === "In Repair") {
//         //     return ["In Repair", "orange", "status,=,In Repair"];
//         // }
//         if (doc.status === "Ready for Delivery") {
//             return ["Delivered", "green", "status,=,Delivered"];
//         }
//     }
// }

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