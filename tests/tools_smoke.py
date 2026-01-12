import json
import time

# Minimal generate_document copied from demo.py for smoke-testing
def generate_document(doc_type, content):
    templates = {
        "prd": (
            "# Product Requirements Document\n"
            "## Problem Statement\n"
            "{problem}\n"
            "## Solution Overview\n"
            "{solution}\n"
            "## Requirements\n"
            "{requirements}\n"
        ),
        "roadmap": (
            "# OneSuite Roadmap - {timeline}\n"
            "## MVP Phase\n"
            "{mvp}\n"
            "## V1 Features\n"
            "{v1}\n"
            "## Scale Phase\n"
            "{scale}\n"
        ),
        "spec": (
            "# Specification - {title}\n"
            "## Overview\n{overview}\n"
            "## Details\n{details}\n"
        )
    }
    if doc_type not in templates:
        raise ValueError(f"Unknown doc_type: {doc_type}")
    return templates[doc_type].format(**content)


def simulate_create_jira_ticket(summary, description, issue_type='Task', project='ONESUITE'):
    fake_key = f"ONESUITE-{int(time.time()) % 100000}"
    fake_url = f"https://jira.example.com/browse/{fake_key}"
    return {"key": fake_key, "url": fake_url, "summary": summary}


if __name__ == '__main__':
    print('Running tools_smoke tests...')

    prd_content = {
        'problem': 'Agencies need unified agent orchestration',
        'solution': 'Provide OneSuite Core for common services',
        'requirements': '- Auth\n- Routing\n- Telemetry'
    }

    prd = generate_document('prd', prd_content)
    print('\nGenerated PRD snippet:\n')
    print(prd[:1000])

    jira = simulate_create_jira_ticket(
        summary='Add authentication middleware',
        description='Implement OAuth2 middleware for agent communication',
        issue_type='Story'
    )
    print('\nSimulated Jira ticket:')
    print(json.dumps(jira, indent=2))
