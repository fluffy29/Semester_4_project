# Security Threats and Countermeasures

- Token leakage: Store JWT secret in env vars, rotate secrets, set reasonable expirations. Always use HTTPS in production.
- Prompt injection: Use system prompts to constrain model, sanitize/validate inputs, and avoid executing model outputs.
- Abuse of admin endpoints: Enforce role-based access and audit access.
- SSRF via external API calls: Use allowlists for outbound hosts and timeouts; avoid using unvalidated URLs from user input.
- Model poisoning/data exfiltration: With PRIVACY_STORE_MESSAGES=false, we avoid persisting content. If enabling, sanitize and limit retention.
- Rate limiting: Per-IP in-memory bucket to reduce abuse and DoS.
- Brute force on login: Same rate limiting on auth route and generic error messages.
