# Webapp Testing

<p align="center">
  <strong>Enterprise-grade Web Application Testing Solution</strong><br>
  End-to-end testing, visual regression, performance testing with multi-browser support
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#license">License</a>
</p>

---

## Features

- ✅ **End-to-End Testing** - Simulate user workflows and validate business logic
- ✅ **Visual Regression Testing** - Pixel-perfect screenshot comparison
- ✅ **Performance Testing** - Web Vitals metrics collection and analysis
- ✅ **Multi-Browser Support** - Chromium, Firefox, and WebKit
- ✅ **Rich Reports** - HTML and JSON test reports
- ✅ **CI/CD Ready** - Easy integration with GitHub Actions, GitLab CI, etc.

## Installation

### Prerequisites

- Python 3.10+
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
playwright install
```

## Quick Start

### 1. Basic Test

```bash
python main.py --action test --url https://example.com
```

### 2. Take Screenshot

```bash
python main.py --action visual --url https://example.com --screenshot-path ./screenshot.png
```

### 3. Performance Test

```bash
python main.py --action performance --url https://example.com
```

### 4. Visual Comparison

```bash
python main.py --action compare \
  --baseline-path ./baseline.png \
  --screenshot-path ./current.png \
  --threshold 0.05
```

## Documentation

### Actions

| Action | Description |
|--------|-------------|
| `test` | Run end-to-end tests |
| `visual` | Take screenshots and compare with baseline |
| `performance` | Collect Web Vitals performance metrics |
| `compare` | Compare two screenshots |
| `generate-config` | Generate test configuration template |

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--action` | string | required | Action to perform |
| `--url` | string | - | Target URL |
| `--browser` | string | chromium | Browser type (chromium/firefox/webkit) |
| `--headless` | boolean | true | Run in headless mode |
| `--screenshot-path` | string | auto | Screenshot save path |
| `--baseline-path` | string | - | Baseline screenshot for comparison |
| `--output-dir` | string | ./test-results | Output directory |
| `--viewport-width` | integer | 1920 | Viewport width |
| `--viewport-height` | integer | 1080 | Viewport height |
| `--threshold` | float | 0.1 | Visual comparison threshold (0-1) |
| `--timeout` | integer | 30000 | Operation timeout in milliseconds |

### Examples

#### E2E Test with Custom Viewport

```bash
python main.py --action test \
  --url https://example.com \
  --browser firefox \
  --viewport-width 1280 \
  --viewport-height 720 \
  --headless false
```

#### Visual Regression Test

```bash
# Generate baseline
python main.py --action visual \
  --url https://app.example.com \
  --screenshot-path ./baselines/homepage.png

# Compare after changes
python main.py --action visual \
  --url https://app.example.com \
  --baseline-path ./baselines/homepage.png \
  --threshold 0.05
```

#### Performance Benchmark

```bash
python main.py --action performance \
  --url https://example.com \
  --browser chromium \
  --output-dir ./perf-results
```

## Test Reports

### HTML Report

After running tests, an HTML report is automatically generated:

```
./test-results/report.html
```

### JSON Report

Structured JSON report for CI/CD integration:

```json
{
  "timestamp": "2026-02-21T10:30:00",
  "results": {
    "total": 10,
    "passed": 9,
    "failed": 1,
    "success": false
  }
}
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Web Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install Dependencies
        run: |
          pip install -r requirements.txt
          playwright install
      
      - name: Run Tests
        run: |
          python main.py --action test --url http://localhost:3000
      
      - name: Upload Results
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: ./test-results/
```

### GitLab CI

```yaml
stages:
  - test

web_test:
  stage: test
  image: python:3.10
  before_script:
    - pip install -r requirements.txt
    - playwright install
  script:
    - python main.py --action test --url http://localhost:3000
  artifacts:
    paths:
      - test-results/
```

## Architecture

```
webapp-testing/
├── main.py              # Main entry point
├── skill.json           # Skill manifest
├── SKILL.md             # Chinese documentation
├── README.md            # English documentation
├── LICENSE              # MIT License
├── requirements.txt     # Dependencies
└── tests/               # Test suite
    ├── __init__.py
    └── test_webapp_testing.py
```

### Core Components

- **WebAppTester** - Main testing orchestrator
- **VisualComparator** - Screenshot comparison engine
- **TestReporter** - Report generation

## Browser Support

| Browser | Engine | Status |
|---------|--------|--------|
| Chrome/Edge | Chromium | ✅ Full Support |
| Firefox | Gecko | ✅ Full Support |
| Safari | WebKit | ✅ Full Support |

## Performance Metrics

Collected Web Vitals:

- **LCP** (Largest Contentful Paint) - Loading performance
- **FID** (First Input Delay) - Interactivity
- **CLS** (Cumulative Layout Shift) - Visual stability
- **FCP** (First Contentful Paint) - First content render
- **TTFB** (Time to First Byte) - Server response time

## Troubleshooting

### Browser Installation

```bash
# Install all browsers
playwright install

# Install specific browser
playwright install chromium

# Install system dependencies
playwright install-deps
```

### Common Issues

**Screenshot comparison fails**
- Ensure pages are fully loaded before screenshot
- Adjust `--threshold` parameter
- Check viewport dimensions match

**Performance metrics are null**
- Some metrics require user interaction
- Ensure page uses standard Web Vitals API

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Playwright](https://playwright.dev/)
- Part of [Godlike Kimi Skills](https://github.com/godlike-kimi-skills)

---

<p align="center">
  Made with ❤️ by Godlike Kimi Skills
</p>
