# Copyright (c) 2026, Harshit and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    filters = frappe._dict(filters or {})

    if not (filters.from_date and filters.to_date):
        frappe.throw(_("From Date and To Date are mandatory."))

    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"label": _("Entry Date"), "fieldname": "date", "fieldtype": "Date", "width": 100},
        {"label": _("Entry Number"), "fieldname": "gate_pass", "fieldtype": "Link", "options": "Gate Pass", "width": 150},
        {"label": _("Person"), "fieldname": "person", "fieldtype": "Data", "width": 170},
        {"label": _("Place"), "fieldname": "place", "fieldtype": "Data", "width": 170},
        {"label": _("Item Name"), "fieldname": "item", "fieldtype": "Data", "width": 200},
        {"label": _("Remarks"), "fieldname": "remarks", "fieldtype": "Data", "width": 160},
        {"label": _("Returnable Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 110},
        {"label": _("Returned Qty"), "fieldname": "return_qty", "fieldtype": "Float", "width": 110},
        {"label": _("Pending Qty"), "fieldname": "pending_qty", "fieldtype": "Float", "width": 110},
        {"label": _("Item UUID"), "fieldname": "item_uuid", "fieldtype": "Data", "hidden": 1},
    ]


def get_data(filters):
    # Every submitted returnable line (returned fully, partly or not at all).
    # Lines that are themselves returns (return_reference set) are excluded.
    return frappe.db.sql(
        """
        SELECT
            gp.date,
            gp.name AS gate_pass,
            rp_from.full_name AS person,
            rp_place.address AS place,
            gpi.item,
            gpi.remarks,
            gpi.qty,
            IFNULL(gpi.return_qty, 0) AS return_qty,
            gpi.qty - IFNULL(gpi.return_qty, 0) - IFNULL(gpi.adjusted_qty, 0) AS pending_qty,
            gpi.item_uuid
        FROM `tabGate Pass Item` gpi
        INNER JOIN `tabGate Pass` gp ON gp.name = gpi.parent
        LEFT JOIN `tabReception Person` rp_from ON rp_from.name = gp.handover_tofrom
        LEFT JOIN `tabReception Person` rp_place ON rp_place.name = gp.handover_place
        WHERE gp.docstatus = 1
            AND gpi.parenttype = 'Gate Pass'
            AND gpi.is_returnable = 1
            AND IFNULL(gpi.return_reference, '') = ''
            AND gp.date BETWEEN %(from_date)s AND %(to_date)s
        ORDER BY gp.date DESC, gp.name DESC, gpi.idx
        """,
        filters,
        as_dict=True,
    )
