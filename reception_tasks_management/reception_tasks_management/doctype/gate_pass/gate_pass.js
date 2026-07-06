// Copyright (c) 2026, Harshit and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Gate Pass", {
//     setup(frm) {
//         if (!$("#gate-pass-css").length) {
//             $("<style id='gate-pass-css'>")
//                 .text(`
//                     .handover-in {
//                         background: #d9f7db !important;
//                         border-left: 5px solid #22f72c !important;
//                         border-radius: 8px;
//                         padding: 10px;
//                     }

//                     .handover-out {
//                         background: #fae7ea !important;
//                         border-left: 5px solid #c62828 !important;
//                         border-radius: 8px;
//                         padding: 10px;
//                     }
//                 `)
//                 .appendTo("head");
//         }
//     },

//     // refresh(frm) {
//     //     update_handover_section(frm);

//     //     // if (!frm.is_new()) return;
//     //     frm.add_custom_button(__("Get Items"), () => {
//     //         open_get_items_dialog(frm);
//     //     });
//     // },

//     refresh(frm) {

//         update_handover_section(frm);
//         frm.add_custom_button(__("Get Items"), () => {
//             open_get_items_dialog(frm);
//         });
//         if (!frm.is_new()) {
//             return;
//         }

//         if (frm.__route_items_loaded) {
//             return;
//         }

//         if (!frappe.route_options) {
//             return;
//         }

//         frm.__route_items_loaded = true;

//         const route = frappe.route_options;

//         if (route.direction) {
//             frm.set_value("direction", route.direction);
//         }

//         if (route.return_items) {

//             const items = JSON.parse(route.return_items);

//             frm.clear_table("items");

//             items.forEach(d => {

//                 let row = frm.add_child("items");

//                 row.item = d.item;
//                 row.qty = d.qty;
//                 row.pending_qty = d.pending_qty;
//                 row.return_reference = d.return_reference;
//                 row.is_returnable = d.is_returnable;
//             });

//             frm.refresh_field("items");
//         }

//         frappe.route_options = null;
//     },

//     direction(frm) {
//         update_handover_section(frm);
//     },

//     // onload(frm) {

//     //     if (!frm.is_new()) return;
//     //     if (!frappe.route_options) return;

//     //     const route = frappe.route_options;

//     //     if (route.direction) {
//     //         frm.set_value("direction", route.direction);
//     //     }

//     //     if (route.return_items) {

//     //         frm.clear_table("items");

//     //         route.return_items.forEach(d => {

//     //             let row = frm.add_child("items");

//     //             row.item = d.item;
//     //             row.qty = d.qty;
//     //             row.pending_qty = d.pending_qty;
//     //             row.return_reference = d.return_reference;
//     //             row.is_returnable = d.is_returnable;
//     //         });

//     //         frm.refresh_field("items");
//     //     }

//     //     frappe.route_options = null;
//     // }
// });

frappe.ui.form.on("Gate Pass", {
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
    },

    refresh(frm) {
        update_handover_section(frm);

        frm.add_custom_button(__("Get Items"), () => {
            open_get_items_dialog(frm);
        });

        populate_route_items(frm);
    },

    direction(frm) {
        update_handover_section(frm);
    }
});

function populate_route_items(frm) {
    console.log('populating items');

    if (!frm.is_new()) return;

    if (frm.__route_items_loaded) return;

    if (!frappe.route_options?.return_items) return;

    frm.__route_items_loaded = true;

    const route = frappe.route_options;
    console.log(route);

    if (route.direction) {
        frm.set_value("direction", route.direction);
    }

    const items = JSON.parse(route.return_items);

    console.log(items);

    frm.clear_table("items");

    items.forEach(d => {
        const row = frm.add_child("items");

        row.item = d.item;
        row.qty = d.qty;
        row.pending_qty = d.pending_qty;
        row.return_reference = d.return_reference;
        row.is_returnable = d.is_returnable;
    });

    frm.refresh_field("items");

    frappe.route_options = null;
}

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

    const dialog = new frappe.ui.Dialog({
        title: __("Get Returnable Items"),
        size: "extra-large",
        fields: [
            {
                fieldname: "direction",
                fieldtype: "Select",
                label: __("Direction"),
                options: ["IN", "OUT"],
                default: search_direction,
                reqd: 1,
                change() {
                    load_items();
                }
            },
            {
                fieldname: "search",
                fieldtype: "Data",
                label: __("Search"),
                change() {
                    load_items();
                }
            },
            {
                fieldname: "items",
                fieldtype: "Table",
                label: __("Returnable Items"),
                cannot_add_rows: true,
                in_place_edit: true,
                fields: [
                    // {
                    // 	fieldname: "select",
                    // 	fieldtype: "Check",
                    // 	in_list_view: 1,
                    // 	label: ""
                    // },
                    {
                        fieldname: "gate_pass",
                        fieldtype: "Link",
                        options: "Gate Pass",
                        read_only: 1,
                        in_list_view: 1,
                        label: "Gate Pass"
                    },
                    {
                        fieldname: "item",
                        fieldtype: "Link",
                        options: "Item",
                        read_only: 1,
                        in_list_view: 1,
                        label: "Item"
                    },
                    // {
                    // 	fieldname: "item_uuid",
                    // 	fieldtype: "Data",
                    // 	read_only: 1,
                    // 	in_list_view: 1,
                    // 	label: "Reference"
                    // },
                    {
                        fieldname: "return_qty",
                        fieldtype: "Float",
                        label: "Return Qty",
                        in_list_view: 1,
                        default: 0
                    },
                    {
                        fieldname: "pending_qty",
                        fieldtype: "Float",
                        label: "Pending Qty",
                        read_only: 1,
                        in_list_view: 1
                    },
                    {
                        fieldname: "returned_qty",
                        fieldtype: "Float",
                        label: "Returned",
                        read_only: 1,
                        in_list_view: 1
                    }
                ]
            }
        ],

        primary_action_label: __("Get Items"),

        primary_action() {

            const rows = dialog.fields_dict.items.grid.get_data();

            rows
                .filter(r => cint(r.select))
                .forEach(r => {

                    let row = frm.add_child("items");

                    row.item = r.item;
                    row.qty = r.pending_qty;
                    row.pending_qty = r.pending_qty;
                    row.return_reference = r.item_uuid;
                    row.is_returnable = r.is_returnable;
                });

            frm.refresh_field("items");
            dialog.hide();
        },

        secondary_action_label: __("Make Gate Pass"),

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
                    is_returnable: r.is_returnable
                });
            });

            if (!items.length) {
                frappe.msgprint(__("Enter Return Qty for at least one item."));
                return;
            }

            const doc = frappe.model.get_new_doc("Gate Pass");

            doc.direction = dialog.get_value("direction");

            items.forEach(d => {
                const row = frappe.model.add_child(doc, "Gate Pass Item", "items");

                row.item = d.item;
                row.qty = d.qty;
                row.pending_qty = d.pending_qty;
                row.return_reference = d.return_reference;
                row.is_returnable = d.is_returnable;
            });

            dialog.hide();

            frappe.set_route("Form", "Gate Pass", doc.name);
        }
    });

    dialog.show();

    load_items();

    function load_items() {

        frappe.call({
            method: "reception_tasks_management.api.gatepass.get_pending_return_items",
            args: {
                direction: dialog.get_value("direction"),
                search: dialog.get_value("search")
            },
            callback(r) {

                dialog.fields_dict.items.df.data = r.message || [];
                dialog.fields_dict.items.grid.refresh();
            }
        });
    }
}


function add_items_to_current_gate_pass() {

    const rows = dialog.fields_dict.items.grid.get_data();

    rows.forEach(r => {

        const qty = flt(r.return_qty);

        if (!qty) return;

        if (qty > r.pending_qty) {
            frappe.throw(
                __("Return Qty for {0} cannot exceed Pending Qty.", [r.item])
            );
        }

        let row = frm.add_child("items");

        row.item = r.item;
        row.qty = qty;
        row.return_reference = r.item_uuid;
        row.is_returnable = r.is_returnable;
    });

    frm.refresh_field("items");
    dialog.hide();
}

// function open_gate_pass_dialog(frm) {
// 	const search_direction = frm.doc.direction === "IN" ? "OUT" : "IN";

// 	new frappe.ui.form.MultiSelectDialog({
// 		doctype: "Gate Pass",
// 		target: frm,

// 		setters: {
// 			direction: search_direction
// 		},

// 		add_filters_group: 1,
// 		date_field: "date",

// 		get_query() {
// 			return {
// 				query: "reception_tasks_management.api.gatepass.get_gate_passes_for_return",
// 				filters: {
// 					direction: search_direction
// 				}
// 			};
// 		},

// 		action(selections) {
// 			if (!selections.length) {
// 				frappe.msgprint(__("Please select at least one Gate Pass"));
// 				return;
// 			}

// 			frappe.call({
// 				method: "reception_tasks_management.api.gatepass.get_returnable_items",
// 				args: {
// 					gate_passes: selections
// 				},
// 				callback(r) {
// 					if (!r.message) return;

// 					r.message.forEach(item => {
// 						const row = frm.add_child("items");

// 						row.item = item.item;
// 						row.qty = item.pending_qty;
// 						row.pending_qty = item.pending_qty;
// 						row.return_reference = item.item_uuid;
// 						row.is_returnable = item.is_returnable;
// 					});

// 					frm.refresh_field("items");
// 				}
// 			});

// 			cur_dialog.hide();
// 		}
// 	});
// }


function make_new_gate_pass() {

    const rows = dialog.fields_dict.items.grid.get_data();

    const items = [];

    rows.forEach(r => {

        const qty = flt(r.return_qty);

        if (!qty) return;

        if (qty > r.pending_qty) {
            frappe.throw(
                __("Return Qty for {0} cannot exceed Pending Qty.", [r.item])
            );
        }

        items.push({
            item: r.item,
            qty: qty,
            return_reference: r.item_uuid,
            is_returnable: r.is_returnable
        });
    });

    if (!items.length) {
        frappe.throw(__("Enter Return Qty for at least one item."));
    }

    frappe.call({
        method: "reception_tasks_management.api.gatepass.make_return_gate_pass",
        args: {
            direction: dialog.get_value("direction"),
            items: items
        },
        callback(r) {
            if (!r.message) return;

            dialog.hide();

            frappe.set_route(
                "Form",
                "Gate Pass",
                r.message
            );
        }
    });
}