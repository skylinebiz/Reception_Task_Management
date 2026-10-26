frappe.query_reports["Returnable Items"] = {
    filters: [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.add_days(frappe.datetime.get_today(), -30),
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1
        }
    ],

    formatter(value, row, column, data, default_formatter) {
        if (!data) {
            return default_formatter(value, row, column, data);
        }

        // Item name -> detail report with the return entries (new window)
        if (column.fieldname === "item" && value) {
            const url = frappe.router.make_url(["query-report", "Returnable Item Details"])
                + frappe.utils.make_query_string({ item_uuid: data.item_uuid });
            return `<a href="${url}" target="_blank" rel="noopener">${frappe.utils.escape_html(value)}</a>`;
        }

        return default_formatter(value, row, column, data);
    }
};

