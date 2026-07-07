# Copyright (c) 2026, Harshit and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class GatePass(Document):
    def before_save(self):
        for row in self.items:
            if not row.item_uuid:
                row.item_uuid = f"{self.name}-{row.idx:03d}"

            if row.is_returnable and not row.return_reference:
                row.pending_qty = row.qty
                row.return_qty = 0

    def on_submit(self):
        self.update_return_qty(1)

    def on_cancel(self):
        self.update_return_qty(-1)

    def update_return_qty(self, multiplier):
        for row in self.items:
            if not row.return_reference:
                continue

            original_name = frappe.db.get_value(
                "Gate Pass Item",
                {"item_uuid": row.return_reference},
                "name"
            )

            if not original_name:
                frappe.throw(f"Original item not found: {row.return_reference}")

            original = frappe.get_doc("Gate Pass Item", original_name)

            returned = flt(original.return_qty) + multiplier * flt(row.qty)

            if returned < 0:
                returned = 0

            if returned > flt(original.qty):
                frappe.throw(
                    f"Returned Qty cannot exceed Original Qty for {original.item}"
                )

            original.return_qty = returned
            original.pending_qty = flt(original.qty) - returned

            original.db_update()
