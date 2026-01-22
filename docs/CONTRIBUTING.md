# Contributing to Daily Tasker

First off, thank you for considering contributing to Daily Tasker! It's people like you that make Daily Tasker such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by respect and professionalism. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

**Bug Report Template:**
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g. Windows 10, macOS 12, Ubuntu 20.04]
 - Browser: [e.g. Chrome 96, Firefox 95]
 - Python Version: [e.g. 3.9.7]
 - Flask Version: [e.g. 2.3.3]

**Additional context**
Any other context about the problem.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description** of the enhancement
- **Step-by-step description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List any alternative solutions** you've considered

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Submit a pull request**

**Pull Request Template:**
```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests you ran

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code where necessary
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have tested on multiple browsers (if UI changes)
```

## Development Setup

1. **Clone your fork:**
```bash
git clone https://github.com/your-username/daily-tasker.git
cd daily-tasker
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create a feature branch:**
```bash
git checkout -b feature/your-feature-name
```

5. **Make your changes and test**

6. **Commit your changes:**
```bash
git add .
git commit -m "Add: Brief description of your changes"
```

## Coding Standards

### Python Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use 4 spaces for indentation (not tabs)
- Maximum line length: 88 characters (Black formatter default)
- Use descriptive variable names

**Good:**
```python
def calculate_completion_percentage(completed_tasks, total_tasks):
    """Calculate the completion percentage of tasks."""
    if total_tasks == 0:
        return 0
    return round((completed_tasks / total_tasks) * 100)
```

**Bad:**
```python
def calc(c, t):
    if t==0:return 0
    return round((c/t)*100)
```

### Documentation

- Add docstrings to all functions and classes
- Use clear, concise comments for complex logic
- Update README.md when adding new features

**Docstring Format:**
```python
def function_name(param1, param2):
    """
    Brief description of the function.
    
    Longer description if needed.
    
    Args:
        param1 (type): Description of param1
        param2 (type): Description of param2
    
    Returns:
        type: Description of return value
    
    Raises:
        ExceptionType: Description of when raised
    """
    pass
```

### HTML/CSS/JavaScript

- Use semantic HTML5 elements
- Follow existing naming conventions for CSS classes
- Keep JavaScript functions focused and single-purpose
- Add comments for complex logic

### Database Changes

If your contribution requires database schema changes:

1. Document the changes clearly
2. Provide migration instructions
3. Test with existing data
4. Consider backward compatibility

## Commit Messages

Write clear, descriptive commit messages:

**Good:**
```
Add: User profile settings page
Fix: Dashboard progress bar calculation error
Update: Improve email reminder scheduling
Docs: Add installation instructions for Windows
```

**Bad:**
```
fixed stuff
update
changes
wip
```

### Commit Message Format

```
Type: Brief description (50 chars or less)

More detailed explanation if needed (wrap at 72 chars)

- Bullet points for multiple changes
- Use present tense ("Add feature" not "Added feature")
- Reference issues: Fixes #123
```

**Types:**
- `Add:` New feature or functionality
- `Fix:` Bug fix
- `Update:` Changes to existing features
- `Remove:` Removal of features or code
- `Docs:` Documentation changes
- `Style:` Code style changes (formatting, etc.)
- `Refactor:` Code refactoring
- `Test:` Adding or updating tests
- `Chore:` Maintenance tasks

## Testing

Before submitting a pull request:

1. **Test all functionality** affected by your changes
2. **Test on multiple browsers** (Chrome, Firefox, Safari, Edge)
3. **Test mobile responsiveness** if UI changes were made
4. **Check for console errors**
5. **Verify database operations** don't cause issues

### Manual Testing Checklist

- [ ] Registration and login work
- [ ] Adding/editing/deleting tasks work
- [ ] Adding/deleting categories work
- [ ] Daily task completion tracking works
- [ ] Progress calculations are correct
- [ ] Theme switching works
- [ ] PDF export works
- [ ] Email reminders work (if configured)
- [ ] Mobile interface is responsive

## Questions?

Feel free to open an issue with your question or contact the maintainers:
- Email: israrmobin@gmail.com
- GitHub: [@Israr-Mobin](https://github.com/Israr-Mobin)

## Recognition

Contributors will be recognized in the project documentation and release notes.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Daily Tasker! 🎉