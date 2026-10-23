frappe.query_reports["Returnable Item Details"] = {
    filters: [
        {
            fieldname: "item_uuid",
            label: __("Item UUID"),
            fieldtype: "Data",
            reqd: 1
        }
    ]
};
