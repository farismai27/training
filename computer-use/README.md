# Claude Computer Use - Setup

Automated QA testing and browser automation with Claude!

## Quick Start

```bash
# Set API key
export ANTHROPIC_API_KEY='your-key-here'

# Run quick start
./quick-start.sh

# Run automated QA test
cd scripts
python3 qa_test_mention_component.py
```

## What's Included

- **Computer Use Client** - Main client for Claude Computer Use API
- **Test Application** - @Mention component with intentional bugs
- **QA Automation** - Automated testing example from the lesson
- **Docker Setup** - Isolated testing environment

## Documentation

See [`../COMPUTER_USE.md`](../COMPUTER_USE.md) for complete documentation.

## Example Usage

### Test the @Mention Component

```bash
# Terminal 1: Start test server
cd test-app
python3 server.py

# Terminal 2: Run automated tests
cd scripts
python3 qa_test_mention_component.py
```

### Custom Tasks

```python
from computer_use_client import ComputerUseClient

client = ComputerUseClient()

task = "Navigate to Google and search for 'Claude AI'"
responses = client.run_task(task)
```

## Files

```
computer-use/
├── docker/                    # Docker setup
│   ├── Dockerfile
│   └── requirements-computer-use.txt
├── scripts/                   # Python scripts
│   ├── computer_use_client.py
│   └── qa_test_mention_component.py
├── test-app/                  # Test web app
│   ├── index.html
│   └── server.py
├── results/                   # Test reports (generated)
├── docker-compose.yml
├── quick-start.sh
└── README.md                  # This file
```

## Requirements

- Python 3.11+
- Anthropic API key
- Linux/Mac (Windows requires WSL)

## Dependencies

Installed automatically by quick-start.sh:
- anthropic
- pyautogui
- pillow
- selenium
- playwright

## Safety

Computer Use runs with PyAutoGUI fail-safe:
- Move mouse to screen corner to abort
- Test in Docker for isolation
- Review tasks before running

## Troubleshooting

### API Key Not Set
```bash
export ANTHROPIC_API_KEY='your-key'
```

### Dependencies Missing
```bash
pip install anthropic pyautogui pillow
```

### Permission Issues (Linux)
```bash
sudo apt-get install python3-tk python3-dev
```

## Learn More

- Full Documentation: [`../COMPUTER_USE.md`](../COMPUTER_USE.md)
- Anthropic Docs: https://docs.anthropic.com/computer-use

---

**Have Claude control your computer and automate QA testing!** 🤖
