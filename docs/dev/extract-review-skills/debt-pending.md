# Debt Pending — extract-review-skills

Buffer for this cycle's tech-debt writes. Flushed by `dev:done` Step 6a.

## To Record

## To Close

- debt-secure-tree-scoping-unsettled — this cycle makes `dev:validate` call `/dev:secure` from a
  cycle worktree, which is exactly the ambiguity the item records: `dev:secure` audits `$PRIMARY`
  while a cycle runs in `.dev-worktrees/<feature>`. The cycle settles the rule by having the
  reviewer skills accept an explicit tree from the caller, so the item is paid rather than deferred.
