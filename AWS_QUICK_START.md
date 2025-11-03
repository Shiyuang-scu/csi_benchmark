# AWS Quick Start Checklist

Follow these steps to deploy your Flask application on AWS EC2.

## ☐ Step 1: AWS Setup (30 minutes)

### Create EC2 Instance
- [ ] Go to AWS Console → EC2 → Launch Instance
- [ ] Choose **Ubuntu Server 22.04 LTS**
- [ ] Select instance type: **t3.medium** (recommended) or **t3.small** (budget)
- [ ] Configure storage: **20 GB gp3**
- [ ] Create/select **key pair** (save .pem file!)
- [ ] Configure **Security Group**:
  - SSH (port 22) from My IP
  - HTTP (port 80) from Anywhere
  - HTTPS (port 443) from Anywhere
- [ ] Launch instance
- [ ] Allocate and attach **Elastic IP** (optional but recommended)

**Note your Elastic IP**: _________________

---

## ☐ Step 2: Connect to Server (5 minutes)

```bash
# Set key permissions
chmod 400 your-key.pem

# Connect
ssh -i your-key.pem ubuntu@YOUR_ELASTIC_IP
```

---

## ☐ Step 3: Install Dependencies (10 minutes)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install packages
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git build-essential libatlas-base-dev gfortran

# Clone your repository
cd /home/ubuntu
git clone https://github.com/Shiyuang-scu/csi_benchmark.git
cd csi_benchmark/benchmarkapp
```

---

## ☐ Step 4: Setup Application (10 minutes)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
nano .env
```

Add to `.env`:
```
SECRET_KEY=paste-output-from-command-below
FLASK_ENV=production
DATABASE_URL=sqlite:///app.db
```

Generate SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

```bash
# Initialize database
flask db upgrade

# Create logs directory
mkdir -p logs

# Test (Ctrl+C to stop)
flask run --host=0.0.0.0 --port=5000
```

Visit: `http://YOUR_ELASTIC_IP:5000` to test

---

## ☐ Step 5: Configure Gunicorn Service (10 minutes)

```bash
# Create systemd service
sudo nano /etc/systemd/system/csi-benchmark.service
```

Paste this (replace paths if needed):
```ini
[Unit]
Description=CSI Benchmark Flask Application
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/csi_benchmark/benchmarkapp
Environment="PATH=/home/ubuntu/csi_benchmark/benchmarkapp/venv/bin"
EnvironmentFile=/home/ubuntu/csi_benchmark/benchmarkapp/.env
ExecStart=/home/ubuntu/csi_benchmark/benchmarkapp/venv/bin/gunicorn -c gunicorn.conf.py main:app

[Install]
WantedBy=multi-user.target
```

Update gunicorn config:
```bash
nano /home/ubuntu/csi_benchmark/benchmarkapp/gunicorn.conf.py
```

Change `bind` line to:
```python
bind = "127.0.0.1:8000"
```

Change `workers` to:
```python
workers = 4  # For t3.medium; use 2 for t3.small
```

Start service:
```bash
sudo systemctl start csi-benchmark
sudo systemctl enable csi-benchmark
sudo systemctl status csi-benchmark
```

---

## ☐ Step 6: Configure Nginx (10 minutes)

```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/csi-benchmark
```

Paste this (replace YOUR_ELASTIC_IP with actual IP):
```nginx
server {
    listen 80;
    server_name YOUR_ELASTIC_IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }

    location /static {
        alias /home/ubuntu/csi_benchmark/benchmarkapp/app/static;
        expires 30d;
    }

    client_max_body_size 100M;
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/csi-benchmark /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## ☐ Step 7: Test Website (5 minutes)

Visit: `http://YOUR_ELASTIC_IP`

- [ ] Homepage loads
- [ ] Can register account
- [ ] Can login
- [ ] Can upload files (test with small model first!)

---

## ☐ Step 8: SSL Certificate (Optional, 10 minutes)

### Only if you have a domain name:

1. Point your domain A record to your Elastic IP
2. Wait for DNS propagation (5-30 minutes)
3. Run:

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

Follow prompts and choose to redirect HTTP to HTTPS.

---

## 🎉 You're Done!

Your website is now live at:
- **HTTP**: `http://YOUR_ELASTIC_IP`
- **HTTPS** (if you set up SSL): `https://your-domain.com`

---

## Common Commands

```bash
# Restart application
sudo systemctl restart csi-benchmark

# View logs
sudo journalctl -u csi-benchmark -f

# Check status
sudo systemctl status csi-benchmark

# Update code
cd /home/ubuntu/csi_benchmark
git pull
sudo systemctl restart csi-benchmark
```

---

## Troubleshooting

**Application won't start?**
```bash
sudo journalctl -u csi-benchmark -n 50
```

**Website not loading?**
```bash
sudo systemctl status nginx
sudo tail -f /var/log/nginx/error.log
```

**Out of memory?**
- Upgrade to t3.medium or t3.large
- Or add swap space (see full deployment guide)

---

## Next Steps

- [ ] Set up automatic backups
- [ ] Configure monitoring
- [ ] Restrict SSH to your IP only in Security Group
- [ ] Set up domain name (optional)
- [ ] Configure HTTPS/SSL

---

**Full documentation**: See `AWS_DEPLOYMENT.md` for detailed explanations.
