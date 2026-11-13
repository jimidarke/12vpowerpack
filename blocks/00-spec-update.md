# Block 0 — replace the specification (no capture)

**Send on:** root thread "4x18650 Battery Pack". **Attachment:** `requirements.md` + `architecture.md`.

## Message
The scope of this project has changed. Do not place or wire anything in this run.

1. Replace the `project-specification` document with the attached requirements (v2).
2. Save the attached architecture as a new document `architecture`.
3. Mark `bms-capture-handoff` as superseded where it conflicts: the BQ77915 shunt is now 7–8 mΩ, and its listed blocking questions are answered in the architecture document and the block-1 brief that follows.
4. Rename the project "12V Power Manager" and update the description to match.

Reply with only a confirmation and any conflict you see between the two attached documents. Do no datasheet research in this run.

## Done when
`get_files` lists the updated `project-specification` and new `architecture`; `get_components` still shows no components.
