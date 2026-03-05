frappe.listview_settings['Job Card'] = {

    get_indicator: function(doc) {

        if (doc.status === "Pending") {
            return ["Pending", "orange", "status,=,Pending"];
        }

        if (doc.status === "In Progress") {
            return ["In Progress", "blue", "status,=,In Progress"];
        }

        if (doc.status === "Ready for Delivery") {
            return ["Ready for Delivery", "green", "status,=,Ready for Delivery"];
        }

        if (doc.status === "Delivered") {
            return ["Delivered", "purple", "status,=,Delivered"];
        }

    }

};