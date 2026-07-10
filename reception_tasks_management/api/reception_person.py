import frappe
from frappe import _

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def reception_person_query(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql(
        """
        SELECT
            name,
            full_name,
            address,
            phone
        FROM `tabReception Person`
        WHERE
            name LIKE %(txt)s
            OR full_name LIKE %(txt)s
            OR address LIKE %(txt)s
            OR phone LIKE %(txt)s
        ORDER BY
            CASE
                WHEN name = %(exact)s THEN 0
                WHEN address = %(exact)s THEN 1
                WHEN phone = %(exact)s THEN 2
                ELSE 3
            END,
            name
        LIMIT %(start)s, %(page_len)s
        """,
        {
            "txt": f"%{txt}%",
            "exact": txt,
            "start": start,
            "page_len": page_len,
        },
    )