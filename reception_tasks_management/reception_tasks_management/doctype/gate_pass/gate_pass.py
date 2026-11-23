# Copyright (c) 2026, Harshit and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import _


def get_original_item(item_uuid):
    """Return the submitted Gate Pass row identified by `item_uuid`, with
    its parent's direction / company, or None."""
    rows = frappe.db.sql("""
        SELECT
            gpi.name, gpi.item, gpi.is_returnable, gpi.qty,
            gpi.return_qty, gpi.adjusted_qty, gpi.pending_qty,
            gp.name AS parent, gp.direction, gp.company
        FROM `tabGate Pass Item` gpi
        INNER JOIN `tabGate Pass` gp
            ON gp.name = gpi.parent
            AND gpi.parenttype = 'Gate Pass'
        WHERE
            gpi.item_uuid = %s
            AND gp.docstatus = 1
        LIMIT 1
    """, item_uuid, as_dict=True)

    return rows[0] if rows else None


class GatePass(Document):
    def before_insert(self):
        # A duplicated Gate Pass must not inherit the source's row identities,
        # otherwise two submitted passes share an item_uuid and returns can be
        # booked against the wrong one. Amendments keep them on purpose.
        if not self.amended_from:
            for row in self.items:
                row.item_uuid = None
                if not row.return_reference:
                    row.return_qty = 0
                    row.adjusted_qty = 0

    def before_save(self):
        self.set_item_uuids()

        old_rows = {}

        if self.amended_from:
            old_doc = frappe.get_doc("Gate Pass", self.amended_from)
            old_rows = {d.item_uuid: d for d in old_doc.items}

            for row in self.items:
                old = old_rows.get(row.item_uuid)
                if old:
                    row.return_qty = flt(old.return_qty)
                    row.adjusted_qty = flt(old.adjusted_qty)
                    row.pending_qty = (
                        flt(row.qty)
                        - flt(old.return_qty)
                        - flt(old.adjusted_qty)
                    )

                    old.return_qty = row.return_qty
                    old.adjusted_qty = row.adjusted_qty
                    old.pending_qty = row.pending_qty
                    old.db_update()

        for row in self.items:

            old = old_rows.get(row.item_uuid)

            if old:
                row.return_qty = flt(old.return_qty)
                row.adjusted_qty = flt(old.adjusted_qty)
                row.pending_qty = (
                    flt(row.qty)
                    - flt(row.return_qty)
                    - flt(row.adjusted_qty)
                )

                if row.pending_qty < 0:
                    frappe.throw(
                        _("Row {0}: Qty {1} cannot be less than already Returned ({2}) "
                          "+ Adjusted ({3}) for {4}.")
                        .format(row.idx, flt(row.qty), flt(row.return_qty),
                                flt(row.adjusted_qty), frappe.bold(row.item))
                    )

            elif row.is_returnable and not row.return_reference:
                row.return_qty = 0
                row.adjusted_qty = 0
                row.pending_qty = row.qty

    def set_item_uuids(self):
        """Give every row a unique item_uuid of the form `<name>-NNN`.

        Numbers continue after the highest one already used in this document
        (instead of using the row idx), so deleting and re-adding rows can
        never produce two rows with the same uuid.
        """
        prefix = f"{self.name}-"
        seen = set()
        last_no = 0

        for row in self.items:
            if not row.item_uuid or row.item_uuid in seen:
                row.item_uuid = None
                continue

            seen.add(row.item_uuid)
            suffix = row.item_uuid[len(prefix):] if row.item_uuid.startswith(prefix) else ""
            if suffix.isdigit():
                last_no = max(last_no, int(suffix))

        for row in self.items:
            if not row.item_uuid:
                last_no += 1
                row.item_uuid = f"{prefix}{last_no:03d}"

    def on_submit(self):
        self.update_return_qty(1)

    def before_cancel(self):
        self.validate_not_referenced()

    def on_cancel(self):
        self.update_return_qty(-1)

    def validate_not_referenced(self):
        """Block cancellation while a draft or submitted Gate Pass (return) or
        Gate Pass Adjustment still points at this document's items.

        `return_reference` is a Data field holding the original row's
        `item_uuid`, so Frappe's standard link check does not catch it.
        """
        item_uuids = [d.item_uuid for d in self.items if d.item_uuid]

        references = []

        if item_uuids:
            references += frappe.db.sql("""
                SELECT DISTINCT 'Gate Pass' AS doctype, gp.name, gp.docstatus
                FROM `tabGate Pass Item` gpi
                INNER JOIN `tabGate Pass` gp
                    ON gp.name = gpi.parent
                    AND gpi.parenttype = 'Gate Pass'
                WHERE
                    gp.docstatus < 2
                    AND gp.name != %(name)s
                    AND gpi.return_reference IN %(uuids)s
            """, {"name": self.name, "uuids": tuple(item_uuids)}, as_dict=True)

        # Adjustments point at the Gate Pass by name and at the row by item_uuid.
        # The uuid survives amendments, so an adjustment made on GP-1 still
        # counts against GP-1-1 and must block cancelling it.
        references += frappe.db.sql("""
            SELECT DISTINCT 'Gate Pass Adjustment' AS doctype, gpa.name, gpa.docstatus
            FROM `tabGate Pass Adjustment` gpa
            LEFT JOIN `tabGate Pass Item` gpi
                ON gpi.parent = gpa.name
                AND gpi.parenttype = 'Gate Pass Adjustment'
            WHERE
                gpa.docstatus < 2
                AND (
                    gpa.gate_pass = %(name)s
                    OR gpi.return_reference = %(name)s
                    OR gpi.item_uuid IN %(uuids)s
                )
        """, {"name": self.name, "uuids": tuple(item_uuids) or ("",)}, as_dict=True)

        if references:
            links = "<br>".join(
                "{0} ({1})".format(
                    frappe.utils.get_link_to_form(d.doctype, d.name),
                    _("Submitted") if d.docstatus == 1 else _("Draft"),
                )
                for d in references
            )
            frappe.throw(
                _("Cannot cancel {0} because it is referenced in the following document(s). "
                  "Cancel or delete them first:<br>{1}").format(frappe.bold(self.name), links),
                title=_("Linked Documents Exist"),
                exc=frappe.LinkExistsError,
            )

    def update_return_qty(self, multiplier):

        for row in self.items:

            if not row.return_reference:
                continue

            original = get_original_item(row.return_reference)

            if not original:
                if multiplier < 0:
                    # The original was cancelled earlier (before cancellation
                    # was blocked); nothing left to reverse.
                    continue
                frappe.throw(_("Original item not found: {0}").format(row.return_reference))

            original = frappe.get_doc("Gate Pass Item", original.name)

            returned = flt(original.return_qty) + multiplier * flt(row.qty)

            if returned < 0:
                returned = 0

            if multiplier > 0 and returned + flt(original.adjusted_qty) > flt(original.qty):
                returnable = (
                    flt(original.qty) - flt(original.return_qty) - flt(original.adjusted_qty)
                )
                frappe.throw(
                    "<b>{row_no}:</b> {idx}<br>"
                    "<b>{item_name}:</b> {item} ({reference})<br>"
                    "<b>{original_qty}:</b> {qty} | <b>{returnable_qty}:</b> {returnable}".format(
                        row_no=_("Row No"),
                        item_name=_("Item Name"),
                        original_qty=_("Original Qty"),
                        returnable_qty=_("Returnable"),
                        idx=row.idx,
                        item=frappe.utils.escape_html(row.item or original.item),
                        reference=frappe.utils.escape_html(original.parent),
                        qty=flt(original.qty),
                        returnable=returnable,
                    ),
                    title=_("Return Qty exceeds the limit"),
                )

            original.return_qty = returned

            original.pending_qty = (
                flt(original.qty)
                - flt(original.return_qty)
                - flt(original.adjusted_qty)
            )

            original.db_update()


    def validate(self):
        self.validate_items()
        self.validate_return_references()

    def validate_items(self):
        # Remove completely blank rows
        self.items = [
            row for row in self.items
            if row.item or flt(row.qty) or row.remarks
        ]

        for row in self.items:
            if not row.item and not row.return_reference:
                frappe.throw(_("Item Name is mandatory in row {0}.").format(row.idx))

            if flt(row.qty) < 0:
                frappe.throw(_("Qty cannot be negative in row {0}.").format(row.idx))

            if (row.return_reference or row.is_returnable) and flt(row.qty) <= 0:
                frappe.throw(
                    _("Qty must be greater than 0 in row {0} for returnable / return items.")
                    .format(row.idx)
                )

    def validate_return_references(self):
        """Server-side check of what a return row points at (the dialog
        filters these, but rows can also come from the API or manual edits)."""
        for row in self.items:
            if not row.return_reference:
                row.return_gate_pass = None
                continue

            original = get_original_item(row.return_reference)
            prefix = _("Row {0}").format(row.idx)

            if row.is_returnable:
                frappe.throw(
                    _("{0}: A return row cannot itself be marked returnable.").format(prefix)
                )

            if not original:
                frappe.throw(
                    _("{0}: Referenced item {1} was not found in any submitted Gate Pass.")
                    .format(prefix, frappe.bold(row.return_reference))
                )

            if original.parent == self.name:
                frappe.throw(_("{0}: A Gate Pass cannot return its own items.").format(prefix))

            if not original.is_returnable:
                frappe.throw(
                    _("{0}: Item {1} in {2} is not returnable.")
                    .format(prefix, frappe.bold(original.item), original.parent)
                )

            if original.direction == self.direction:
                frappe.throw(
                    _("{0}: {1} is also an {2} Gate Pass; a return must be in the opposite direction.")
                    .format(prefix, original.parent, self.direction)
                )

            if self.company and original.company != self.company:
                frappe.throw(
                    _("{0}: {1} belongs to company {2}, not {3}.")
                    .format(prefix, original.parent, original.company, self.company)
                )

            # Link to the original Gate Pass so Frappe's linked-document checks
            # and the "Cancel All Documents" dialog see this return.
            row.return_gate_pass = original.parent
