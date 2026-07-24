// Copyright (c) 2026, Harshit and contributors
// For license information, please see license.txt

frappe.ui.form.on("Transporter Entry", {
    refresh(frm) {
        frm.set_query("transporter", function () {
            return {
                filters: {
                    is_transporter: 1
                }
            };
        });

        frm.fields_dict.supplier.get_new_doc = () => {
            frappe.route_options = {
                is_transporter: 1
            };
            frappe.new_doc("Supplier");
        };
    }
});
