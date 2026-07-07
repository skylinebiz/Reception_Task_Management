# Copyright (c) 2026, Harshit and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class GatePass(Document):
    def before_save(self):
        old_rows = {}

        if self.amended_from:
            old_doc = frappe.get_doc("Gate Pass", self.amended_from)
            old_rows = {d.item_uuid: d for d in old_doc.items}

            for row in self.items:
                old = old_rows.get(row.item_uuid)
                if old:
                    row.return_qty = flt(old.return_qty)
                    row.pending_qty = flt(row.qty) - flt(old.return_qty)

                    # Keep the old row in sync as well
                    old.return_qty = row.return_qty
                    old.pending_qty = row.pending_qty
                    old.db_update()

        for row in self.items:

            old = old_rows.get(row.item_uuid)

            if old:
                row.return_qty = flt(old.return_qty)
                row.pending_qty = flt(row.qty) - flt(row.return_qty)
            else:
                if not row.item_uuid:
                    row.item_uuid = f"{self.name}-{row.idx:03d}"

                if row.is_returnable and not row.return_reference:
                    row.return_qty = 0
                    row.pending_qty = row.qty

    def on_submit(self):
        self.update_return_qty(1)

    def on_cancel(self):
        self.update_return_qty(-1)

    def update_return_qty(self, multiplier):
        for row in self.items:
            if not row.return_reference:
                continue

            original_name = frappe.db.sql("""
                SELECT gpi.name
                FROM `tabGate Pass Item` gpi
                INNER JOIN `tabGate Pass` gp
                    ON gp.name = gpi.parent
                WHERE
                    gpi.item_uuid = %s
                    AND gp.docstatus = 1
                ORDER BY gp.creation DESC
                LIMIT 1
            """, row.return_reference)

            if not original_name:
                frappe.throw(f"Original item not found: {row.return_reference}")

            original = frappe.get_doc("Gate Pass Item", original_name[0][0])

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
