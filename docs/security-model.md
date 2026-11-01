# Security model

SentinelTrace is defensive and offline by design. It never executes log contents, contacts monitored hosts, blocks traffic, or performs remediation. Uploads are restricted to the ingestion endpoint and capped at 10 MiB. Production deployments should add analyst authentication, HTTPS, a reverse proxy, malware scanning for uploads, PostgreSQL, and operational rate limiting.
