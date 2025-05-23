# Security Policy

## Supported Versions

The following DC-API-X versions are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :x:                |

## Reporting a Vulnerability

We take the security of DC-API-X seriously. If you believe you've found a security vulnerability, please follow these steps:

1. **Do not disclose the vulnerability publicly**
2. **Email our security team** at security@datacosmos.com.br with a detailed description of the issue
3. Include steps to reproduce, impact, and any potential mitigations you've identified
4. If possible, encrypt your email using our [PGP key](https://datacosmos.com.br/keys/security-pgp-key.txt)

## What to Expect

- We will acknowledge receipt of your vulnerability report within 2 business days
- We will provide a more detailed response within 5 business days with our initial assessment
- We will work with you to understand and address the issue
- We'll keep you informed about our progress throughout the process

## Security Measures

DC-API-X implements the following security measures:

- Regular dependency scanning with Dependabot
- Static code analysis with CodeQL
- Security-focused code reviews for all pull requests
- Regular security audits with Bandit
- Container scanning for Docker images

## Security Best Practices

When using DC-API-X in your projects, we recommend following these security best practices:

1. Keep your dependency packages updated
2. Use the latest stable version of DC-API-X
3. Apply the principle of least privilege for API access controls
4. Properly secure your environment variables and secrets
5. Implement proper authentication and authorization in your API implementations

## Security Updates

Security updates are announced through:

- GitHub Security Advisories
- Release notes
- Our official mailing list (subscribe at security-announce@datacosmos.com.br)

Thank you for helping keep DC-API-X and its community safe!
