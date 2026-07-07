---
id: KB-007
title: REST API Design Guidelines
category: Best Practices
document_type: API
version: 1.0
tags:
  - api
  - rest
  - backend
---

# REST API Design Guidelines

## Purpose

REST APIs should be simple, consistent, and predictable for clients to consume.

## Best Practices

- Use nouns for resources.
- Keep endpoint names descriptive.
- Validate request inputs.
- Return consistent JSON responses.
- Use appropriate HTTP status codes.
- Version public APIs.
- Include helpful error messages.

## Recommended Status Codes

- 200 OK
- 201 Created
- 400 Bad Request
- 401 Unauthorized
- 404 Not Found
- 500 Internal Server Error

## Common Mistakes

- Using verbs in URLs.
- Returning inconsistent response formats.
- Missing validation.
- Exposing internal implementation details.

## Example

Good

GET /v1/projects/12

POST /v1/agent

Bad

GET /getProject?id=12

POST /runAgentNow

## Summary

Consistent API design improves developer experience and simplifies future maintenance.