// Copyright (c) 2026, Harshit and contributors
// For license information, please see license.txt

frappe.ui.form.on("Gate Pass Adjustment", {
    refresh(frm) {

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

                        // Original issued qty (read only)
                        d.qty = row.qty;

                        // Quantity to adjust
                        d.adjusted_qty = row.pending_qty;

                        d.remarks = row.remarks;
                        d.return_reference = row.parent;
                        d.item_uuid = row.item_uuid;
                    });

                    frm.refresh_field("items");
                }
            });

        }

    }
});