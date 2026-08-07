frappe.query_reports["Daily Gate Pass Item"] = {

    onload(report) {
        setTimeout(() => {
            if (report.datatable) {
                report.datatable.options.cellHeight = 42;
                report.datatable.refresh();
            }
        }, 100);
    },

    filters: [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.add_days(frappe.datetime.get_today(), -6),
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

        value = default_formatter(value, row, column, data);

        if (column.fieldname === "action" && value === "Make Adjustment") {
            return `
        <button
            class="btn btn-xs btn-primary make-adjustment"
            data-gate-pass="${data.gate_pass}"
            data-item="${data.item}"
            data-qty="${data.qty}">
            Make Adjustment
        </button>
    `;
        }

        return value;

    }
};


$(document).off("click", ".make-adjustment");

$(document).on("click", ".make-adjustment", function () {

    const gate_pass = $(this).data("gate-pass");
    const item = $(this).data("item");
    const qty = $(this).data("qty");

    // console.log(gate_pass, item, qty);

    frappe.new_doc("Gate Pass Adjustment", {
        gate_pass: gate_pass
    });

});
