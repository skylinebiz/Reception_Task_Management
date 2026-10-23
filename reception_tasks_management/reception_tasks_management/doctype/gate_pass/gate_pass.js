// Copyright (c) 2026, Harshit and contributors
// For license information, please see license.txt

frappe.ui.form.on("Gate Pass", {
    onload(frm) {
        if (frm.is_new()) {
            frm.set_value("date", frappe.datetime.get_today());
        }
    },

    setup(frm) {
        if (!$("#gate-pass-css").length) {
            $("<style id='gate-pass-css'>")
                .text(`
                    .handover-in {
                        background: #d9f7db !important;
                        border-left: 5px solid #22f72c !important;
                        border-radius: 8px;
                        padding: 10px;
                    }

                    .handover-out {
                        background: #fae7ea !important;
                        border-left: 5px solid #c62828 !important;
                        border-radius: 8px;
                        padding: 10px;
                    }
                `)
                .appendTo("head");
        }
        frm.set_query("handover_tofrom", () => {
            return {
                query: "reception_tasks_management.api.reception_person.reception_person_query"
            };
        });

        frm.set_query("handover_place", () => {
            return {
                query: "reception_tasks_management.api.reception_person.reception_person_query"
            };
        });
    },

    refresh(frm) {
        frm.fields_dict.items.grid.update_docfield_property(
            "adjusted_qty",
            "in_list_view",
            0
        );
        frm.refresh_field("items");
        toggle_return_reference_column(frm);

        update_handover_section(frm);

        if (frm.doc.docstatus === 0) {
            frm.add_custom_button(__("Get Returnable Items"), () => {
                if (!frm.doc.direction) {
                    frappe.msgprint(__("Please select Direction first."));
                    return;
                }
                open_get_items_dialog(frm);
            });
        }
    },

    direction(frm) {
        update_handover_section(frm);
    },
});

frappe.ui.form.on("Gate Pass Item", {
    items_remove(frm) {
        toggle_return_reference_column(frm);
    },
});

// Show the Return Reference column in the items grid only while at least
// one row carries a return reference.
function toggle_return_reference_column(frm) {
    const grid = frm.fields_dict.items && frm.fields_dict.items.grid;
    if (!grid) return;

    const show = (frm.doc.items || []).some(d => d.return_reference) ? 1 : 0;
    const df = grid.docfields.find(d => d.fieldname === "return_reference");
    if (!df || cint(df.in_list_view) === show) return;

    grid.update_docfield_property("return_reference", "in_list_view", show);
    grid.reset_grid();
}

// frappe.ui.form.on("Gate Pass Item", {
//     form_render(frm, cdt, cdn) {
//         // lock_linked_item_names(frm);
//     },

//     items_add(frm) {
//         // lock_linked_item_names(frm);
//     },
// });

// Rows populated via "Get Returnable Items" carry a return_reference;
// their item name must follow the original gate pass and cannot be edited.
// function lock_linked_item_names(frm) {
//     const grid = frm.fields_dict.items && frm.fields_dict.items.grid;
//     if (!grid) return;

//     const apply = () => {
//         (grid.grid_rows || []).forEach(grid_row => {
//             const linked = !!(grid_row.doc && grid_row.doc.return_reference);
//             grid_row.toggle_editable("item", !linked);
//         });
//     };

//     apply();
//     // rows of a freshly routed new doc are drawn just after refresh
//     setTimeout(apply, 0);
// }

function update_handover_section(frm) {
    const sections = ["handover_section", "items_section"];

    sections.forEach(fieldname => {
        const section = frm.fields_dict[fieldname];
        if (!section) return;

        const wrapper = $(section.wrapper);

        wrapper.removeClass("handover-in handover-out");

        if (frm.doc.direction === "IN") {
            wrapper.addClass("handover-in");
        } else if (frm.doc.direction === "OUT") {
            wrapper.addClass("handover-out");
        }
    });
}

function open_get_items_dialog(frm) {
    const search_direction = frm.doc.direction === "IN" ? "OUT" : "IN";
    const company = frm.doc.company

    const dialog = new frappe.ui.Dialog({
        title: __("Get Returnable Items"),
        size: "extra-large",
        fields: [
            {
                fieldname: "items",
                fieldtype: "Table",
                label: __("Returnable Items"),
                cannot_add_rows: true,
                in_place_edit: false,
                fields: [
                    {
                        fieldname: "gate_pass",
                        fieldtype: "Link",
                        options: "Gate Pass",
                        read_only: 1,
                        in_list_view: 1,
                        label: "Gate Pass",
                        columns: 2
                    },
                    {
                        fieldname: "item",
                        fieldtype: "Data",
                        read_only: 1,
                        in_list_view: 1,
                        label: "Item",
                        columns: 2
                    },
                    {
                        fieldname: "tofrom_full_name",
                        fieldtype: "Data",
                        label: "Handover To/From",
                        read_only: 1,
                        in_list_view: 1,
                        columns: 2
                    },
                    {
                        fieldname: "place_full_name",
                        fieldtype: "Data",
                        label: "Place",
                        read_only: 1,
                        in_list_view: 1,
                        columns: 2
                    },
                    {
                        fieldname: "date",
                        fieldtype: "Date",
                        label: "Date",
                        read_only: 1,
                        in_list_view: 1,
                        columns: 2
                    },
                    {
                        fieldname: "qty",
                        fieldtype: "Float",
                        label: "Challan Qty",
                        read_only: 1,
                        in_list_view: 1,
                        columns: 2
                    },
                    {
                        fieldname: "pending_qty",
                        fieldtype: "Float",
                        label: "Pending Qty",
                        read_only: 1,
                        in_list_view: 1,
                        columns: 2
                    },
                    {
                        fieldname: "return_qty",
                        fieldtype: "Float",
                        label: "Return Qty",
                        in_list_view: 1,
                        default: 0,
                        columns: 2
                    },
                    {
                        fieldname: "remarks",
                        fieldtype: "Data",
                        label: __("Remarks"),
                        read_only: 1,
                        columns: 2
                    },
                ]
            }
        ],

        primary_action_label: __("Get Items"),

        primary_action() {

            frappe.call({
                method: "reception_tasks_management.api.gatepass.get_pending_return_items",
                args: {
                    direction: frm.doc.direction,
                    company: company,
                    search: dialog.get_value("search")
                },
                callback(r) {
                    dialog.fields_dict.items.df.data = r.message || [];
                    dialog.fields_dict.items.grid.refresh();
                }
            });

        },

        secondary_action_label: __("Populate"),

        secondary_action() {

            const rows = dialog.fields_dict.items.grid.get_data();

            const items = [];

            rows.forEach(r => {
                const qty = flt(r.return_qty);

                if (!qty) return;

                if (qty > r.pending_qty) {
                    frappe.throw(
                        __("Return Qty cannot exceed Pending Qty for {0}", [r.item])
                    );
                }

                items.push({
                    item: r.item,
                    qty: qty,
                    pending_qty: r.pending_qty,
                    return_reference: r.item_uuid,
                    remarks: r.remarks
                });
            });

            if (!items.length) {
                frappe.msgprint(__("Enter Return Qty for at least one item."));
                return;
            }

            if (!frm.is_new()) {
                // Existing draft: append to the current form instead of creating a new doc
                const existing = new Set(
                    (frm.doc.items || []).map(d => d.return_reference).filter(Boolean)
                );

                // drop a single empty placeholder row, if any
                (frm.doc.items || [])
                    .filter(d => !d.item && !flt(d.qty) && !d.remarks)
                    .forEach(d => frappe.model.clear_doc(d.doctype, d.name));

                items.forEach(d => {
                    if (existing.has(d.return_reference)) return;

                    const row = frm.add_child("items");
                    row.item = d.item;
                    row.qty = d.qty;
                    row.pending_qty = d.pending_qty;
                    row.return_reference = d.return_reference;
                    row.remarks = d.remarks;
                });

                frm.refresh_field("items");
                toggle_return_reference_column(frm);
                frm.dirty();
                dialog.hide();
                return;
            }

            const doc = frappe.model.get_new_doc("Gate Pass");

            doc.direction = frm.doc.direction;
            doc.company = company
            items.forEach(d => {
                const row = frappe.model.add_child(doc, "Gate Pass Item", "items");

                row.item = d.item;
                row.qty = d.qty;
                row.pending_qty = d.pending_qty;
                row.return_reference = d.return_reference;
                row.remarks = d.remarks
            });

            dialog.hide();

            frappe.set_route("Form", "Gate Pass", doc.name);
        }
    });

    dialog.show();
}
