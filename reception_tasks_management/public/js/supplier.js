frappe.ui.form.on("Supplier", {
    onload(frm) {
        if (frappe.route_options?.is_transporter) {
            frm.set_value("is_transporter", 1);
        }
    }
});