# Keeping manual edits through a rescan

A metadata refresh should improve a library without undoing the work someone has put into it. In Viewarr, changing a title or choosing a poster gives that field a lock. Other fields can still receive updates.

For a fictional film called *Northlight*, the rule looks like this:

| Field | Before refresh | Incoming metadata | After refresh |
| --- | --- | --- | --- |
| Title, manually edited | Northlight: Winter Cut | Northlight | Northlight: Winter Cut |
| Overview, untouched | An older description | An updated description | An updated description |
| Poster, manually chosen | Dawn artwork | Default artwork | Dawn artwork |

## Put the rule where writes happen

The editor saves each changed value and its lock in the same database transaction. Provider updates check the lock as part of the write: a locked field keeps its existing value; an unlocked field accepts the incoming value.

That rule lives in the storage layer. A background scan, an explicit refresh and a local NFO import must respect the same decision. Checking only in the editor would leave the background writers free to overwrite it.

The lock is per field, rather than for the whole film. Correcting a title does not stop the overview or other untouched details from improving. Choosing artwork follows the same rule and advances an artwork version so the browser sees the new image.

## Give control back explicitly

The editor marks locked fields and offers **Unlock and restore from provider**. Removing the lock permits future writes; it does not itself erase the existing value. When a provider match is available, the restore action fetches its metadata again. An unmatched item can retain its value until a later match or import supplies a replacement.

This deliberately gives a manual choice priority over fresh provider data. A correction from the provider will not silently replace a locked field: the administrator has to hand it back.

## Check the behaviour, not just the dialog

The interface tour uses fictional data and simulated storage. Separately, five tests against Viewarr's real SQLite storage layer passed on 8 November 2026:

- Provider writes preserve edited fields while updating unlocked ones; unlocking selected fields permits subsequent updates.
- An edited content rating remains effective for viewing restrictions after a provider update.
- Episode edits survive provider updates and filename realignment.
- Chosen artwork survives a provider write and changes its versioned URL.
- Local NFO metadata fills unlocked fields without replacing manual edits.

These are isolated storage tests, not a claim that every scanner or provider failure has been exercised. The examples here are invented; no library records or server configuration are included.

[View the interface tour](README.md) · [Back to profile](../../README.md)
