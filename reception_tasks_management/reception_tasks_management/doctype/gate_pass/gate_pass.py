# Copyright (c) 2026, Harshit and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class GatePass(Document):
	def before_save(self):
		for row in self.items:
			if not row.item_uuid:
				row.item_uuid = f"{self.name}-{row.idx:03d}"
