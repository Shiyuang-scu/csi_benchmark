# AWS EC2 Deployment Guide

Complete guide for deploying the CSI Benchmark Flask application on AWS EC2.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Create EC2 Instance](#create-ec2-instance)
3. [Initial Server Setup](#initial-server-setup)
4. [Install Dependencies](#install-dependencies)
5. [Deploy Application](#deploy-application)
6. [Configure Gunicorn](#configure-gunicorn)
7. [Configure Nginx](#configure-nginx)
8. [SSL Certificate Setup](#ssl-certificate-setup)
9. [Monitoring & Logs](#monitoring--logs)

---

## Prerequisites

- AWS Account
- Domain name (optional, but recommended for SSL)
- SSH key pair for EC2 access
- Basic Linux/terminal knowledge

---

## Create EC2 Instance

### 1. Launch EC2 Instance

**AWS Console → EC2 → Launch Instance**

**Recommended Settings:**
- **AMI**: Ubuntu Server 22.04 LTS (64-bit ARM or x86)
- **Instance Type**:
  - Minimum: **t3.small** (2 GB RAM, 2 vCPUs) - ~$15/month
  - Recommended: **t3.medium** (4 GB RAM, 2 vCPUs) - ~$30/month
  - For heavy processing: **t3.large** (8 GB RAM, 2 vCPUs) - ~$60/month
- **Storage**: 20 GB gp3 (General Purpose SSD)
- **Key Pair**: Create or select existing key pair (save .pem file securely)

### 2. Configure Security Group

Create security group with these inbound rules:

| Type  | Protocol | Port Range | Source    | Description        |
|-------|----------|------------|-----------|-------------------|
| SSH   | TCP      | 22         | My IP     | SSH access        |
| HTTP  | TCP      | 80         | 0.0.0.0/0 | Web traffic       |
| HTTPS | TCP      | 443        | 0.0.0.0/0 | Secure web traffic|

**Important**: After initial setup, change SSH source from "My IP" to your specific IP address for security.

### 3. Allocate Elastic IP (Recommended)

- AWS Console → EC2 → Elastic IPs → Allocate Elastic IP
- Associate with your EC2 instance
- This gives you a static IP that won't change when you restart the instance

---

## Initial Server Setup

### 1. Connect to EC2 Instance

```bash
# Set permissions for your key file
chmod 400 your-key.pem

# Connect via SSH
ssh -i your-key.pem ubuntu@YOUR_ELASTIC_IP
```

### 2. Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### 3. Create Application User (Optional but Recommended)

```bash
sudo adduser flaskapp
sudo usermod -aG sudo flaskapp
```

---

## Install Dependencies

### 1. Install Python and System Dependencies

```bash
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y nginx certbot python3-certbot-nginx
sudo apt install -y git curl
```

### 2. Install Additional Libraries (for NumPy/SciPy)

```bash
sudo apt install -y build-essential libatlas-base-dev gfortran
```

---

## Deploy Application

### 1. Clone Repository

```bash
cd /home/ubuntu
git clone https://github.com/Shiyuang-scu/csi_benchmark.git
cd csi_benchmark
```

### 2. Create Virtual Environment

```bash
cd benchmarkapp
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Set Environment Variables

Create a `.env` file:

```bash
nano .env
```

Add these variables:

```bash
SECRET_KEY=your-very-long-random-secret-key-here
FLASK_ENV=production
DATABASE_URL=sqlite:///app.db
```

Generate a secure SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Initialize Database

```bash
flask db upgrade
```

### 6. Test Application

```bash
flask run --host=0.0.0.0 --port=5000
```

Open browser: `http://YOUR_ELASTIC_IP:5000`

If it works, press `Ctrl+C` to stop Flask dev server.

---

## Configure Gunicorn

### 1. Create Systemd Service File

```bash
sudo nano /etc/systemd/system/csi-benchmark.service
```

Add this content:

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

### 2. Update Gunicorn Config for Production

Edit `gunicorn.conf.py`:

```bash
nano /home/ubuntu/csi_benchmark/benchmarkapp/gunicorn.conf.py
```

Update to:

```python
# Gunicorn configuration for AWS EC2 production

# Bind to localhost (Nginx will proxy to this)
bind = "127.0.0.1:8000"

# Workers: 2-4 x CPU cores (adjust based on instance size)
workers = 4

# Worker class
worker_class = "sync"

# Timeout for long-running 3D mesh computations
timeout = 300

# Keep-alive
keepalive = 2

# Logging
accesslog = "/home/ubuntu/csi_benchmark/benchmarkapp/logs/access.log"
errorlog = "/home/ubuntu/csi_benchmark/benchmarkapp/logs/error.log"
loglevel = "info"

# Memory management
max_requests = 1000
max_requests_jitter = 50

# Daemon mode
daemon = False
```

### 3. Create Logs Directory

```bash
mkdir -p /home/ubuntu/csi_benchmark/benchmarkapp/logs
```

### 4. Start and Enable Service

```bash
sudo systemctl start csi-benchmark
sudo systemctl enable csi-benchmark
sudo systemctl status csi-benchmark
```

---

## Configure Nginx

### 1. Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/csi-benchmark
```

Add this content (replace `your-domain.com` with your actual domain):

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # If you don't have a domain, use:
    # server_name YOUR_ELASTIC_IP;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Increase timeout for long-running computations
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }

    # Serve static files directly
    location /static {
        alias /home/ubuntu/csi_benchmark/benchmarkapp/app/static;
        expires 30d;
    }

    # Increase max upload size for 3D model files
    client_max_body_size 100M;
}
```

### 2. Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/csi-benchmark /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3. Test Website

Open browser: `http://YOUR_ELASTIC_IP` or `http://your-domain.com`

---

## SSL Certificate Setup

### Option A: With Domain Name (Recommended)

**1. Point your domain to Elastic IP**
- Go to your domain registrar
- Add an A record pointing to your Elastic IP

**2. Get Free SSL Certificate with Certbot**

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

Follow prompts:
- Enter email address
- Agree to terms
- Choose to redirect HTTP to HTTPS (recommended)

**3. Auto-renewal**

Certbot automatically sets up renewal. Test it:

```bash
sudo certbot renew --dry-run
```

### Option B: Without Domain (Self-Signed - Development Only)

```bash
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/nginx-selfsigned.key \
  -out /etc/ssl/certs/nginx-selfsigned.crt
```

Update Nginx config to include SSL.

---

## Monitoring & Logs

### Check Application Status

```bash
sudo systemctl status csi-benchmark
```

### View Application Logs

```bash
# Gunicorn logs
tail -f /home/ubuntu/csi_benchmark/benchmarkapp/logs/error.log
tail -f /home/ubuntu/csi_benchmark/benchmarkapp/logs/access.log

# Flask logs
tail -f /home/ubuntu/csi_benchmark/benchmarkapp/logs/benchmarkapp.log

# Systemd logs
sudo journalctl -u csi-benchmark -f
```

### Restart Application

```bash
sudo systemctl restart csi-benchmark
```

### Update Application

```bash
cd /home/ubuntu/csi_benchmark
git pull
cd benchmarkapp
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
sudo systemctl restart csi-benchmark
```

---

## Troubleshooting

### Application Won't Start

```bash
# Check service status
sudo systemctl status csi-benchmark

# Check logs
sudo journalctl -u csi-benchmark -n 50

# Test gunicorn manually
cd /home/ubuntu/csi_benchmark/benchmarkapp
source venv/bin/activate
gunicorn -c gunicorn.conf.py main:app
```

### Nginx Issues

```bash
# Test Nginx config
sudo nginx -t

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log
```

### Out of Memory

- Upgrade to larger instance type (t3.medium or t3.large)
- Reduce number of Gunicorn workers
- Add swap space:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## Security Best Practices

1. **Use SSH Keys Only**: Disable password authentication
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Set: PasswordAuthentication no
   sudo systemctl restart sshd
   ```

2. **Configure Firewall**: Use AWS Security Groups (already covered above)

3. **Keep System Updated**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

4. **Regular Backups**:
   - Database: `cp app.db app.db.backup`
   - Create AMI snapshots in AWS Console

5. **Monitor Resource Usage**:
   ```bash
   htop
   df -h
   free -h
   ```

---

## Estimated AWS Costs

| Instance Type | RAM | vCPUs | Monthly Cost | Best For |
|---------------|-----|-------|--------------|----------|
| t3.small      | 2GB | 2     | ~$15         | Testing, small models |
| t3.medium     | 4GB | 2     | ~$30         | Production, medium models |
| t3.large      | 8GB | 2     | ~$60         | Heavy processing, all models |

**Additional costs:**
- Elastic IP: Free while attached to running instance
- Data transfer: First 1GB free, then $0.09/GB
- Storage (20GB): ~$2/month

**Total estimated**: $17-$62/month depending on instance type

---

## Quick Reference Commands

```bash
# Restart application
sudo systemctl restart csi-benchmark

# View logs
sudo journalctl -u csi-benchmark -f

# Update code
cd /home/ubuntu/csi_benchmark && git pull && sudo systemctl restart csi-benchmark

# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
ps aux | grep gunicorn
```

---

## Support

For issues or questions:
- Check logs: `/home/ubuntu/csi_benchmark/benchmarkapp/logs/`
- AWS EC2 Documentation: https://docs.aws.amazon.com/ec2/
- Flask Documentation: https://flask.palletsprojects.com/
- Nginx Documentation: https://nginx.org/en/docs/

---

**Last Updated**: November 2025
