# Contributing to Football Lineup Bot

First off, thank you for considering contributing to Football Lineup Bot! 🎉

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Style Guidelines](#style-guidelines)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **Screenshots** (if applicable)
- **Environment details** (OS, Python version, Node version)

**Template:**

```markdown
## Bug Description

Brief description of the bug

## Steps to Reproduce

1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior

What should happen

## Actual Behavior

What actually happens

## Environment

- OS: [e.g., Ubuntu 22.04]
- Python: [e.g., 3.11.5]
- Node: [e.g., 20.9.0]
```

### 💡 Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use case** - Why is this enhancement needed?
- **Proposed solution** - How should it work?
- **Alternatives** - What alternatives have you considered?
- **Additional context** - Any other context or screenshots

### 🔧 Pull Requests

1. Fork the repo and create your branch from `main`
2. Follow the development setup instructions
3. Make your changes following our style guidelines
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation as needed
7. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- UV package manager
- Git

### Local Development

1. **Fork and Clone**

```bash
git clone https://github.com/YOUR_USERNAME/football-lineup-bot.git
cd football-lineup-bot
```

2. **Create Branch**

```bash
git checkout -b feature/your-feature-name
```

3. **Install Dependencies**

```bash
# Backend
uv sync

# Frontend
cd frontend
npm install
```

4. **Set Up Pre-commit Hooks**

```bash
pre-commit install
```

5. **Run Tests**

```bash
# Backend tests
uv run pytest

# Frontend tests
cd frontend
npm test
```

## Development Workflow

### 1. Before Starting Work

- Check existing issues and PRs
- Create or claim an issue
- Discuss approach if it's a major change

### 2. During Development

- Write clean, readable code
- Add unit tests for new features
- Update documentation
- Run linters and formatters

### 3. Before Submitting

- Run all tests: `uv run pytest`
- Run linters: `uv run ruff check .`
- Format code: `uv run ruff format .`
- Run pre-commit: `pre-commit run --all-files`

## Style Guidelines

### Python Code Style

We use Ruff for Python linting and formatting:

```python
# Good
def calculate_lineup_score(players: list[Player]) -> float:
    """Calculate the overall score for a lineup."""
    return sum(player.rating for player in players) / len(players)

# Bad
def calc(p):
    s = 0
    for x in p:
        s += x.rating
    return s / len(p)
```

**Guidelines:**

- Use type hints
- Write docstrings for all public functions
- Keep functions under 20 lines
- One function = one responsibility
- Use descriptive variable names

### TypeScript/React Style

```typescript
// Good
interface Player {
  name: string;
  position: string;
  number: number;
}

const PlayerCard: React.FC<{ player: Player }> = ({ player }) => {
  return (
    <div className="player-card">
      <h3>{player.name}</h3>
      <p>{player.position}</p>
    </div>
  );
};

// Bad
const PlayerCard = (props: any) => {
  return <div>{props.player.name}</div>;
};
```

**Guidelines:**

- Use TypeScript strictly
- Define interfaces for all props
- Use functional components with hooks
- Keep components small and focused

### Testing Guidelines

```python
# Good test
def test_prediction_service_returns_valid_lineup():
    """Test that prediction service returns 11 players."""
    service = PredictionService()
    result = await service.predict("Arsenal")

    assert len(result.lineup) == 11
    assert all(player.position for player in result.lineup)
    assert result.formation in VALID_FORMATIONS

# Bad test
def test_prediction():
    """Test prediction."""
    service = PredictionService()
    result = await service.predict("Arsenal")
    assert result is not None
```

**Guidelines:**

- Write descriptive test names
- Test one thing per test
- Use fixtures for common setup
- Mock external dependencies
- Aim for 80% coverage minimum

## Commit Guidelines

We follow Conventional Commits specification:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Examples

```bash
# Good commits
git commit -m "feat(bot): add lineup comparison command"
git commit -m "fix(api): handle team name with spaces"
git commit -m "docs: update API documentation"
git commit -m "test(prediction): add edge case tests"

# Bad commits
git commit -m "fixed stuff"
git commit -m "WIP"
git commit -m "updates"
```

## Pull Request Process

### 1. PR Title

Follow the commit message format:

- `feat(bot): add lineup comparison command`
- `fix(api): handle rate limiting correctly`

### 2. PR Description Template

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

- [ ] All tests pass
- [ ] Added new tests
- [ ] Manual testing completed

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

### 3. Review Process

1. **Automated Checks**: CI/CD must pass
2. **Code Review**: At least one maintainer approval
3. **Testing**: All tests must pass
4. **Documentation**: Must be updated if needed

### 4. After Merge

- Delete your feature branch
- Update your local main branch
- Close related issues

## Project Structure

When adding new features, follow the existing structure:

```
backend/
├── app/
│   ├── adapters/     # External service integrations
│   ├── bot/          # Telegram bot logic
│   ├── models/       # Data models
│   ├── routers/      # API endpoints
│   └── services/     # Business logic
└── tests/            # Test files (mirror app structure)

frontend/
├── src/
│   ├── api/          # API client
│   ├── components/   # React components
│   ├── hooks/        # Custom hooks
│   └── utils/        # Utility functions
└── tests/            # Frontend tests
```

## Getting Help

- **Discord**: [Join our Discord](#)
- **GitHub Discussions**: [Ask questions](https://github.com/t3chn/football-lineup-bot/discussions)
- **Issues**: [Report bugs](https://github.com/t3chn/football-lineup-bot/issues)

## Recognition

Contributors will be recognized in:

- README.md contributors section
- Release notes
- Special thanks in documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Football Lineup Bot! ⚽ 🤖
