# Changelog

All notable changes to Reception Tasks Management are documented here.

## [6.0.0] - 2026-11-23

This release was first pushed as 5.3.0 (commit `f8663f1`) and is renumbered 6.0.0 with no code
changes, because it adds a Gate Pass Item field and rejects documents that 5.x accepted: cancelling
a referenced Gate Pass, invalid return references, zero or negative return qty, and adjustments
above pending qty. There is no separate 5.3.0 release. A site that already ran `migrate` on 5.3.0
needs nothing more; the `set_return_gate_pass` patch keeps its name and does not run again.

### Added
- **Return Gate Pass** (`return_gate_pass`, read-only Link → Gate Pass) on Gate Pass Item. It is set
  on save from the row-level `return_reference` (return rows) or the adjusted Gate Pass (adjustment
  rows). `return_reference` still holds the original row's `item_uuid` and is unchanged. Because the
  new field is a Link, Frappe's **Cancel All Documents** dialog now lists the return Gate Passes
  that reference a Gate Pass, as well as its adjustments, and cancels them first.
- New patch `set_return_gate_pass` (post model sync) fills the field on existing rows. A return
  row resolves to the submitted Gate Pass that holds its uuid now (the amended one, after an
  amendment), falling back to the latest Gate Pass that held it.

### Fixed
- **A referenced Gate Pass could be cancelled.** Cancelling is now blocked while a draft or
  submitted return Gate Pass or Gate Pass Adjustment references it (by Gate Pass name or by row
  uuid, so references made before an amendment count too). The message lists each document with a
  link and marks it Draft or Submitted.
- **Duplicating a Gate Pass copied its row uuids**, so two submitted passes could share one and a
  return could be booked against the wrong one. A duplicate now gets fresh uuids; amendments still
  keep theirs.
- **Two rows in one Gate Pass could get the same uuid** after deleting and re-adding rows. New rows
  are now numbered after the highest number already used in the document.
- **Gate Pass Adjustment updated the cancelled row after an amendment.** It now finds the original
  row by `item_uuid` on the submitted Gate Pass, like returns do.
- Cancelling a return or an adjustment whose original Gate Pass was already cancelled failed with
  "Original item not found". That row is now skipped, so these documents can be cancelled.

### Changed
- **Return rows are checked on save as well as submit:** the referenced row must be on a submitted
  Gate Pass, be returnable, be in the opposite direction and be in the same company, and a Gate
  Pass cannot return its own items. A return row cannot itself be marked returnable.
- **Qty:** negative qty is rejected on every row; returnable and return rows need qty greater
  than 0.
- **Gate Pass Adjustment:** only returnable rows of a submitted Gate Pass can be adjusted, and every
  row must belong to the adjustment's Gate Pass. Adjusted qty cannot be negative or more than the
  pending qty (qty − returned − already adjusted). Pending qty is now calculated after the adjusted
  qty is clamped at 0.
- **Amending a Gate Pass** cannot reduce a row's qty below its returned + adjusted qty.
- `get_gate_pass_items` (adjustment item fetch) returns nothing for a draft or cancelled Gate Pass,
  and only Gate Pass rows.
- `get_pending_return_items` ("Get Returnable Items") leaves out return rows and adjustment rows,
  matching the Returnable Items report.

### Upgrade notes
- Run `bench --site <site> migrate` (new field and patch), then restart the bench so the server
  loads the new code.
- No role has Cancel or Amend permission on Gate Pass Adjustment, so the Cancel All Documents dialog
  will not offer "Cancel All" when an adjustment is listed. Grant those permissions to the roles that
  need them.

## [5.2.0] - 2026-11-19

### Changed
- **App icon** — replaced the grey "R" text tile with a drawn icon: a gate pass ticket with a check
  mark on a green rounded square (`reception-tasks-logo.svg`). It has no text, so it stays readable
  at sidebar size.
- **Returnable Items** and **Returnable Item Details** reports no longer carry a default
  System Manager role. Anyone with Report permission on Gate Pass (the reports' reference doctype)
  can now open them.

### Removed
- The old `workspace_sidebar/` sidebar **Reception Tasks**. This Frappe version no longer imports
  that folder; the app's sidebar is the module `Sidebar` under
  `reception_tasks_management/reception_tasks_management/sidebar/`.
- New patch `remove_legacy_workspace_sidebars` (pre model sync) deletes the old `Workspace Sidebar`
  record from the database, so Frappe's sidebar upgrade does not rebuild it.

### Upgrade notes
- Run `bench --site <site> migrate` (report roles, old sidebar cleanup), then hard-refresh browsers to see the new icon.

## [5.1.0] - 2026-11-03

### Added
- **App icon** — the app now has its own icon (an "R" tile, `reception-tasks-logo.svg`) on the Apps screen, set through `app_logo_url` / `add_to_apps_screen` in `hooks.py`.

### Changed
- **Sidebar** — Gate Pass, Reception Person, Supplier, Gate Pass Adjustment and
  Transporter Entry are now grouped under a new **Masters** section, the
  **Reports** section is no longer indented, and Returnable Items has a table icon.

## [5.0.0] - 2026-10-25

### Added
- **Returnable Items report** (Script Report on Gate Pass). Takes a From/To Date
  range on the entry date and lists every submitted returnable item, whether
  fully returned, partly returned or still pending.
  - Columns: Entry Date, Entry Number, Person, Place, Item Name, Remarks,
    Returnable Qty, Returned Qty and Pending Qty.
  - Place shows the Reception Person's address.
  - Entry Number is a Link column and opens Frappe's side-panel preview of the
    Gate Pass.
  - Item Name opens **Returnable Item Details** in a new tab, filtered to that
    item.
- **Returnable Item Details report**, the connected report. Shows the main entry
  details (entry number, date, direction, person, place, item, remarks,
  returnable / returned / pending qty) above a table of the return entries made
  against the item: Return Entry Date, Return Entry Number, Person, Place, Item
  Name, Reference / Remarks and Return Qty. Return entry numbers are Link columns.
- Both reports are available from the Reception Tasks sidebar (Returnable Items).

### Changed
- **Item Name is editable on every Gate Pass Item row**, including rows populated
  via Get Returnable Items. This supersedes the 4.2.0 read-only rule.
- **Return Reference column in the items grid is dynamic:** shown only while at
  least one row carries a return reference, hidden otherwise.
- **Return Qty check on Submit** now counts adjusted qty (original qty minus
  adjusted qty is the limit) and reports the row, the item (with its reference
  without the row suffix), the original qty and the returnable qty:
  `Row No | Item Name | Original Qty | Returnable`. Cancel still takes the qty
  back off the original row.
- Several Gate Passes can return the same original row, each with its own item
  name; only the combined returned qty is limited, and it is checked on Submit
  only (not on Save).
- Rows with a return reference no longer require Same Item Name.

### Removed
- The server-side guard for linked item names (`validate_linked_item_names`):
  linked rows no longer take the original item name and renames are no longer
  rejected.

### Upgrade notes
- Run `bench --site <site> migrate` (new reports, Gate Pass Item field setting),
  then `bench build --app reception_tasks_management` and hard-refresh browsers.
- The old report names from development ("Returnable Items Register",
  "Returnable Item Returns") can be deleted from the Report list if they exist.

## [4.2.0] - 2026-10-14

### Added
- **Get Returnable Items on draft Gate Passes.** The button was previously
  available only on a new Gate Pass; it now shows on any draft (`docstatus = 0`).
  - On an existing draft, *Populate* appends the selected items to the open
    document instead of creating a new Gate Pass.
  - Items already linked on the draft (same `return_reference`) are skipped, and
    a blank placeholder row is removed first.
  - The button asks for **Direction** first, since the search direction depends
    on it.
- **Server-side guard for linked item names** (`Gate Pass.validate`). A row
  linked to an original item takes its item name from that original on first
  save, and a later rename is rejected with
  *"Row N: Item Name cannot be changed for an item linked to <reference>."*

### Changed
- **Item Name is read-only for rows populated via Get Returnable Items** (rows
  with a `return_reference`). The rule is applied while each row renders, so
  linked rows are locked from the first paint; manually added rows stay editable.
- **Gate Pass Item fields made read-only:** `return_qty`, `pending_qty`,
  `return_reference`, `item_uuid` and `adjusted_qty`.

### Fixed
- Returns could be submitted with a renamed, still-linked row, which failed at
  Submit with *"Returned Qty cannot exceed Original Qty for <original item>"*,
  naming an item no longer on screen. The link can no longer drift from the item.

### Upgrade notes
- Run `bench --site <site> migrate` (Gate Pass Item field properties changed),
  then `bench build --app reception_tasks_management` and hard-refresh browsers.

## [4.1.0] - 2026-08-25
- Fixed Handover Place name and the Remarks field type.

## [4.0.0] - 2026-07-31
- Added Gate Pass Adjustment, the adjustment button in the Return Status report,
  and updated naming series.
