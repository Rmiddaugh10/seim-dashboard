# Usage Guide

## Basic Usage

1. Start the services:
```bash
docker-compose up -d
```

2. Access the dashboard:
```
http://localhost:3000
```

## Configuration Options

### Log Ingestion Settings
- batch_size: Number of logs to process in each batch
- processing_interval: Frequency of log processing (in seconds)
- retention_period: Log retention period (in days)

### Alert Thresholds
- critical: Threshold for critical severity alerts
- high: Threshold for high severity alerts
- medium: Threshold for medium severity alerts
- low: Threshold for low severity alerts

### Dashboard Settings
- refresh_rate: Dashboard refresh rate (in seconds)
- max_alerts: Maximum number of alerts to display
- default_timespan: Default time range for metrics

## Features

### Log Management
- Real-time log ingestion
- Multi-source log aggregation
- Log filtering and search
- Custom log parsing rules
- Log retention policies

### Alert Management
- Real-time alert generation
- Alert severity classification
- Alert assignment and tracking
- Custom alert rules
- Alert notification system

### Security Analytics
- Threat pattern detection
- Anomaly detection
- Security metrics calculation
- Geographic attack visualization
- Trend analysis

## API Examples

1. Create a log entry:
```bash
curl -X POST http://localhost:8000/api/v1/logs \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Failed login attempt",
    "level": "warning",
    "source": "auth_service",
    "host": "web-server-01"
  }'
```

2. Create an alert:
```bash
curl -X POST http://localhost:8000/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Multiple Failed Login Attempts",
    "description": "Detected multiple failed login attempts from single IP",
    "severity": "high",
    "source": "authentication"
  }'
```

3. Get security metrics:
```bash
curl http://localhost:8000/api/v1/metrics/dashboard \
  -H "Content-Type: application/json"
```

## Dashboard Views

### Main Dashboard
- Security overview
- Recent alerts
- Key metrics
- Active threats
- System health

### Log Analysis
- Log search and filtering
- Log aggregation
- Pattern analysis
- Source distribution
- Timeline view

### Alert Management
- Alert queue
- Alert details
- Assignment tracking
- Resolution workflow
- Alert history

### Reports
- Security reports
- Compliance reports
- Trend analysis
- Custom reports
- Export options