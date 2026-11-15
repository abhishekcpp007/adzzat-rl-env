# Scope note

**What the agent does.** It gets a copy of the `inflection` library (MIT, a
Python port of the Rails inflector, about 430 lines) in `/app` and an issue
written the way a user would write it. It reads code and runs commands as an
unprivileged user with no network. When it's done it submits, and the only
thing that leaves its container is `/app/inflection.py`.

**The tasks.**

| Task | Difficulty | What it takes |
|---|---|---|
| `ordinal-teens` | easy | One wrong condition makes `ordinalize(11)` return `11st`. |
| `parameterize-unicode` | medium | Two bugs in two functions that call each other: accents get dropped, and custom separators double up. One issue describes only the symptoms. |
| `acronym-support` | hard | A new feature across four functions plus a registry. `underscore(camelize(s)) == s` has to hold, so the CamelCase tokenizer needs real design. |
| `plural-rules` | medium, partial credit | Four broken rule-table entries. Each fixed rule earns 0.25, and breaking anything else scores 0. |
| `plural-counterfactual` | probe | Same as `plural-rules`, but one rule differs from upstream on purpose, so recalling the original library loses credit. |

**What success means.** The grader runs the submitted module on a fixed set of
cases plus a few hundred random ones drawn from a fresh seed, and compares each
result to a reference module. Tasks 1 to 3 pay 1.0 only if every group of
cases matches. Nothing the agent can see decides the reward: the visible tests
are a starting point, and editing them changes nothing.

**Why a lab would want this data.** Small as it is, the environment covers the
skill that matters most in coding agents: reading unfamiliar code, finding
where a symptom comes from, and fixing it without breaking the rest. The
random differential cases make the reward hard to fake, so a policy trained on
it can't climb by memorizing examples or editing tests. The task builder makes
variants cheap too. A new bug is one `(old, new)` pair in `src/tasks/bugs.py`,
and the reference comes for free. That's how you'd get hundreds of graded
tasks from one small library. The honest limit is difficulty: see
[RESULTS.md](RESULTS.md).
