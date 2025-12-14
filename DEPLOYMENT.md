# Deployment Guide for Render

## Quick Deploy

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Instagram Barter System"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Create Render Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: instagram-barter-system
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python app.py`
     - **Instance Type**: Free (or paid for production)

3. **Set Environment Variables**
   In Render dashboard, add these environment variables:
   - `SECRET_KEY`: Generate a strong secret key (e.g., use `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `ADMIN_PASSWORD`: Set a strong admin password

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Your app will be available at: `https://your-app-name.onrender.com`

## Important Notes

### Database Persistence
- SQLite database will reset on each deployment (Render's ephemeral filesystem)
- For production, consider upgrading to PostgreSQL:
  1. Add `psycopg2-binary` to requirements.txt
  2. Create a PostgreSQL database on Render
  3. Update `SQLALCHEMY_DATABASE_URI` in config.py to use `DATABASE_URL` environment variable

### Session Files
- Instagram session files are stored in `sessions/` folder
- These will also reset on deployment
- Consider using cloud storage (S3, Google Cloud Storage) for production

### Production Recommendations

1. **Use PostgreSQL**
   ```python
   # config.py
   SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///barter.db'
   ```

2. **Encrypt Passwords**
   - Don't store Instagram passwords in plain text
   - Use encryption library like `cryptography`

3. **Rate Limiting**
   - Add rate limiting to prevent abuse
   - Use Flask-Limiter

4. **HTTPS Only**
   - Render provides HTTPS by default
   - Ensure all requests use HTTPS

5. **Monitoring**
   - Set up logging
   - Monitor Instagram API rate limits
   - Track failed login attempts

6. **Backup Strategy**
   - Regular database backups
   - Export session files periodically

## Alternative: Docker Deployment

If you prefer Docker, here's a Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

Deploy on:
- Render (Docker)
- Railway
- Fly.io
- Heroku
- DigitalOcean App Platform

## Troubleshooting

### Issue: "Module not found"
- Ensure all dependencies are in requirements.txt
- Check Python version compatibility

### Issue: "Database locked"
- SQLite doesn't handle concurrent writes well
- Upgrade to PostgreSQL for production

### Issue: "Instagram login fails"
- Check if Instagram account has 2FA enabled (not supported)
- Verify credentials are correct
- Instagram may require additional verification

### Issue: "Socket.IO not working"
- Ensure WebSocket connections are allowed
- Check CORS settings
- Verify async_mode is set correctly
