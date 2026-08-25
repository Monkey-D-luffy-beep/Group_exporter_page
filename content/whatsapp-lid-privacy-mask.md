---
title: What the +91••••••93 in Your WhatsApp Export Means
description: That masked entry is not a name and not a corrupted number. It is WhatsApp's LID privacy mask, and it tells you exactly two useful things about the member it belongs to.
slug: whatsapp-lid-privacy-mask
date: 2026-08-25
template: guide
keywords: whatsapp privacy mask, whatsapp lid, export whatsapp group contacts, whatsapp export shows dots instead of number, whatsapp hidden phone number
takeaways:
  - It is a mask, not a name :: WhatsApp stores it in a field called displayNameLID. Tools that treat it as a name fill your Name column with dotted numbers.
  - It carries two real facts :: The country code and the last two digits are genuine. Everything between them is redaction, not data.
  - Country code is recoverable :: Reading the mask lifted country-code coverage from 69% of rows to 99.4% on a real 12,635-row export.
  - The full number is not recoverable :: The tables that would translate a LID back to a phone number are empty on disk. Not restricted — empty.
  - Blank beats fake :: A masked name shown as a name made a working export look 48% broken. Leaving it blank is the honest presentation.
faq:
  - What does +91 followed by dots mean in a WhatsApp export? :: It is WhatsApp's LID privacy mask. The country code and last two digits are real, the middle is redacted, and it appears when WhatsApp has not shared that member's full number with your device.
  - Is the masked number a bug in the export tool? :: No. The mask is what WhatsApp stored. A tool can either show it, hide it, or mistake it for a name, but no tool can turn it back into a full number.
  - Can I get the full phone number some other way? :: Not from the browser. The lid-pn-mapping table that would translate it is empty on disk. If the person is in a group where WhatsApp shares numbers, you already have it.
  - Why does my export show Unknown instead of a name? :: Older versions of many tools write a literal "Unknown" when no name field exists. On a real 12,635-row export that was 36.3% of rows. A blank cell is more accurate.
---

Open a WhatsApp group export and you will eventually find a row like this:

`+91••••••••93`

It sits in the Name column, or the Phone column, or both, depending on which tool produced the file. It looks like corruption. It is not. It is a deliberate WhatsApp data structure, and once you know what it is, it tells you two genuinely useful things.

## It is called a LID, and it lives in a name field

WhatsApp stores it in a field named `displayNameLID`. LID stands for linked identity — an identifier WhatsApp uses in place of a phone number when it has not shared that member's real number with your device.

The field name is the trap. It has "displayName" in it, so a tool reading contact records naively will accept the mask as if it were a person's name, and write it straight into your Name column.

That is not a hypothetical. It is the single most common reason a WhatsApp export looks broken when it is working correctly.

> On a real 12,635-row export, 47.6% of rows carried a privacy mask in the name column and 36.3% carried the literal string "Unknown". Only 16.1% carried a real name. The data underneath was fine. The presentation made it look like a 48% failure.

## What the mask actually encodes

The format is fixed: a country code, a run of redaction characters, then the last two digits.

| Part | Example | Real? |
|---|---|---|
| Country code | `+91` | **Yes** |
| Middle digits | `••••••••` | No — redaction, not data |
| Last two digits | `93` | **Yes** |

So a masked row is not empty. You know the member's country, and you have two digits of verification if you are matching against a list you already hold.

That is worth more than it sounds. Reading the country code out of the mask rather than discarding the row lifted country-code coverage from roughly 69% of rows to **99.4%** on a real export. Three thousand eight hundred and seventy-three rows that previously had nothing in that column now carry a valid dialling code.

## What it does not encode, and why no tool can recover it

The obvious question: if WhatsApp knows the LID maps to a real number, is the mapping stored somewhere on my machine?

There are two tables that would hold exactly that, `lid-pn-mapping` and `lid-display-name-mapping`. Both are **empty**. Not access-restricted, not encrypted — zero records.

We checked this the direct way. In a 1,907-member group where every participant used a LID, we examined 200 of them individually:

| | Count |
|---|---|
| Participants sampled | 200 |
| Had a contact record at all | 200 |
| Carried a real `phoneNumber` | 17 |
| Carried only the mask, nothing else | 183 |
| Had a `pushname` we were failing to read | 0 |
| Had an address-book `name` we were failing to read | 0 |

There is no hidden field. The number was never sent to your browser, so nothing running in your browser can retrieve it. Any tool advertising that it can unmask these is either mistaken or selling you something that does not work.

## Where masks come from

Masks are not randomly distributed. They cluster almost entirely in **WhatsApp Community sub-groups**, particularly announcement-only ones, where WhatsApp withholds member numbers by design — the "only community admins can see all members" rule.

Ordinary groups behave completely differently. Every plain group we measured returned a real phone number for every member, at sizes of 883, 740, 675, 500, 496, 453, 146 and 130. If your export is full of masks, look at what kind of group it came from before you blame the tool. The full breakdown is in [our research on blank phone numbers](/whatsapp-group-export-blank-numbers.html).

## Why WhatsApp introduced this at all

The mask is not an accident of an old system. It is the visible edge of a
deliberate shift in how WhatsApp identifies people.

Historically a WhatsApp account *was* its phone number — the number was the
identifier, and anyone who could see you in a group could see it. That is
convenient and it is also the reason group harvesting became an industry.

The linked identity is the replacement: a stable handle that lets WhatsApp route
messages and render a chat without handing your number to everyone in the room.
Your number still exists, and people you have actually exchanged contact details
with still see it. What changes is the default for strangers who happen to share a
large group with you.

For anyone exporting group contacts, the practical reading is that the share of
masked entries goes **up** over time, not down. A tool built on the assumption that
every member has a readable number was built against a WhatsApp that is going away.

## Working with masked rows in a spreadsheet

A masked row is partial data, not useless data. Three things it supports:

- **Segment by country.** The dialling code is real, so a pivot on the Country Code
  column gives you an accurate geographic breakdown of a group even when most
  numbers are hidden. On a 12,635-row export that column was populated for 99.4% of
  rows.
- **Match against a list you already hold.** If you have a customer or member list
  with phone numbers, the country code plus the last two digits is enough to narrow
  a candidate set hard. It is not a unique key, but combined with a name it usually
  resolves.
- **Filter cleanly.** Sort or filter on the `Number Status` column — `Available` or
  `Not available` — rather than trying to pattern-match dots in a text field.

What it does not support is dialling, messaging, or import into a CRM as a contact
record. A masked row is a person you know is there, not a person you can reach.

## The right way to present it

Once you know the mask is not a name, the handling follows:

- **Never write it into the Name column.** A dotted number is not a name, and putting it there converts a working export into one that looks half-broken.
- **Never substitute a placeholder.** "Unknown" in 36% of rows is noise you then have to filter out.
- **Leave the name blank.** A blank cell is accurate and sorts, filters and de-duplicates cleanly.
- **Mine the mask for the country code**, because that part is real.
- **Say how many rows are affected**, right after the export, so a correct file is never mistaken for a failed one.

That is what Group Contacts Exporter does: real name or blank, country code recovered from the mask, and a `Number Status` column that says `Available` or `Not available` for every row.
