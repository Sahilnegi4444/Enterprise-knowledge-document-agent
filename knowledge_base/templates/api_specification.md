---
id: KB-003
title: API Specification Template
category: Template
document_type: API
version: 1.0
tags:
  - api
  - backend
---

# API Specification

## Purpose

API documentation defines how clients communicate with a service. It should clearly describe endpoints, requests, responses, and possible errors.

## Recommended Structure

- Overview
- Base URL
- Authentication
- Endpoints
- Request Schema
- Response Schema
- Error Codes
- Examples

## Best Practices

- Use RESTful endpoint names.
- Validate request data.
- Return consistent JSON.
- Use meaningful HTTP status codes.
- Include request examples.
- Document error responses.

## Common Mistakes

- Missing validation rules
- Inconsistent response format
- Poor endpoint naming
- No error documentation

## Example

POST /agent

Request

```json
{
  "request":"Create a project proposal"
}
```

Response

```json
{
  "status":"success"
}
```

## Summary

Good API documentation reduces integration effort and improves developer experience.