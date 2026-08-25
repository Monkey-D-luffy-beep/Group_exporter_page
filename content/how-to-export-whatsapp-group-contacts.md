---
title: How to Export WhatsApp Group Contacts to Excel (4 Methods, 2026)
description: Every working way to export contacts from a WhatsApp group to Excel or CSV — by hand, with the browser console, with WhatsApp's own chat export, and with an extension. What each one costs you, and which to pick.
slug: how-to-export-whatsapp-group-contacts
date: 2026-08-25
template: guide
keywords: how to export whatsapp group contacts, export whatsapp group contacts to excel, export contacts from whatsapp group, download whatsapp group contacts, export whatsapp group contacts to csv, export contact list from whatsapp group
takeaways:
  - WhatsApp has no export button :: There is no native way to export a group member list. Every method below is a workaround.
  - You do not need to be an admin :: Ordinary membership is enough to see and export the participant list in a normal group.
  - You do need WhatsApp Web :: Every method that produces a spreadsheet runs through web.whatsapp.com on a computer. The phone apps cannot do it.
  - Chat export is the wrong tool :: WhatsApp's built-in Export Chat gives you messages, not a member list. It is the most common wasted hour.
  - Pick by group size :: Under 30 members, copy by hand. Above that, the manual methods stop being worth the time.
faq:
  - Can I export WhatsApp group contacts without being an admin? :: Yes. In an ordinary group, any member can see the participant list, and anything you can see you can export. Admin rights change nothing here.
  - How do I export WhatsApp group contacts to Excel? :: Export to CSV, then open the CSV in Excel. Every method below produces either CSV or something you paste into a spreadsheet. There is no direct .xlsx route.
  - Does WhatsApp have a built-in contact export? :: No. Export Chat exports messages, not members. There is no native member-list export on any platform.
  - Can I export WhatsApp group contacts on my phone? :: Not into a usable spreadsheet. Every method that produces a contact list needs WhatsApp Web on a computer.
  - Is it legal to export WhatsApp group contacts? :: Exporting a list you already have access to is generally fine. What you then do with it is the part that carries obligations — unsolicited bulk messaging breaches WhatsApp's terms and, in many countries, data protection law.
---

WhatsApp does not have an export button for group members. There is no menu item, no hidden setting, and no official API for it on a personal account. Anyone telling you otherwise is describing a workaround.

There are four workarounds that actually work. Here is each one, honestly, including the two we do not sell.

## Before you start: three things that trip people up

**You do not need to be an admin.** This is the single most common misconception. In an ordinary WhatsApp group, every member can see the full participant list — and anything you can see, you can export. Admin rights change what you can *do* to the group, not what you can read from it.

**You do need a computer.** Every method that produces a spreadsheet runs through WhatsApp Web at `web.whatsapp.com`. The iPhone and Android apps have no route to a CSV. If you only have a phone, none of the four methods below will work for you.

**"Export Chat" is not what you want.** WhatsApp's built-in Export Chat feature produces a `.txt` file of *messages*. It contains a member's number only if that member happened to post. On a 500-member group where 40 people talk, you get 40 numbers. This is the most common wasted hour in this whole exercise, so rule it out first.

## Method 1: Copy the list by hand

The one everybody tries first, and for small groups it is genuinely the right answer.

1. Open WhatsApp Web and open the group.
2. Click the group name to open Group Info.
3. Scroll the participant list to load every member.
4. Select the list, copy, and paste into Excel or Google Sheets.
5. Clean up the result — names and numbers usually land in one column, and you will need Text to Columns to split them.

**When to use it:** groups under about 30 members, or a one-off you will never repeat.

**What it costs:** roughly a minute per 15–20 members once you include cleanup, and it scales linearly. A 500-member group is most of an afternoon and you will make mistakes near the end.

## Method 2: A browser console script

Free, no installation, and genuinely effective if you are comfortable with it. You open Chrome DevTools, paste a JavaScript snippet, and it walks the participant list and dumps a file.

**When to use it:** you are technical, you need this once, and you do not want to install anything.

**What it costs, and be honest with yourself about this one:**

- **You are pasting code you did not write into a live, logged-in session of your own WhatsApp account.** A malicious snippet in that context can read your messages and act as you. Only ever run one you have read and understood line by line.
- Most published scripts break. WhatsApp Web's internals change, and gists written a year ago frequently return nothing or half a list with no error.
- Most of them scroll the rendered participant list, which means they inherit its limits — see the section on incomplete lists below.

If you search for this, you will find several GitHub gists ranking on page one. They are real, some of them work, and the security caveat above is the entire reason we do not recommend them to non-technical users.

## Method 3: WhatsApp's Export Chat (and why it is not the answer)

Covered above, but for completeness, because so many guides list it as a contact export method:

1. Open the group on your phone.
2. Tap the group name, scroll down, tap **Export Chat**.
3. Choose **Without Media**.
4. Send the `.txt` file to yourself.

What you get is a message transcript. Numbers appear beside messages from people not in your address book. Silent members — usually the large majority — do not appear at all.

**When to use it:** when you want a record of the conversation. Never for a member list.

## Method 4: A Chrome extension

Install once, then export in about three clicks. This is what most people end up doing for anything above a small group.

The general shape:

1. Install the extension from the Chrome Web Store.
2. Open WhatsApp Web and sign in as usual.
3. Click the extension icon.
4. Choose the group and export to CSV.
5. Open the CSV in Excel or Google Sheets.

**When to use it:** any group above ~30 members, or any time you will do this more than once.

**What to check before installing one**, because this category attracts junk:

- **Does it cap the free tier?** Several show you the first 10 contacts and hide the rest behind payment. Check before you spend time on an export.
- **Does anything leave your machine?** Extraction can be entirely local. Some tools upload your contact list to a server. Read the privacy disclosure on the store listing, not the marketing page.
- **Can it send messages?** A read-only exporter cannot. Anything that also offers bulk messaging is asking for far more access to your account, and bulk messaging is what gets WhatsApp numbers banned.
- **Does it need you to open and scroll the group?** This one predicts whether your export will be complete.

## Why your export might come back incomplete

Worth knowing regardless of which method you choose, because it affects three of the four.

Methods 1, 2 and most extensions read the participant list **that WhatsApp Web has drawn on screen**. WhatsApp virtualises long lists — it keeps only a window of rows in the page and discards what you have scrolled past. So the collection is bounded by how far the list was scrolled, and it fails silently. Nothing warns you that rows are missing.

On a real 679-member group, scroll-based collection returned 500 rows. The file looked fine. It was missing a quarter of the group. We wrote that up in detail in [why exports miss members](/blog/whatsapp-group-export-missing-members.html).

Two related things that look like failures but are not:

- **Rows with a name but no phone number.** In ordinary groups this is rare. In WhatsApp **Community sub-groups** it is normal and unavoidable — WhatsApp withholds those numbers by design. See [exporting community members](/blog/export-whatsapp-community-members.html).
- **A count that is one or two short of what the group header says.** That header is a cached number and it drifts. [Details here](/blog/whatsapp-group-member-count-wrong.html).

## Which method to pick

| Your situation | Use |
|---|---|
| Under 30 members, one time | Method 1, by hand |
| Technical, one time, install nothing | Method 2, console script — read it first |
| You want the conversation, not the members | Method 3, Export Chat |
| Above 30 members, or you will repeat it | Method 4, an extension |
| You need every group in one file | Method 4, and only some extensions can |
| You are on a phone with no computer | None of these work |

For anything routine, the extension route wins on time alone. The question is which one, and the checklist above matters more than the feature list on any given landing page.
