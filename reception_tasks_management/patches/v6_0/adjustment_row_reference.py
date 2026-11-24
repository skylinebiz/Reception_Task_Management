import frappe


def execute():
	"""Store Gate Pass Adjustment rows the same way as return rows.

	Before: return_reference = Gate Pass name, item_uuid = original row's uuid.
	After:  return_reference = original row's uuid, item_uuid = the row's own
	        uuid (`<adjustment>-NNN`), return_gate_pass = Gate Pass name.

	Only rows still in the old format (return_reference is a Gate Pass name)
	are changed, so the patch is safe to run again.
	"""
	rows = frappe.db.sql(
		"""
		SELECT gpi.name, gpi.parent, gpi.idx, gpi.item_uuid, gpi.return_reference, gpi.return_gate_pass
		FROM `tabGate Pass Item` gpi
		INNER JOIN `tabGate Pass` gp ON gp.name = gpi.return_reference
		WHERE gpi.parenttype = 'Gate Pass Adjustment'
		ORDER BY gpi.parent, gpi.idx
		""",
		as_dict=True,
	)

	for row in rows:
		frappe.db.set_value(
			"Gate Pass Item",
			row.name,
			{
				"return_reference": row.item_uuid,
				"item_uuid": f"{row.parent}-{row.idx:03d}",
				"return_gate_pass": row.return_gate_pass or row.return_reference,
			},
			update_modified=False,
		)
