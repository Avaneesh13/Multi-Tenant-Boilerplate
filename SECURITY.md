# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of Flask PostgreSQL Multi-Tenant Boilerplate seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please do NOT report security vulnerabilities through public GitHub issues.

Instead, please report them via email to: **[your-security-email@example.com]**

Please include the following information in your report:
- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

### What to expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours.
- **Investigation**: We will investigate and validate the issue within 7 days.
- **Updates**: We will keep you informed of our progress throughout the process.
- **Resolution**: We aim to resolve critical vulnerabilities within 30 days.
- **Disclosure**: We follow responsible disclosure practices.

## Security Best Practices

When using this boilerplate, please follow these security guidelines:

### Database Security
- **Use strong passwords** for database users
- **Limit database user permissions** to only what's necessary
- **Use SSL/TLS connections** to the database in production
- **Regularly update PostgreSQL** to the latest stable version
- **Monitor database access logs** for suspicious activity

### Application Security
- **Never commit credentials** to version control
- **Use environment variables** for sensitive configuration
- **Validate all input** before database operations
- **Implement proper authentication** and authorization
- **Use HTTPS** in production environments
- **Keep dependencies updated** regularly

### Multi-Tenant Security
- **Verify tenant isolation** in your implementation
- **Validate tenant access** in all operations
- **Use parameterized queries** to prevent SQL injection
- **Implement tenant-aware logging** for audit trails
- **Test tenant boundary enforcement** regularly

### Production Deployment
- **Use a reverse proxy** (nginx, Apache) in front of Flask
- **Run with a WSGI server** (Gunicorn, uWSGI) instead of Flask's dev server
- **Enable database connection pooling** appropriately
- **Implement proper error handling** to avoid information disclosure
- **Use monitoring and alerting** for suspicious activities

## Known Security Considerations

### Database Connections
- The application uses connection pooling which may reuse connections across tenants
- Ensure proper connection cleanup and tenant context isolation

### Migration System
- Migration files can contain sensitive operations
- Review all migration files before applying to production
- Use the checkpoint recovery system to handle failed migrations safely

### Environment Variables
- `.env` files contain sensitive information
- Ensure `.env` files are not deployed to production
- Use proper secrets management in production environments

## Security Updates

Security updates will be released as patch versions and announced through:
- GitHub Security Advisories
- Release notes in CHANGELOG.md
- Email notifications to maintainers

## Contributing to Security

If you want to contribute to improving the security of this project:
1. Review the codebase for potential security issues
2. Suggest security improvements through issues or pull requests
3. Help improve security documentation
4. Contribute security-focused tests

Thank you for helping to keep Flask PostgreSQL Multi-Tenant Boilerplate secure! 