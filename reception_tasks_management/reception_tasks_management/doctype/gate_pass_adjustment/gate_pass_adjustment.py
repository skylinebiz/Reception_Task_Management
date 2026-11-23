# Copyright (c) 2026, Harshit and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import _

from reception_tasks_management.reception_tasks_management.doctype.gate_pass.gate_pass import (
    get_original_item,
)


class GatePassAdjustment(Document):

    def validate(self):
        self.validate_gate_pass()

    def validate_gate_pass(self):
        """Adjustments are only allowed against returnable rows of submitted
        Gate Passes, and never for more than is still pending."""
        if not self.items:
            frappe.throw(_("Add at least one item to adjust."))

        for row in self.items:
            prefix = _("Row {0}").format(row.idx)

            if not row.return_reference or not row.item_uuid:
                frappe.throw(_("{0}: Gate Pass reference is missing.").format(prefix))

            if self.gate_pass and row.return_reference != self.gate_pass:
                frappe.throw(
                    _("{0}: item belongs to {1}, not {2}.")
                    .format(prefix, row.return_reference, self.gate_pass)
                )

            original = get_original_item(row.item_uuid)

            if not original or original.parent != row.return_reference:
                frappe.throw(
                    _("{0}: Gate Pass {1} is not submitted (draft, cancelled or amended) "
                      "or does not contain this item, so it cannot be adjusted.")
                    .format(prefix, frappe.bold(row.return_reference))
                )

            if not original.is_returnable:
                frappe.throw(
                    _("{0}: Item {1} in {2} is not returnable.")
                    .format(prefix, frappe.bold(original.item), original.parent)
                )

            if flt(row.adjusted_qty) < 0:
                frappe.throw(_("{0}: Adjusted Qty cannot be negative.").format(prefix))

            if flt(row.adjusted_qty) > flt(original.pending_qty):
                frappe.throw(
                    _("{0}: Adjusted Qty {1} exceeds Pending Qty {2} for {3}.")
                    .format(prefix, flt(row.adjusted_qty), flt(original.pending_qty),
                            frappe.bold(original.item))
                )

            row.return_gate_pass = original.parent

    def on_submit(self):
        self.update_adjustment_qty(1)

    def on_cancel(self):
        self.update_adjustment_qty(-1)

    def update_adjustment_qty(self, multiplier):

        for row in self.items:

            # Resolve by item_uuid against the *submitted* Gate Pass. The uuid is
            # kept across amendments, so this finds the live row (e.g. GP-1-1)
            # rather than the cancelled one the parent name may point at.
            original_row = get_original_item(row.item_uuid)

            if not original_row:
                if multiplier < 0:
                    # Original was cancelled before cancellation was blocked;
                    # nothing left to reverse.
                    continue
                frappe.throw(
                    _("Original Gate Pass Item not found for Item UUID {0}")
                    .format(row.item_uuid)
                )

            original = frappe.get_doc("Gate Pass Item", original_row.name)

            adjustment_qty = flt(row.adjusted_qty)

            adjusted = (
                flt(original.adjusted_qty)
                + multiplier * adjustment_qty
            )

            if adjusted < 0:
                adjusted = 0

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

            if multiplier > 0 and pending < 0:
                frappe.throw(
                    _("Row {0}: Adjusted Qty {1} exceeds Pending Qty {2} for {3} "
                      "(Qty {4}, Returned {5}, Already Adjusted {6}).")
                    .format(
                        row.idx, adjustment_qty, flt(original.pending_qty), original.item,
                        flt(original.qty), flt(original.return_qty), flt(original.adjusted_qty),
                    ),
                    title=_("Adjusted Qty exceeds the limit"),
                )

            original.adjusted_qty = adjusted

            original.pending_qty = pending

            original.db_update()
