# Contributing to Flask PostgreSQL Multi-Tenant Boilerplate

Thank you for your interest in contributing to this project! This boilerplate aims to provide a solid foundation for building multi-tenant Flask applications with PostgreSQL.

## How to Contribute

### Reporting Issues

1. **Search existing issues** first to avoid duplicates
2. **Use issue templates** when available
3. **Provide detailed information**:
   - Python version
   - PostgreSQL version
   - Operating system
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages/logs

### Suggesting Enhancements

1. **Check existing feature requests** to avoid duplicates
2. **Clearly describe the enhancement**:
   - Use case and motivation
   - Proposed solution
   - Alternative solutions considered
   - Potential impact on existing functionality

### Code Contributions

#### Getting Started

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/Avaneesh13/Multi-Tenant-Boilerplate.git
   cd flask-postgresql-multi-tenant
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Set up your development environment** using the setup script:
   ```bash
   python scripts/run_migrations/run_initial_setup.py
   ```

#### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Make your changes** following the coding standards
3. **Test your changes** thoroughly
4. **Commit your changes**:
   ```bash
   git commit -m "Add feature: brief description"
   ```
5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Create a Pull Request** from your fork to the main repository

#### Coding Standards

- **Follow PEP 8** for Python code style
- **Use meaningful variable and function names**
- **Add docstrings** to functions and classes
- **Keep functions focused** and reasonably sized
- **Add comments** for complex logic
- **Use type hints** where appropriate

#### Testing

- Test your changes with different PostgreSQL versions
- Verify that both system and tenant migrations work correctly
- Test the checkpoint recovery system
- Ensure all existing functionality still works

#### Commit Messages

Use clear, descriptive commit messages:
- `feat: add new tenant isolation feature`
- `fix: resolve migration rollback issue`
- `docs: update setup instructions`
- `refactor: improve connection pooling`
- `test: add unit tests for migration system`

### Documentation

- Update README.md if your changes affect setup or usage
- Add inline code comments for complex logic
- Update API documentation for new endpoints
- Include examples for new features

## Development Setup

### Database Setup for Development

1. **Install PostgreSQL** (version 12+ recommended)
2. **Create a development user**:
   ```sql
   CREATE USER dev_user WITH PASSWORD 'dev_password' CREATEDB;
   ```
3. **Configure your .env file**:
   ```
   DB_USERNAME=dev_user
   DB_PASSWORD=dev_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

### Running Tests

Currently, this project focuses on manual testing. Future contributions for automated testing are welcome!

**Manual Testing Checklist:**
- [ ] Initial setup script runs successfully
- [ ] System migrations apply correctly
- [ ] Tenant migrations apply with checkpoint recovery
- [ ] Flask server starts and all endpoints respond
- [ ] Database isolation between tenants works
- [ ] Migration rollback works on failures

## Areas for Contribution

We welcome contributions in these areas:

### High Priority
- **Unit and integration tests**
- **Docker containerization**
- **Performance optimizations**
- **Security enhancements**
- **Better error handling**

### Medium Priority
- **Additional database backends** (MySQL, SQLite)
- **Admin dashboard** for tenant management
- **Migration scheduling** and automation
- **Monitoring and logging** improvements
- **Configuration management** enhancements

### Documentation
- **Video tutorials**
- **Deployment guides** (Docker, AWS, GCP, Azure)
- **Architecture deep-dive**
- **Performance tuning guide**
- **Security best practices**

## Code Review Process

1. **All contributions** require review by project maintainers
2. **Feedback** will be provided constructively
3. **Changes may be requested** before merge
4. **Be patient** - reviews may take a few days

## Community Guidelines

- **Be respectful** and professional
- **Help others** learn and contribute
- **Share knowledge** and best practices
- **Acknowledge others'** contributions
- **Follow the Code of Conduct**

## Questions?

- **Open an issue** for general questions
- **Check existing discussions** for common topics
- **Be specific** about what you need help with

Thank you for contributing to make this boilerplate better for everyone! 🚀 