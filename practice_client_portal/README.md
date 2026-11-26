# Practitioner Suite - Client Portal

A health record's patient portal, sized for a practice that treats clients
(massage, herbalism, paramedical tattooing and the like). Built 2026-11-24. OCA has nothing to build on: `OCA/vertical-medical`
has no modules on any branch from 14.0 to 19.0.

## Client notes (`practice.note`)

On the client, optionally linked to a session and treatment plan: title, note,
date, author, and **visibility**:

- **Internal** (the default): staff only.
- **Shared with client**: shown under **My Records** in their portal. They're
  emailed that there's an update, with a link to sign in. The email never
  contains the note, its title or anything client, because email isn't
  private. `shared_on` records when.

Notes are on a session's **Notes** tab, the client's **Notes** button, and
Practitioner Suite › Clinical › Clinical Notes.

## Photos and marketing permission (`practice.photo`)

One record per session before/after photo, kept in step with the session
(added and removed with the photo; existing photos are picked up on install).

- **Shared with Client** (staff tick it, per photo): the photo appears in the
  client's portal, served by `/my/records/photo/<id>` only to that client
  and only while shared (session photos are private attachments).
- **OK for Marketing**: set only by the client in their portal (and withdrawn
  the same way), or by staff attaching a **signed Photo Release** consent to
  the photo. Staff can't tick it directly: the write is refused without the
  context only those two paths set. Each photo shows a badge such as
  "Marketing OK (Client, in their portal, 11/24/2026)"; every grant and
  withdrawal is logged in its chatter. Filter **OK for Marketing** under
  Practitioner Suite › Clinical › Photos to find usable photos.
- **One release, many photos.** Tick **Covers All Photos** on a signed Photo
  Release: every photo of that client gets permission, and each new one does
  as it's added (`practice.photo.create`). Or select photos and use **Actions ›
  Attach Signed Release** (`practice.photo.release.wizard`, one client at a
  time). The release shows a Photos button listing what it covers.
- **Who wins:** a photo the client decided in their portal (allowed or
  withdrew, `withdrawn_by_client`) is left alone by any release; only the
  client can allow a withdrawn photo again. Unsigning or deleting a release
  ends the permission it gave, on every photo it covered. Every change is
  logged on the photo.

The client-level "OK to Use Photos for Marketing/Portfolio" checkbox from
`practice_base` is hidden: permission is per photo now, each with its proof.
Her decisions (2026-11-24): notes internal by default; only shared photos in
the portal; permission from the client or a signed form; notification email
with a link only.

## Portal

`/my/records` (a "My Records" card on the portal home): the client's shared
notes and shared photos, with Allow / Withdraw per photo. Everything is looked
up through the signed-in user's own partner, never by an id alone. A client
needs portal access (contact › gear › Grant portal access).

## Testing

15 tests (HttpCase): internal by default; sharing emails a link and never the
note; a note can't point at another client's session; photo records follow
the session; staff can't set marketing permission by hand; a signed release
grants it and an unsigned one doesn't; the portal shows only shared notes and
photos; photos are served only to their client and only when shared; the
client grants and withdraws (logged); another client can't change it.
