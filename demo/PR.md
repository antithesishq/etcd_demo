# Don't reuse same ReadIndex in retries

Ref #<ISSUE#>

Should fix the stale read found by Antithesis. The linearizable read loop reused a single ReadIndex `requestID` across retries, so under a process pause a late response to a superseded request could be accepted and confirm a stale index. This tracks every in-flight `requestID` and resends with a fresh one, ignoring out-of-date responses (mirrors upstream etcd-io/etcd#21399, backported to `release-3.6` as #21417, released in v3.6.9).

Comment `/run-antithesis-test` on this PR to reproduce the green run.



Verified with Antithesis — the finding is resolved:

| | `Linearization validation passes` |
|---|---|
| **Before** | ❌ Failing — 108 counterexamples (run `517ea7809cf80d9abbbe69c10638bd78-55-12`) |
| **After**  | ✅ Passing — assertion evaluated, 0 counterexamples (run `<AFTER-RUN>`) |

> "After" must show the assertion **present and Passing** (`example_count > 0`), not merely absent.
