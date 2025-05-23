# Security Policy

## Supported Versions

The following DC-API-X versions are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :x:                |

## Reporting a Vulnerability

We take the security of DC-API-X seriously. If you believe you've found a security vulnerability, please follow these guidelines:

### Preferred Method - GitHub Private Vulnerability Reporting

DC-API-X has enabled GitHub's Private Vulnerability Reporting feature. This is our preferred method for receiving security reports as it ensures proper tracking and security.

1. Go to the [Security tab](https://github.com/datacosmos-br/dc-api-x/security) of the DC-API-X repository
2. Select "Report a vulnerability"
3. Fill out the form with a detailed description of the vulnerability
4. GitHub will keep your report private and notify project maintainers

### Alternative Method - Email

If you prefer not to use GitHub's reporting feature:

1. **Do not disclose the vulnerability publicly**
2. Email our security team at <security@datacosmos.com.br> with:
   - A detailed description of the issue
   - Steps to reproduce
   - Potential impact
   - Suggested fixes (if any)
3. Use the subject line: "DC-API-X Security Vulnerability"
4. If possible, encrypt your email using our [PGP key](https://datacosmos.com.br/keys/security-pgp-key.txt)

## What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 2 business days
- **Assessment**: We will provide a more detailed response within 5 business days with our initial assessment
- **Updates**: We will keep you informed about our progress throughout the process
- **Resolution**: Once the vulnerability is fixed, we will:
  - Notify you
  - Issue a security advisory
  - Credit you (unless you prefer to remain anonymous)
  - Release a patched version

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
- Our official mailing list (subscribe at <security-announce@datacosmos.com.br>)

Thank you for helping keep DC-API-X and its community safe!
