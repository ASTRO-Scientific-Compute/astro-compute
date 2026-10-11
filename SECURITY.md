# Security policy

**Status: experimental public reference preview. No supported production deployment is announced.**

## Reporting a vulnerability

Use GitHub's private **Report a vulnerability** action in this repository's Security tab if it is available. If no private reporting action is available, open only a nonsensitive request for a private contact channel; do not disclose exploit details, credentials, researcher data or private logs in an issue. No private email address is advertised or assumed here.

A useful private report states the affected component/revision, expected behavior, observed behavior, impact and a minimal sanitized reproduction. Avoid testing against systems or data you do not own or have authorization to assess. No response-time SLA or bug bounty is promised.

## Secrets and data handling

Never commit API keys, passwords, access tokens, wallet secrets, private keys, .env files, machine credentials, personal data or researcher datasets. Use minimal local test inputs. Git ignore rules reduce accidental inclusion but do not sanitize a staged file. Review every upload and rotate/revoke any exposed credential through its issuer; deleting a commit is not sufficient remediation.

Benchmark output retention is profile-only. Research result deletion requires a real verified MainNode ACK, not the simulator. Independent validation, authenticated receipts and full network isolation are future integration gates, not completed protections of a deployed network.
