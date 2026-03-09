frappe.query_reports["Spare Parts Inventory"] = {

    formatter: function (value, row, column, data, default_formatter) {

        value = default_formatter(value, row, column, data);

        if (!data) return value;

        if (data.part_name !== "TOTAL" && data.stock_qty <= data.reorder_level) {
            value = `<span style="color:red;font-weight:bold">${value}</span>`;
        }

        if (data.part_name === "TOTAL") {
            value = `<b>${value}</b>`;
        }

        return value;
    }

};