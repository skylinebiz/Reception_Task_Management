import frappe


def execute():
	"""Fill Gate Pass Item.return_gate_pass (Link -> Gate Pass) for existing rows.

	Return rows store the original row's item_uuid in `return_reference`.
	The uuid is shared across amendments, so prefer the submitted Gate Pass
	that holds it now; fall back to the latest Gate Pass that ever held it.
	Adjustment rows already store the Gate Pass name in `return_reference`.
	"""
	rows = frappe.db.sql(
		"""
		SELECT name, return_reference
		FROM `tabGate Pass Item`
		WHERE parenttype = 'Gate Pass'
			AND IFNULL(return_reference, '') != ''
			AND IFNULL(return_gate_pass, '') = ''
		""",
		as_dict=True,
	)

	for row in rows:
		original = frappe.db.sql(
			"""
			SELECT gp.name
			FROM `tabGate Pass Item` gpi
			INNER JOIN `tabGate Pass` gp
				ON gp.name = gpi.parent
				AND gpi.parenttype = 'Gate Pass'
			WHERE gpi.item_uuid = %s
			ORDER BY (gp.docstatus = 1) DESC, gp.creation DESC
			LIMIT 1
			""",
			row.return_reference,
		)
		if original:
			frappe.db.set_value(
				"Gate Pass Item", row.name, "return_gate_pass", original[0][0], update_modified=False
			)

	frappe.db.sql(
		"""
		UPDATE `tabGate Pass Item` gpi
		INNER JOIN `tabGate Pass` gp ON gp.name = gpi.return_reference
		SET gpi.return_gate_pass = gpi.return_reference
		WHERE gpi.parenttype = 'Gate Pass Adjustment'
			AND IFNULL(gpi.return_gate_pass, '') = ''
		"""
	)
