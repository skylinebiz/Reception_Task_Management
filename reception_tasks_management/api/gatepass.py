import frappe
from frappe import _

@frappe.whitelist()
def get_returnable_items(gate_passes):
    if isinstance(gate_passes, str):
        gate_passes = frappe.parse_json(gate_passes)

    items = []

    for gp in gate_passes:
        rows = frappe.get_all(
            "Gate Pass Item",
            filters={
                "parent": gp,
                "is_returnable": 1
            },
            fields=[
                "item",
                "qty",
                "return_qty",
                "item_uuid",
                "is_returnable"
            ]
        )

        for row in rows:
            pending = (row.qty or 0) - (row.return_qty or 0)

            if pending <= 0:
                continue

            items.append({
                "gate_pass": gp,
                "item": row.item,
                "item_uuid": row.item_uuid,
                "pending_qty": pending,
                "is_returnable": row.is_returnable,
            })

    return items


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_gate_passes_for_return(doctype, txt, searchfield, start, page_len, filters):

    return frappe.db.sql("""
        SELECT DISTINCT
            gp.name,
            gp.direction,
            gp.handover_tofrom
        FROM `tabGate Pass` gp
        INNER JOIN `tabGate Pass Item` gpi
            ON gpi.parent = gp.name
        WHERE gp.docstatus = 1
          AND gp.direction = %(direction)s
          AND gpi.is_returnable = 1
          AND COALESCE(gpi.return_qty,0) < gpi.qty
          AND gp.name LIKE %(txt)s
        ORDER BY gp.modified DESC
        LIMIT %(start)s, %(page_len)s
    """, {
        "direction": filters.get("direction"),
        "txt": f"%{txt}%",
        "start": start,
        "page_len": page_len,
    })

@frappe.whitelist()
def get_pending_return_items(direction, search=None):

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
            gpi.item,
            gpi.item_uuid,
            gpi.qty,
            COALESCE(gpi.return_qty,0) AS returned_qty,
            (gpi.qty - COALESCE(gpi.return_qty,0)) AS pending_qty
        FROM `tabGate Pass Item` gpi
        INNER JOIN `tabGate Pass` gp
            ON gp.name = gpi.parent
        WHERE
            gp.docstatus = 1
            AND gp.direction = %(direction)s
            AND gpi.is_returnable = 1
            AND COALESCE(gpi.return_qty,0) < gpi.qty
            {condition}
        ORDER BY gp.modified DESC
    """, filters, as_dict=True)