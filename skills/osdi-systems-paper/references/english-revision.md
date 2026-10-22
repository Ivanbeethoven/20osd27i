# English revision for systems arguments

## Paragraph checks

Read first sentences in sequence: they should expose the argument without a file inventory. Within each paragraph establish context, explain one mechanism or observation, and connect it to a scoped consequence.

Use stable technical terms. Distinguish files, chunks, uploaded objects, coding blocks, and physical read/checksum units. Prefer explicit actors and verbs over noun stacks. Keep subjects and verbs close; place the important consequence near the sentence end.

## Tense and certainty

Use present tense for mechanisms and models, past tense for completed work, and planning/conditional language for unexecuted studies. Preserve uncertainty.

| Overbroad wording | More precise wording |
|---|---|
| “The system eliminates metadata overhead.” | “The lower-snapshot lookup path resolves file attributes without consulting per-file records in the mutable metadata store.” |
| “Three innovations significantly accelerate agents.” | “The evaluation will test workspace provisioning, lower-snapshot access, and object-range I/O separately, then measure their combined effect on agent tasks.” |
| “Delta stores only changed bytes.” | “The private upper records namespace and data-mapping changes; the data representation determines which extents are rewritten.” |
| “The first system to solve this problem.” | “The design combines these mechanisms under the stated sharing and isolation model; its distinction from the closest prior systems requires the following comparisons.” |

## Revision passes

1. Verify scope and truth before style.
2. Connect observations to design choices.
3. Remove repeated framing and vague significance claims.
4. Align title, abstract, design names, and research questions.
5. Reconcile symbols, units, baselines, and counts.
6. Make captions state varied and controlled quantities and the actual evidence.

These examples are original editing illustrations, not measured findings. Check implementation before using them in a manuscript.
