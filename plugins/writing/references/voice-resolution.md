# Voice Resolution

The single procedure the platform skills (`email`, `linkedin`) use to decide which personal
voice to write in. It is location- and layout-independent: it never reads a hardcoded
reference-file path inside a specific voice skill. A voice is always loaded **at the skill
level** — the resolved voice skill is self-contained, whether it's a single `SKILL.md` or one
that carries its own `references/`.

Follow this order every time.

## Resolution order

1. **Registered pointer.** If `~/.claude/CLAUDE.md` contains a line of the form
   `Writing voice: <skill-name-or-path>`, use it. The value may name an installed skill
   (e.g. `voice-jordan`) or point to a voice located anywhere. Load that voice at the skill
   level and stop here.

2. **Convention.** If there is no pointer, discover installed `voice-*` skills using Claude's
   own skill discovery — the roster of available skills, **not** a filesystem glob.
   - **0 voices found** → no personal voice. Fall through to the default (below).
   - **1 voice found** → use it.
   - **2 or more found** → enumerate them and ask the user which to write in. Never silently
     pick one.

3. **Default.** When resolution yields no voice, write in a natural, varied, human default
   voice — clean and direct. Still apply the channel best-practices in full. Never error out
   over a missing voice, and never assume a specific named person's voice.

## Edge cases (inherited by every skill that follows this procedure)

- **Pointer references a missing or renamed skill.** Do not hard-fail. Note that the pointer
  didn't resolve, then fall back to the convention (step 2), and then the default (step 3).
- **Voice installed outside the `voice-*` convention** (a different name or a location the
  roster doesn't surface as `voice-*`). It is resolvable only via the `Writing voice:` pointer.
  If there's no pointer, the convention won't find it — fall through to asking the user to name
  or describe their voice, and otherwise the default.
- **Zero voices and no pointer.** Use the clean best-practice default. This is a fully
  supported path, not a failure: a fresh installer with nothing set up still gets good output
  (current channel best-practices + a de-AI pass + a natural default voice).

## The default, stated plainly

If nothing resolves, the correct behavior is a natural, varied human default voice — not an
error and not any particular person's voice. The channel best-practices always apply on top,
so the output is still current and well-structured; it simply isn't personalized.

## Registering a voice

To make a voice resolve first, add a single line to `~/.claude/CLAUDE.md`:

```
Writing voice: <skill-name-or-path>
```

`voice-extractor` offers to write or refresh this line when it creates a voice skill. It can
also be added by hand. It may name an installed `voice-*` skill or point to a voice anywhere.
