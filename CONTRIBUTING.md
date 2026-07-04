# Contributing

## How to contribute

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Development

### Prerequisites
- Docker
- Node.js 22+
- Python 3.12+

### Local setup
`ash
git clone git@github.com:diosmentiras/Nexus-Lore.git
cd Nexus-Lore
cp .env.example .env
# start database
docker run -d --name nexus-pg -e POSTGRES_DB=nexus_lore -e POSTGRES_USER=nexus -e POSTGRES_PASSWORD=nexus_pass -p 5432:5432 postgres:16-alpine
# backend
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload
# frontend
cd frontend && npm install && npm run dev
`

## Code style
- Python: ruff
- Vue/TS: prettier
