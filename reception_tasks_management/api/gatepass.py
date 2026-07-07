import frappe
from frappe import _

@frappe.whitelist()
def get_pending_return_items(direction, search=None):

    direction = "OUT" if direction == "IN" else "IN"

    filters = {
        "direction": direction
    }

    condition = ""

    if search:
        condition = """
            AND (
                gpi.item LIKE %(search)s
                OR gp.name LIKE %(search)s
                OR gpi.item_uuid LIKE %(search)s
            )
        """
        filters["search"] = f"%{search}%"

    return frappe.db.sql(f"""
        SELECT
            gp.name AS gate_pass,
            gp.handover_tofrom,
            gp.handover_place,
            rp.full_name AS handover_name,
            rp.address AS handover_address,
            gp.date,
            gpi.item,
            gpi.item_uuid,
            gpi.qty,
            gpi.return_qty AS returned_qty,
            gpi.pending_qty,
            gpi.is_returnable
        FROM `tabGate Pass Item` gpi
        INNER JOIN `tabGate Pass` gp
            ON gp.name = gpi.parent
        LEFT JOIN `tabReception Person` rp
            ON rp.name = gp.handover_place
        WHERE
            gp.docstatus = 1
            AND gp.direction = %(direction)s
            AND gpi.is_returnable = 1
            AND gpi.pending_qty > 0
            {condition}
        ORDER BY gp.modified DESC
    """, filters, as_dict=True)