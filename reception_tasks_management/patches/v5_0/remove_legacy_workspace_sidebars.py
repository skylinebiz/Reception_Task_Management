import frappe

# Old v16-style sidebar this app used to ship from `reception_tasks_management/workspace_sidebar/`.
# The app now ships its sidebar as a module `Sidebar`
# (reception_tasks_management/reception_tasks_management/sidebar/), so this row is dead weight.
# Left in the database, Frappe's `convert_sidebars` upgrade patch would turn it back into a sidebar.
LEGACY_SIDEBARS = ("Reception Tasks",)


def execute():
	if not frappe.db.exists("DocType", "Workspace Sidebar"):
		return

	for name in LEGACY_SIDEBARS:
		frappe.delete_doc(
			"Workspace Sidebar",
			name,
			ignore_permissions=True,
			ignore_missing=True,
			force=True,
		)

	frappe.clear_cache()
