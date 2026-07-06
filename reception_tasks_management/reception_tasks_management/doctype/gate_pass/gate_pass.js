// Copyright (c) 2026, Harshit and contributors
// For license information, please see license.txt

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
    },

    direction(frm) {
        update_handover_section(frm);
    }
});

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