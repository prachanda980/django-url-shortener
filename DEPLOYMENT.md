# Deployment Guide to AWS EC2

This guide explains how to deploy the URL Shortener application to an AWS EC2 instance using Docker and Docker Compose.

## 1. Prerequisites on EC2

Ensure your EC2 instance has Docker and Docker Compose installed.

```bash
# Update and install Docker
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo usermod -aG docker $USER
# Log out and log back in for group changes to take effect
```

## 2. Prepare the Application

1. **Clone your repository** on the EC2 instance:
   ```bash
   git clone <your-repo-url>
   cd vrittech
   ```

2. **Create the environment file**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set your `SECRET_KEY`, `ALLOWED_HOSTS`, and `SITE_URL`.

## 3. Deployment

Run the follow command to build and start the services:

```bash
docker-compose up -d --build
```

This will:
- Build the Django application image.
- Start a Redis container.
- Start the Django web server (running via Gunicorn on port 8000).
- Start the Celery worker for background tasks.
- Run database migrations automatically.
- Collect static files automatically.

## 4. Troubleshooting

- **Check logs**: `docker-compose logs -f`
- **Check container status**: `docker-compose ps`
- **Restart services**: `docker-compose restart`

## 5. Next Steps (Optional)

- **Reverse Proxy**: Set up Nginx on the EC2 host (or in another container) to serve the app on port 80/443 with SSL (Certbot).
- **External Database**: For production, consider using AWS RDS (PostgreSQL) instead of SQLite. Update the `DATABASE_URL` in `.env` accordingly.
