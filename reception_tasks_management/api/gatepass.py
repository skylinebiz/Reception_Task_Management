import frappe
from frappe import _
from frappe.utils.pdf import get_pdf
from frappe.utils.jinja import render_template
from werkzeug.wrappers import Response


@frappe.whitelist()
def get_pending_return_items(direction, company=None, search=None):

    direction = "OUT" if direction == "IN" else "IN"

    filters = {
        "direction": direction,
        "company": company

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

    if company:
        condition += """
            AND gp.company = %(company)s
        """

    return frappe.db.sql(f"""
        SELECT
            gp.name AS gate_pass,
            gp.company,
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


@frappe.whitelist()
def download_gate_pass_pdf(name):
    doc = frappe.get_doc("Gate Pass", name)

    base_height = 70
    row_height = 5
    page_height = base_height + len(doc.items) * row_height + 10

    html = render_template(
        "reception_tasks_management/templates/prints/gate_pass_thermal.html",
        {
            "doc": doc,
            "frappe": frappe,
        },
    )

    pdf = get_pdf(
        html,
        options={
            "page-width": "78mm",
            "page-height": f"{page_height}mm",
            "margin-top": "2mm",
            "margin-bottom": "0.5mm",
            "margin-left": "2mm",
            "margin-right": "0.5mm",
        },
    )

    return Response(
        pdf,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{name}.pdf"'
        },
    )