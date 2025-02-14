# SIEM Dashboard

A comprehensive Security Information and Event Management (SIEM) dashboard designed for real-time security monitoring, log analysis, and threat detection.

## Features

- Real-time log ingestion and processing
- Advanced security alert management
- Threat detection and analysis
- Interactive security metrics visualization
- Detailed security reporting and analytics
- Customizable dashboard views
- Multi-source log aggregation

## Quick Start

1. Install the package:
```bash
pip install -r requirements.txt
```

2. Configure Elasticsearch:
```bash
cp config/elasticsearch.example.yml config/elasticsearch.yml
# Edit elasticsearch.yml with your settings
```

3. Start the services:
```bash
docker-compose up -d
```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

## Requirements

- Python 3.8+
- Elasticsearch 7.x
- RabbitMQ
- Required packages listed in requirements.txt

## Installation

For detailed installation instructions, see [Installation Guide](docs/installation.md).

1. Clone the repository:
```bash
git clone https://github.com/yourusername/siem-dashboard.git
cd siem-dashboard
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

For detailed usage instructions, see [Usage Guide](docs/usage.md).

Basic usage example:
```python
from app.services.log_ingestion import LogIngestionService
from app.services.alert_manager import AlertManager

# Initialize services
log_service = LogIngestionService()
alert_manager = AlertManager()

# Ingest logs
await log_service.create_log(log_entry)

# Create alert
await alert_manager.create_alert(alert)
```

## Development

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [Elastic Security](https://www.elastic.co/security)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)