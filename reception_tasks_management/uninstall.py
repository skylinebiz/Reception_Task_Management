import frappe

ROLES = [
    "Reception User",
    "Reception Manager",
]

DOCTYPES = [
    "Gate Pass",
    "Transporter Entry",
    "Reception Person",
    "Supplier",
]


def after_uninstall():
    """Cleanup after uninstall. Never fail the uninstall."""
    for fn in (
        delete_custom_permissions,
        remove_roles_from_users,
        delete_roles,
    ):
        try:
            fn()
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"Reception Tasks Management uninstall: {fn.__name__}",
            )

    frappe.clear_cache()
    frappe.db.commit()


def delete_custom_permissions():
    """Delete Custom DocPerm records created by this app."""

    try:
        frappe.db.delete(
            "Custom DocPerm",
            {
                "parent": ["in", DOCTYPES],
                "role": ["in", ROLES],
            },
        )
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Failed deleting Custom DocPerm records",
        )


def remove_roles_from_users():
    """Remove app roles from all users."""

    try:
        frappe.db.delete(
            "Has Role",
            {
                "role": ["in", ROLES],
            },
        )
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Failed deleting Has Role records",
        )


def delete_roles():
    """Delete custom roles."""

    for role in ROLES:
        try:
            if frappe.db.exists("Role", role):
                frappe.delete_doc(
                    "Role",
                    role,
                    ignore_permissions=True,
                    force=True,
                )
        except Exception:
            # Fallback: delete directly if delete_doc fails
            try:
                frappe.db.delete("Role", {"name": role})
            except Exception:
                frappe.log_error(
                    frappe.get_traceback(),
                    f"Failed deleting Role: {role}",
                )