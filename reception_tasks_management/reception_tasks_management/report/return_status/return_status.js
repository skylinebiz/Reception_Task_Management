frappe.query_reports["Return Status"] = {

    onload(report) {
        setTimeout(() => {
            if (report.datatable) {
                report.datatable.options.cellHeight = 42;
                report.datatable.refresh();
            }
        }, 100);
    },

    formatter(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname === "action" && value === "ADJ") {
            return `
                <button
                    class="btn btn-xs btn-primary make-adjustment"
                    data-gate-pass="${data.gate_pass}"
                    data-gate-pass-item="${data.gate_pass_item}"
                    data-item="${data.item}"
                    data-qty="${data.qty}">
                    ADJ
                </button>
            `;
        }

        return value;
    }
};

$(document).off("click", ".make-adjustment");

$(document).on("click", ".make-adjustment", function () {

    frappe.new_doc("Gate Pass Adjustment", {
        gate_pass: $(this).data("gate-pass"),
        gate_pass_item: $(this).data("gate-pass-item"),
        item: $(this).data("item"),
        qty: $(this).data("qty")
    });

});