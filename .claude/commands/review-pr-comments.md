---
description: Review and respond to code review comments from automated reviewers (AI bots, linters, etc.)
---

## User Input

```text
$ARGUMENTS
```

**Required**: PR number (e.g., `45`)

## Goal

Evaluate code review comments from automated reviewers, decide which to accept or reject, implement fixes, and respond appropriately.

## Execution Steps

### Step 1: Fetch Review Comments

Use `gh` CLI to get review threads and comments. **Important**: Two different ID formats are needed:

1. **Thread ID** (GraphQL node_id like `PRRT_xxx`): Used for resolving threads
2. **Comment ID** (REST API numeric like `2604837472`): Used for replying to comments

```bash
# Step 1a: Get thread IDs (for resolving) via GraphQL
gh api graphql -f query='
query {
  repository(owner: "drillan", name: "e-stat-mcp") {
    pullRequest(number: $ARGUMENTS) {
      reviewThreads(first: 50) {
        nodes {
          id
          isResolved
          path
          line
          comments(first: 10) {
            nodes {
              body
              author { login }
            }
          }
        }
      }
    }
  }
}'

# Step 1b: Get numeric comment IDs (for replying) via REST API
gh api repos/drillan/e-stat-mcp/pulls/$ARGUMENTS/comments --jq '.[] | "\(.id) \(.path):\(.line) \(.user.login)"'
```

Filter for unresolved threads from automated reviewers (bots, AI assistants, linters).

**ID Mapping Example**:
| Thread ID (GraphQL) | Comment ID (REST) | File |
|---------------------|-------------------|------|
| PRRT_kwDOQZ9YJM5lbGiX | 2604837472 | src/e_stat_mcp/client.py:45 |

### Step 2: Evaluate Each Comment

For each comment, evaluate using these criteria:

| Criterion | Accept if... | Reject if... |
|-----------|-------------|--------------|
| **Type Safety** | Improves type annotations, fixes mypy errors | Over-specified types that reduce readability |
| **Code Quality** | Fixes ruff warnings, improves maintainability | Stylistic preferences without clear benefit |
| **Testing** | Adds missing test coverage, fixes flaky tests | Over-testing trivial code |
| **Security** | Addresses real vulnerabilities | Security theater without practical benefit |
| **Performance** | Fixes proven bottlenecks | Premature optimization |

### Step 3: Create Response Plan

Output a table summarizing decisions:

| Thread ID | File | Issue | Decision | Action |
|-----------|------|-------|----------|--------|
| PRRT_xxx | path/file.py | Description | Accept / Reject | Fix / Reply+Resolve |

### Step 4: For REJECTED Comments - Reply and Resolve

**Important**: Use the correct ID format for each operation:
- **Reply**: Use **numeric comment ID** from REST API (e.g., `2604837472`)
- **Resolve**: Use **thread ID** from GraphQL (e.g., `PRRT_kwDOQZ9YJM5lbGiX`)

```bash
# Reply to the comment (use NUMERIC comment ID from REST API)
gh api repos/drillan/e-stat-mcp/pulls/$ARGUMENTS/comments/{numeric_comment_id}/replies \
  -f body='Thank you for the suggestion. After evaluation:

[REASON]

This is acceptable for our use case because [SPECIFIC REASON].

Resolving this conversation.'

# Resolve the thread (use THREAD ID from GraphQL)
gh api graphql -f query='
mutation {
  resolveReviewThread(input: {threadId: "PRRT_xxx"}) {
    thread { isResolved }
  }
}'
```

### Step 5: For ACCEPTED Comments - Implement Fixes

1. Read the affected files
2. Make the necessary changes
3. Verify changes don't break anything:

```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy . && uv run pytest
```

### Step 6: Summarize in PR Comment

```bash
gh pr comment $ARGUMENTS --body "## Code Review Response

### Addressed
- [Description of fix 1]
- [Description of fix 2]

### Declined (with rationale)
- [Issue]: [Reason for declining]

Commit: [commit hash]"
```

### Step 7: Commit Changes

```bash
git add -A
git commit -m "fix: address code review feedback

- [Change 1]
- [Change 2]
```

## Evaluation Criteria Details

### When to ACCEPT

- **Type safety issues**: Missing type annotations, incorrect types, mypy errors
- **Linting issues**: ruff warnings, formatting inconsistencies
- **Test coverage**: Missing tests for critical paths
- **Documentation**: Incorrect or outdated docstrings
- **Security issues**: Input validation, error handling gaps

### When to REJECT

- **Over-engineering**: Excessive abstraction, unnecessary complexity
- **Stylistic preferences**: Changes that don't improve readability or maintainability
- **Premature optimization**: Performance improvements without evidence of bottleneck
- **Over-testing**: Testing trivial code or implementation details
- **Type over-specification**: Overly complex type hints that reduce readability

## Example Reply Templates

### For Rejected Type Annotation Suggestions

```
Thank you for the type safety suggestion. After evaluation:

The current type annotation is intentionally broad to allow flexibility in this context. Adding more specific types would:
- Require significant refactoring of dependent code
- Not provide meaningful additional safety

Resolving this conversation.
```

### For Rejected Over-Engineering

```
Thank you for the suggestion. While the proposed abstraction has merits, it introduces unnecessary complexity for our current use case.

Our philosophy prioritizes simplicity and maintainability. See CLAUDE.md for project guidelines.

Resolving this conversation.
```

## Important Notes

- Always explain your reasoning when rejecting suggestions
- Be respectful in replies - AI reviewers provide valuable perspectives
- Prioritize fixes that improve code quality without adding complexity
- Run quality checks before committing: `uv run ruff check . && uv run ruff format --check . && uv run mypy . && uv run pytest`
- Check CLAUDE.md for project-specific guidelines
