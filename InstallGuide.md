# Installation Guide

## Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose
- Node.js 14+ (for frontend)
- Git (for version control)

## System Requirements

- CPU: 4+ cores recommended
- RAM: 8GB minimum, 16GB recommended
- Storage: 100GB+ recommended for log storage
- OS: Linux (recommended), macOS, or Windows with WSL2

## Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/siem-dashboard.git
cd siem-dashboard
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install backend dependencies:
```bash
pip install -r requirements.txt
```

4. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

## Configuration

### Backend Configuration

1. Create environment file:
```bash
cp .env.example .env
```

2. Configure Elasticsearch:
```bash
cp config/elasticsearch.example.yml config/elasticsearch.yml
# Edit elasticsearch.yml with your settings
```

3. Configure RabbitMQ:
```bash
cp config/rabbitmq.example.conf config/rabbitmq.conf
# Edit rabbitmq.conf with your settings
```

### Frontend Configuration

1. Configure API endpoints:
```bash
cp frontend/.env.example frontend/.env
# Edit .env with your API settings
```

## Docker Setup

1. Build and start containers:
```bash
docker-compose build
docker-compose up -d
```

2. Verify services are running:
```bash
docker-compose ps
```

## Database Setup

1. Initialize Elasticsearch indices:
```bash
python scripts/init_elasticsearch.py
```

2. Verify Elasticsearch connection:
```bash
curl http://localhost:9200/_cat/health
```

## Security Setup

1. Generate security keys:
```bash
python scripts/generate_keys.py
```

2. Configure firewall rules:
```bash
sudo ufw allow 8000  # API
sudo ufw allow 3000  # Frontend
sudo ufw allow 9200  # Elasticsearch
sudo ufw allow 5672  # RabbitMQ
```

## Verification

1. Run the test suite:
```bash
pytest tests/
```

2. Start the development server:
```bash
uvicorn app.main:app --reload
```

3. Access the dashboard:
```
http://localhost:3000
```

## Troubleshooting

### Common Issues

1. Elasticsearch connection failed:
- Check Elasticsearch is running:
```bash
docker-compose ps elasticsearch
```
- Verify configuration:
```bash
cat config/elasticsearch.yml
```

2. RabbitMQ connection issues:
- Check RabbitMQ status:
```bash
docker-compose logs rabbitmq
```
- Verify credentials:
```bash
cat config/rabbitmq.conf
```

3. Frontend not loading:
- Check Node.js version:
```bash
node --version
```
- Verify API configuration:
```bash
cat frontend/.env
```

### Logs

- Application logs: `logs/app.log`
- Elasticsearch logs: `logs/elasticsearch.log`
- RabbitMQ logs: `logs/rabbitmq.log`

## Production Deployment

### Server Setup

1. Configure production server:
```bash
bash scripts/setup_production.sh
```

2. Set up SSL certificates:
```bash
certbot --nginx -d yourdomain.com
```

3. Configure monitoring:
```bash
bash scripts/setup_monitoring.sh
```

### Security Hardening

1. Configure authentication:
```bash
python scripts/setup_auth.py
```

2. Set up backup system:
```bash
bash scripts/setup_backup.sh
```

### Performance Tuning

1. Optimize Elasticsearch:
```bash
bash scripts/tune_elasticsearch.sh
```

2. Configure caching:
```bash
python scripts/setup_cache.py
```

## Additional Resources

- [Elasticsearch Documentation](https://www.elastic.co/guide/index.html)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/getting-started.html)