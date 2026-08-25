---
title: Export WhatsApp Group Contacts to Google Sheets (Without Breaking the Numbers)
description: Getting the contacts into Sheets is the easy part. Stopping Sheets from mangling the phone numbers — dropping the plus, eating leading zeros, converting long numbers to scientific notation — is the part nobody warns you about.
slug: export-whatsapp-group-contacts-to-google-sheets
date: 2026-08-26
template: guide
keywords: export whatsapp group contacts to google sheets, whatsapp contacts google sheets, import whatsapp csv google sheets, whatsapp group contacts spreadsheet, phone numbers google sheets formatting
takeaways:
  - Import as text, not automatically :: The single setting that prevents every phone-number problem is turning off automatic type detection at import.
  - The plus sign is the first casualty :: Sheets reads a leading + as a formula operator and will silently strip or error on it.
  - Leading zeros vanish :: A number stored as a number cannot begin with 0, so UK, Italian and many other formats are quietly corrupted.
  - Long numbers become scientific notation :: A 12-digit number can render as 9.19876E+11, which looks like data loss but is a display type.
  - Fix it at import, not afterwards :: Once a number has been converted to a numeric type, the lost digits are genuinely gone.
faq:
  - How do I import a WhatsApp contacts CSV into Google Sheets? :: File, Import, Upload, then set "Convert text to numbers, dates and formulas" to No. That last setting is what keeps phone numbers intact.
  - Why did Google Sheets remove the plus from my phone numbers? :: Sheets treats a leading + as the start of a formula. Importing the column as text stops it being interpreted.
  - Why do my phone numbers show as 9.19876E+11? :: They were imported as numbers rather than text. Scientific notation is how Sheets displays large numeric values, and re-formatting does not always restore the original digits.
  - Can I open the CSV directly in Google Sheets from Drive? :: Yes, but double-clicking a CSV in Drive uses default conversion settings and will damage phone number columns. Use File then Import instead.
  - Should I use Excel or Google Sheets for this? :: Either works. Both mangle phone numbers by default and both are fixed by importing the column as text.
---

Exporting the contacts is the quick part. The part that quietly wastes an afternoon is opening the file and finding that your phone numbers have been helpfully reformatted into uselessness.

This happens to everyone, it is not specific to WhatsApp exports, and it is entirely preventable with one setting.

## What goes wrong, and why

Google Sheets tries to guess what each column contains. For almost every kind of data that is helpful. For phone numbers it is destructive, because a phone number **looks like** a number and is not one.

Three specific failures, in the order you will hit them:

| Symptom | Cause | Recoverable? |
|---|---|---|
| `+919876543210` becomes `919876543210` | Sheets reads a leading `+` as a formula operator | Yes, if the digits survived |
| `07911123456` becomes `7911123456` | Numeric types cannot have leading zeros | **No** — the zero is gone |
| `919876543210` becomes `9.19876E+11` | Large values render in scientific notation | Sometimes — often already rounded |

The third one is the nastiest. Beyond 15 significant digits, spreadsheets stop storing the exact value, and re-formatting the cell afterwards gives you back a rounded number that looks plausible and is wrong. There is no warning.

> A phone number is a string of digits, not a quantity. Nothing about it is arithmetic — you never add two phone numbers together. Treat the column as text and every one of these problems disappears.

## The correct import, step by step

1. In Google Sheets, go to **File → Import**.
2. Choose **Upload** and select your exported CSV.
3. Import location: **Create new spreadsheet** or **Replace current sheet**.
4. Separator type: **Detect automatically** is fine for a standard CSV.
5. **Set "Convert text to numbers, dates and formulas" to `No`.** This is the whole ballgame. It is the only setting on this screen that matters.
6. Click **Import data**.

Everything arrives as text, exactly as exported, with plus signs and leading zeros intact.

**Do not double-click the CSV in Google Drive.** That path uses default conversion and gives you no opportunity to set step 5. It is the single most common way people damage the file, precisely because it is the most obvious thing to do.

## If you have already imported it badly

Be realistic about what is recoverable.

- **Missing `+` only, digits intact:** fixable. Add it back with a formula such as `="+"&A2`, then copy and paste-special as values.
- **Missing leading zero:** not fixable from the file. The digit was never stored. If you know every number in that column shares a country, you can prefix it — but you are reconstructing, not recovering.
- **Scientific notation:** check before trusting it. Widen the column and compare a few values against the original CSV in a text editor. If the last digits differ, the values were rounded and the column is unusable.

In all three cases the fastest route is to delete the sheet and import again properly. It takes thirty seconds and removes any doubt about which rows were damaged.

## Useful things to do once it is in

With the columns intact, a WhatsApp export becomes genuinely workable:

- **Split the country code.** Our export already provides Country Code as its own column, so a pivot on it gives you an immediate geographic breakdown of any group.
- **Filter on Number Status.** Sorting or filtering on the `Available` / `Not available` column is far more reliable than trying to pattern-match blanks or dots in the phone field.
- **Sort by Role** to separate owners and admins from ordinary members.
- **Count group overlap** if you exported [all groups at once](/blog/export-all-whatsapp-groups-at-once.html) — a pivot on phone number, counting rows, ranks people by how many of your groups they are in.
- **Freeze the header row** (View → Freeze → 1 row) before you do any of it.

## Keeping it live, and why you probably should not

A frequent follow-up: can the sheet update itself as the group changes?

Not from a WhatsApp export, and it is worth understanding why rather than hunting for
a tool that claims otherwise. The export is a snapshot read from your own browser's
local storage at a moment in time. There is no feed, no webhook and no personal API
to subscribe to — a "live" WhatsApp contacts sheet would require something running
against your account continuously, which is both what WhatsApp's terms prohibit and
what gets numbers banned.

The practical pattern instead:

- **Re-export periodically** and import into a new tab, dated. Monthly is plenty for
  most groups.
- **Keep the raw exports.** Comparing this month's file to last month's tells you who
  joined and who left, which nothing in WhatsApp will tell you directly.
- **Use a formula, not manual comparison.** `COUNTIF` on the phone column across two
  tabs identifies additions and departures in one pass.

That gives you the useful part of a live view — change over time — without anything
running against your account.

## Before you share the sheet

A populated contacts sheet in Google Drive is a list of other people's personal data, and Sheets makes sharing it one click.

- Keep it **restricted**, not "anyone with the link". Link-shared sheets get indexed and forwarded.
- Share with named people only, and prefer **Viewer** over **Editor**.
- If you are sending it on, consider whether the recipient needs the phone numbers at all — often names and group membership are enough.
- Delete working copies when you are done. Duplicated intermediate sheets are how these lists leak.

None of this is legal advice, but in the EU, India, Brazil and many other jurisdictions a spreadsheet of phone numbers is regulated personal data regardless of how easy it was to produce.

## Excel behaves the same way

If you use Excel rather than Sheets, the problem and the fix are identical. Use **Data → From Text/CSV**, and in the import preview set the phone number column's type to **Text** before loading. Do not double-click the CSV to open it — same trap, same result.

For the export itself and the other available methods, see [how to export WhatsApp group contacts](/blog/how-to-export-whatsapp-group-contacts.html).
