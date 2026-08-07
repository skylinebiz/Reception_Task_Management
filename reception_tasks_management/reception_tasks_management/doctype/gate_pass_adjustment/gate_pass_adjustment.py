# Copyright (c) 2026, Harshit and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import _


from frappe.model.document import Document
from frappe.utils import flt
import frappe
from frappe import _


class GatePassAdjustment(Document):

    def on_submit(self):
        self.update_adjustment_qty(1)

    def on_cancel(self):
        self.update_adjustment_qty(-1)

    def update_adjustment_qty(self, multiplier):

        for row in self.items:

            original_name = frappe.db.get_value(
                "Gate Pass Item",
                {
                    "parent": row.return_reference,
                    "parenttype": "Gate Pass",
                    "item_uuid": row.item_uuid,
                },
                "name",
            )

            if not original_name:
                frappe.throw(
                    _("Original Gate Pass Item not found for Item UUID {0}")
                    .format(row.item_uuid)
                )

            original = frappe.get_doc("Gate Pass Item", original_name)

            adjustment_qty = flt(row.adjusted_qty)
			
    
            adjusted = (
                flt(original.adjusted_qty)
                + multiplier * adjustment_qty
            )

            pending = (
                flt(original.qty)
                - flt(original.return_qty)
                - adjusted
            )

            frappe.log_error(
                title="Gate Pass Adjustment Debug",
                message=f"""
Multiplier            : {multiplier}

Current Adjustment Row
----------------------
Item                  : {row.item}
Original Qty          : {row.qty}
Adjustment Qty        : {adjustment_qty}
Item UUID             : {row.item_uuid}
Return Reference      : {row.return_reference}

Original Gate Pass Item
-----------------------
Name                  : {original.name}
Parent                : {original.parent}
Parent Type           : {original.parenttype}
Item                  : {original.item}
Original Qty          : {original.qty}
Returned Qty          : {original.return_qty}
Adjusted Qty (Before) : {original.adjusted_qty}
Pending Qty (Before)  : {original.pending_qty}

Calculated
----------
Adjusted Qty (After)  : {adjusted}
Pending Qty (After)   : {pending}
"""
            )

            if adjusted < 0:
                adjusted = 0

            if adjusted > flt(original.qty):
                frappe.throw(
                    _("Adjusted Qty cannot exceed Original Qty for {0}")
                    .format(original.item)
                )

            original.adjusted_qty = adjusted

            original.pending_qty = pending

            original.db_update()