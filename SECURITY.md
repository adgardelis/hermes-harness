# Security policy

## Reporting a vulnerability

Please do not disclose suspected vulnerabilities in a public issue, discussion, pull request, or social-media post.

Use GitHub's **Report a vulnerability** private reporting flow for this repository. Include:

- affected commit or release;
- reproduction steps;
- expected and observed behavior;
- whether payload confidentiality, session isolation, filesystem containment, or recovery integrity is affected;
- suggested mitigation, if known.

Do not attach real secrets, production payloads, capability URIs, user session identifiers, or credentials. Use synthetic test data.

## Security-sensitive boundaries

The following are considered load-bearing:

- same-session capability authorization;
- bearer-token confidentiality;
- AES-GCM authentication and plaintext digest verification;
- symlink, reparse-point, FIFO/device, ownership, and mode checks;
- fail-closed behavior for scoped persistence failures;
- ordinary-path rejection in capability-only transports.

## Supported versions

HERMES HARNESS is currently a research preview. Security fixes target the latest commit on `main` and the exact upstream proposal while it remains open.
