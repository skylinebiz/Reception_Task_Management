# Copyright (c) 2026, Harshit and contributors
# For license information, please see license.txt

from urllib.parse import quote

import frappe
from frappe import _
from frappe.utils import escape_html, flt, formatdate


def execute(filters=None):
    filters = frappe._dict(filters or {})

    if not filters.item_uuid:
        frappe.throw(_("Open this report from an item in the Returnable Items."))

    return get_columns(), get_data(filters), get_main_entry_html(filters)


def get_columns():
    return [
        {"label": _("Return Entry Date"), "fieldname": "date", "fieldtype": "Date", "width": 120},
        {"label": _("Return Entry Number"), "fieldname": "gate_pass", "fieldtype": "Link", "options": "Gate Pass", "width": 160},
        {"label": _("Person"), "fieldname": "person", "fieldtype": "Data", "width": 170},
        {"label": _("Place"), "fieldname": "place", "fieldtype": "Data", "width": 170},
        {"label": _("Item Name"), "fieldname": "item", "fieldtype": "Data", "width": 200},
        {"label": _("Reference / Remarks"), "fieldname": "remarks", "fieldtype": "Data", "width": 200},
        {"label": _("Return Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 100},
    ]


def get_data(filters):
    return frappe.db.sql(
        """
        SELECT
            gp.date,
            gp.name AS gate_pass,
            rp_from.full_name AS person,
            rp_place.address AS place,
            gpi.item,
            CONCAT_WS(' / ', NULLIF(gp.referance, ''), NULLIF(gpi.remarks, '')) AS remarks,
            gpi.qty
        FROM `tabGate Pass Item` gpi
        INNER JOIN `tabGate Pass` gp ON gp.name = gpi.parent
        LEFT JOIN `tabReception Person` rp_from ON rp_from.name = gp.handover_tofrom
        LEFT JOIN `tabReception Person` rp_place ON rp_place.name = gp.handover_place
        WHERE gp.docstatus = 1
            AND gpi.parenttype = 'Gate Pass'
            AND gpi.return_reference = %(item_uuid)s
        ORDER BY gp.date, gp.name, gpi.idx
        """,
        filters,
        as_dict=True,
    )


def get_main_entry_html(filters):
    main = frappe.db.sql(
        """
        SELECT
            gp.name, gp.date, gp.direction, gp.referance,
            rp_from.full_name AS person,
            rp_place.address AS place,
            gpi.item, gpi.remarks, gpi.qty,
            IFNULL(gpi.return_qty, 0) AS return_qty,
            gpi.qty - IFNULL(gpi.return_qty, 0) - IFNULL(gpi.adjusted_qty, 0) AS pending_qty
        FROM `tabGate Pass Item` gpi
        INNER JOIN `tabGate Pass` gp ON gp.name = gpi.parent
        LEFT JOIN `tabReception Person` rp_from ON rp_from.name = gp.handover_tofrom
        LEFT JOIN `tabReception Person` rp_place ON rp_place.name = gp.handover_place
        WHERE gpi.item_uuid = %(item_uuid)s
            AND gpi.parenttype = 'Gate Pass'
            AND gp.docstatus = 1
        LIMIT 1
        """,
        filters,
        as_dict=True,
    )

    if not main:
        return "<p class='text-danger'>{0}</p>".format(
            escape_html(_("Main entry not found for {0}").format(filters.item_uuid))
        )

    m = main[0]

    def cell(label, value):
        return (
            "<div style='min-width:0'>"
            "<div class='text-muted small'>{0}</div>"
            "<div style='min-height:20px;word-break:break-word'><b>{1}</b></div></div>"
        ).format(escape_html(label), value or "&mdash;")

    link = "<a href='/desk/gate-pass/{0}' target='_blank' rel='noopener'>{1}</a>".format(
        quote(m.name), escape_html(m.name)
    )
    remarks = " / ".join(x for x in (m.referance, m.remarks) if x)

    return (
        "<div style='margin-bottom:12px'><h5>{title}</h5>"
        "<div style='display:grid;grid-template-columns:repeat(5,minmax(0,1fr));"
        "gap:12px 24px;max-width:900px'>"
        "{c1}{c2}{c3}{c4}{c5}{c6}{c7}{c8}{c9}{c10}"
        "</div></div>"
    ).format(
        title=escape_html(_("Main Entry Details")),
        c1=cell(_("Entry Number"), link),
        c2=cell(_("Entry Date"), escape_html(formatdate(m.date))),
        c3=cell(_("Direction"), escape_html(m.direction or "")),
        c4=cell(_("Person"), escape_html(m.person or "")),
        c5=cell(_("Place"), escape_html(m.place or "")),
        c6=cell(_("Item Name"), escape_html(m.item or "")),
        c7=cell(_("Reference / Remarks"), escape_html(remarks)),
        c8=cell(_("Returnable Qty"), str(flt(m.qty))),
        c9=cell(_("Returned Qty"), str(flt(m.return_qty))),
        c10=cell(_("Pending Qty"), str(flt(m.pending_qty))),
    )
