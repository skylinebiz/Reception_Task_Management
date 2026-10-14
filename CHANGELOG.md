# Changelog

All notable changes to Reception Tasks Management are documented here.

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
