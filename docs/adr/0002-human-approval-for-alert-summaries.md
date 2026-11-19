# Title

ADR 0002: Human Approval for Alert Summaries

## Status

Accepted

## Context

An incorrect or misleading automated alert summary sent to the on-call channel
could cause the on-call engineer to under-react or over-react to a real incident.
A few minutes of approval delay costs much less than a bad summary during an
active incident.

## Decision

The capstone's n8n alert-summary workflow routes each generated summary to a human
for approval before it is sent to the on-call channel, instead of sending it
automatically.

## Consequences

- Human approval addresses the risk that a misleading summary causes the on-call
  engineer to under-react or over-react during an active incident.
- Summary delivery is slower because it waits for approval.
- Delivery depends on someone being available to approve.