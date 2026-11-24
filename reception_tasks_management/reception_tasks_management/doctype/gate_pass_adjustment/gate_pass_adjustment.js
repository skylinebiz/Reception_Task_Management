// Copyright (c) 2026, Harshit and contributors
// For license information, please see license.txt

frappe.ui.form.on("Gate Pass Adjustment", {
    refresh(frm) {

        const grid = frm.fields_dict.items.grid;

        grid.update_docfield_property(
            "adjusted_qty",
            "in_list_view",
            1
        );

        // Disable adding rows
        grid.cannot_add_rows = true;
        grid.wrapper.find(".grid-add-row").hide();

        frm.refresh_field("items");

        if (frm.is_new() && frm.doc.gate_pass && !frm.doc.items.length) {

            frappe.call({
                method: "reception_tasks_management.api.gatepass.get_gate_pass_items",
                args: {
                    gate_pass: frm.doc.gate_pass
                },
                callback(r) {

                    if (!r.message) return;

                    frm.clear_table("items");

                    r.message.forEach(row => {

                        let d = frm.add_child("items");

                        d.item = row.item;
                        d.qty = row.qty;
                        d.adjusted_qty = row.pending_qty;
                        d.remarks = row.remarks;
                        // Same as a return row: return_reference is the original
                        // row's uuid. The row gets its own item_uuid on save.
                        d.return_reference = row.item_uuid;
                        d.return_gate_pass = row.parent;
                    });

                    frm.refresh_field("items");

                    // Hide again after refresh
                    grid.wrapper.find(".grid-add-row").hide();
                }
            });

        }

    }
});