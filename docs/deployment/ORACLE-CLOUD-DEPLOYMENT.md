# Oracle Cloud + DuckDNS Free Deployment Guide

> Deploy Warehouse Capacity Planner **completely free** using Oracle Cloud's Always Free tier and DuckDNS

**Total Cost: $0.00/month forever**

## What You'll Get

- ✅ **4 CPU cores, 24GB RAM** (ARM-based Ampere processor)
- ✅ **200GB storage**
- ✅ **Free subdomain** (yourdomain.duckdns.org)
- ✅ **SSL/HTTPS** with Let's Encrypt
- ✅ **Free forever** - No time limit, no credit card charges

---

## Table of Contents

1. [Create Oracle Cloud Account](#step-1-create-oracle-cloud-account)
2. [Create VM Instance](#step-2-create-vm-instance)
3. [Configure Firewall](#step-3-configure-firewall)
4. [Get DuckDNS Domain](#step-4-get-duckdns-domain)
5. [Connect to Server](#step-5-connect-to-server)
6. [Deploy Application](#step-6-deploy-application)
7. [Access Your Application](#step-7-access-your-application)
8. [Troubleshooting](#troubleshooting)

---

## Step 1: Create Oracle Cloud Account

### 1.1 Sign Up

1. **Go to Oracle Cloud Free Tier:**
   - Visit: https://www.oracle.com/cloud/free/
   - Click **"Start for free"**

2. **Fill out registration form:**
   - **Country/Territory:** Select your country
   - **Name:** Your full name
   - **Email:** Your email address
   - Click **"Verify my email"**

3. **Verify your email:**
   - Check your inbox for verification email
   - Click the verification link
   - You'll be redirected to continue registration

4. **Complete account details:**
   - **Password:** Create a strong password
   - **Company Name:** Can use your name or make one up
   - **Cloud Account Name:** Choose a unique name (e.g., `mywarehouse123`)
     - This becomes your login identifier
     - Write it down - you'll need it to log in!
   - **Home Region:** Choose closest to you (can't be changed later)
     - US: `us-ashburn-1` or `us-phoenix-1`
     - Europe: `uk-london-1` or `eu-frankfurt-1`

5. **Enter payment information:**
   - **Important:** Credit card required for verification
   - **You will NOT be charged** for Always Free resources
   - Oracle uses it to prevent abuse
   - Only charged if you manually upgrade to paid services

6. **Complete verification:**
   - May require ID verification (depends on region)
   - Follow on-screen instructions
   - Wait for account activation (usually instant)

7. **Welcome to Oracle Cloud!**
   - You'll see the Oracle Cloud Console
   - $300 free credit for 30 days (plus Always Free tier)

---

## Step 2: Create VM Instance

### 2.1 Navigate to Compute Instances

1. **From Oracle Cloud Console:**
   - Click **"Create a VM instance"** on the homepage
   - Or: Menu → Compute → Instances → **"Create Instance"**

### 2.2 Configure Instance

**Name your instance:**
```
warehouse-planner-prod
```

**Placement:**
- **Availability domain:** Leave default (or choose any)
- **Fault domain:** Leave default

**Image and shape:**

1. **Click "Edit" next to "Image and shape"**

2. **Change the shape:**
   - Click **"Change shape"**
   - Select **"Ampere"** (ARM-based)
   - Click **"VM.Standard.A1.Flex"**
   - **OCPU count:** `2` (this is 2 CPU cores)
   - **Memory (GB):** `12`
   - Click **"Select shape"**

   **Important:** This configuration is **Always Free**! You can use up to 4 OCPUs and 24GB RAM total across all instances.

3. **Image:**
   - Should default to "Canonical Ubuntu 22.04"
   - If not, click "Change Image" and select it

**Networking:**

1. **Primary VNIC information:**
   - Leave "Create new virtual cloud network" selected
   - VCN name: `warehouse-vcn` (or leave default)
   - Subnet name: `warehouse-subnet` (or leave default)
   - **Assign a public IPv4 address:** ✅ Checked (very important!)

**Add SSH keys:**

This is how you'll securely connect to your server.

**Option A: Generate SSH keys (Recommended if you don't have one):**

On Windows:
```powershell
# Open PowerShell
ssh-keygen -t rsa -b 4096 -f "$env:USERPROFILE\.ssh\oracle_cloud_key"
# Press Enter for no passphrase (or set one if you prefer)
```

On Mac/Linux:
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/oracle_cloud_key
# Press Enter for no passphrase (or set one if you prefer)
```

**Option B: Use existing SSH key:**
- If you already have an SSH key, you can use it

**Upload the public key:**
1. Select **"Paste public keys"**
2. Open your public key file:
   - Windows: `C:\Users\YourName\.ssh\oracle_cloud_key.pub`
   - Mac/Linux: `~/.ssh/oracle_cloud_key.pub`
3. Copy the entire contents
4. Paste into Oracle Cloud form

**Boot volume:**
- **Boot volume size:** `50 GB` (Always Free tier includes up to 200GB total)
- Leave other options as default

### 2.3 Create the Instance

1. Click **"Create"** at the bottom
2. **Wait for provisioning** (2-5 minutes)
3. Status will change from "Provisioning" → "Running"
4. **Copy your public IP address** - You'll need this!
   - It looks like: `XXX.XXX.XXX.XXX` (e.g., `132.145.67.89`)

**⚠️ Troubleshooting: "Out of capacity"**

If you see "Out of capacity for shape VM.Standard.A1.Flex", try:
1. Different availability domain (change during instance creation)
2. Different region (need to create new account with different home region)
3. Try again later (capacity changes throughout the day)
4. Use AMD shape instead: VM.Standard.E2.1.Micro (1 vCPU, 1GB RAM - less powerful but also always free)

---

## Step 3: Configure Firewall

Oracle Cloud has TWO firewalls you need to configure:

### 3.1 Oracle Cloud Security List (Cloud Firewall)

1. **Navigate to your VCN:**
   - Menu → Networking → Virtual Cloud Networks
   - Click your VCN (e.g., `warehouse-vcn`)

2. **Edit Security List:**
   - Click **"Security Lists"** in the left menu
   - Click **"Default Security List for warehouse-vcn"**

3. **Add Ingress Rules for HTTP and HTTPS:**
   - Click **"Add Ingress Rules"**

   **For HTTP (port 80):**
   - Source CIDR: `0.0.0.0/0`
   - IP Protocol: `TCP`
   - Source Port Range: (leave empty)
   - Destination Port Range: `80`
   - Description: `HTTP`
   - Click **"Add Ingress Rules"**

   **Repeat for HTTPS (port 443):**
   - Click **"Add Ingress Rules"** again
   - Source CIDR: `0.0.0.0/0`
   - IP Protocol: `TCP`
   - Destination Port Range: `443`
   - Description: `HTTPS`
   - Click **"Add Ingress Rules"**

4. **Verify:**
   - You should now see rules for ports 22 (SSH), 80 (HTTP), and 443 (HTTPS)

### 3.2 Ubuntu Firewall (iptables)

We'll configure this after connecting to the server in Step 5.

---

## Step 4: Get DuckDNS Domain

DuckDNS provides **free subdomains** that work perfectly with Let's Encrypt SSL.

### 4.1 Create DuckDNS Account

1. **Go to DuckDNS:**
   - Visit: https://www.duckdns.org/

2. **Sign in:**
   - Click **"sign in with google"** (or GitHub/Twitter/Reddit)
   - Authorize DuckDNS

3. **You're logged in!**
   - You'll see your account token at the top
   - This is used for updating your IP address

### 4.2 Create Subdomain

1. **Enter your desired subdomain:**
   - Type in the box: `mywarehouse` (or any name you want)
   - It will become: `mywarehouse.duckdns.org`
   - Check availability (green checkmark = available)

2. **Set your IP address:**
   - Paste your Oracle Cloud instance public IP
   - Click **"add domain"**

3. **Verify:**
   - Your domain should appear in the "domains" section
   - Current IP should match your Oracle Cloud IP

4. **Test DNS:**
   - Wait 1-2 minutes for DNS propagation
   - Open Command Prompt/Terminal:
     ```bash
     nslookup mywarehouse.duckdns.org
     ```
   - Should return your Oracle Cloud IP

---

## Step 5: Connect to Server

### 5.1 Get Your Connection Details

You need:
- **IP Address:** Your Oracle Cloud instance public IP
- **Username:** `ubuntu` (default for Ubuntu instances)
- **SSH Key:** The private key you generated earlier

### 5.2 Connect via SSH

**On Windows (PowerShell):**
```powershell
ssh -i $env:USERPROFILE\.ssh\oracle_cloud_key ubuntu@YOUR-ORACLE-IP
```

**On Mac/Linux:**
```bash
ssh -i ~/.ssh/oracle_cloud_key ubuntu@YOUR-ORACLE-IP
```

**First time connecting:**
- You'll see: "The authenticity of host... can't be established"
- Type `yes` and press Enter
- You're now connected to your Oracle Cloud server!

**Expected output:**
```
Welcome to Ubuntu 22.04.3 LTS (GNU/Linux 5.15.0-1045-oracle aarch64)
...
ubuntu@warehouse-planner-prod:~$
```

### 5.3 Configure Ubuntu Firewall (iptables)

Oracle Cloud Ubuntu uses iptables instead of UFW:

```bash
# Allow HTTP (port 80)
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT

# Allow HTTPS (port 443)
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT

# Save rules
sudo netfilter-persistent save
```

**If you get "command not found" for netfilter-persistent:**
```bash
sudo apt-get update
sudo apt-get install -y iptables-persistent
# Answer "Yes" to save current rules

# Then save again
sudo netfilter-persistent save
```

### 5.4 Verify Firewall

```bash
sudo iptables -L -n | grep -E "80|443"
```

Should show:
```
ACCEPT     tcp  --  0.0.0.0/0    0.0.0.0/0    state NEW tcp dpt:80
ACCEPT     tcp  --  0.0.0.0/0    0.0.0.0/0    state NEW tcp dpt:443
```

---

## Step 6: Deploy Application

Now for the easy part - automated deployment!

### 6.1 Run Deployment Script

Still connected to your Oracle Cloud server via SSH, run:

```bash
curl -fsSL https://raw.githubusercontent.com/bryanstanleyyy/warehouse-capacity-planner/main/scripts/quick-deploy.sh | bash
```

### 6.2 Answer Prompts

The script will ask you:

**"Continue with deployment? (y/N):"**
```
y
```

**"Enter your domain name (e.g., example.com):"**
```
mywarehouse.duckdns.org
```
(Replace with YOUR DuckDNS domain)

**"Enter your email address:"**
```
your-email@gmail.com
```
(For SSL certificate notifications)

### 6.3 Wait for Deployment

The script will now:
- ✅ Install Docker and dependencies (5-10 minutes)
- ✅ Configure firewall and security
- ✅ Clone repository
- ✅ Generate secure secrets
- ✅ Obtain SSL certificate (1-2 minutes)
- ✅ Build Docker images (10-15 minutes)
- ✅ Start all services
- ✅ Initialize database
- ✅ Run health checks

**Total time: 20-30 minutes**

**What you'll see:**
```
==============================================
Warehouse Capacity Planner
Automated Production Deployment
==============================================

→ Installing Docker...
✓ Docker installed
✓ Server setup completed!

→ Cloning repository...
✓ Repository ready

→ Generating secure configuration...
✓ Environment configured with secure secrets

→ Obtaining SSL certificates from Let's Encrypt...
✓ SSL certificates obtained and configured

→ Building Docker images (this may take 5-10 minutes)...
✓ Docker images built

→ Starting services...
✓ All containers are running (4/4)
✓ Database is ready
✓ Database migrations completed

==============================================
✓ DEPLOYMENT COMPLETED!
==============================================

🎉 Your Warehouse Capacity Planner is now live!

Access your application:
  🌐 https://mywarehouse.duckdns.org
```

---

## Step 7: Access Your Application

### 7.1 Open in Browser

1. **Visit your domain:**
   ```
   https://mywarehouse.duckdns.org
   ```
   (Replace with your domain)

2. **You should see:**
   - ✅ Valid SSL certificate (green lock icon)
   - ✅ Warehouse Capacity Planner homepage
   - ✅ No security warnings

### 7.2 Test the Application

1. **Create a warehouse:**
   - Click "Warehouses" in navigation
   - Click "Create Warehouse"
   - Fill in details, add zones
   - Save

2. **Upload inventory:**
   - Click "Inventory Upload"
   - Upload an Excel file
   - Verify parsing works

3. **Run allocation:**
   - Go to "Allocation Planner"
   - Select warehouse and inventory
   - Run allocation
   - View results

---

## Troubleshooting

### Issue 1: Can't Connect via SSH

**Symptom:** Connection timeout or "Permission denied"

**Solutions:**

1. **Check IP address:**
   ```bash
   # Verify you're using the correct IP
   ping YOUR-ORACLE-IP
   ```

2. **Check SSH key permissions:**
   ```powershell
   # Windows (PowerShell)
   icacls $env:USERPROFILE\.ssh\oracle_cloud_key
   # Should show only your user has access

   # Mac/Linux
   chmod 400 ~/.ssh/oracle_cloud_key
   ```

3. **Try password authentication (if enabled):**
   ```bash
   ssh ubuntu@YOUR-ORACLE-IP
   # Oracle Cloud instances don't have password by default
   ```

4. **Check Oracle Cloud Console:**
   - Instance state should be "Running" (green)
   - Public IP should be assigned

### Issue 2: Ports 80/443 Not Accessible

**Symptom:** Can SSH in, but can't access website

**Solutions:**

1. **Check Oracle Cloud Security List:**
   - VCN → Security Lists
   - Verify ingress rules for ports 80 and 443 exist
   - Source should be `0.0.0.0/0`

2. **Check Ubuntu firewall:**
   ```bash
   sudo iptables -L -n | grep -E "80|443"
   ```
   Should show ACCEPT rules

3. **Re-add firewall rules:**
   ```bash
   sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
   sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
   sudo netfilter-persistent save
   ```

### Issue 3: SSL Certificate Failed

**Symptom:** Certbot fails to obtain certificate

**Solutions:**

1. **Check DNS:**
   ```bash
   nslookup mywarehouse.duckdns.org
   ```
   Should return your Oracle Cloud IP

2. **Check port 80 is open:**
   ```bash
   sudo lsof -i :80
   # Should show nothing (port available)
   ```

3. **Try manual certificate request:**
   ```bash
   sudo certbot certonly --standalone \
     -d mywarehouse.duckdns.org \
     --email your-email@gmail.com \
     --agree-tos
   ```

### Issue 4: Docker Build Fails

**Symptom:** "Out of memory" or build errors

**Solutions:**

1. **Check available memory:**
   ```bash
   free -h
   ```
   Should show several GB available

2. **If using E2.1.Micro (1GB RAM):**
   - This instance type has limited RAM
   - Upgrade to A1.Flex or add swap:
   ```bash
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   ```

3. **Build one service at a time:**
   ```bash
   cd ~/warehouse-capacity-planner
   docker compose -f docker-compose.prod.yml build backend
   docker compose -f docker-compose.prod.yml build frontend
   docker compose -f docker-compose.prod.yml up -d
   ```

### Issue 5: Instance Stopped/Terminated

**Symptom:** Instance shows "Terminated" status

**Oracle Cloud may reclaim Always Free instances if:**
- Not used for 90+ days
- Suspected abuse
- Policy violations

**Prevention:**
1. Use the instance regularly
2. Don't mine cryptocurrency
3. Don't run network scanners
4. Keep the VM actively serving your application

**Recovery:**
- Create a new instance following this guide
- Restore from database backup if you had automated backups configured

### Issue 6: Port 80/443 Not Accessible (SSL Certificate Fails)

**Symptom:** Let's Encrypt cannot connect to port 80, or browser shows ERR_CONNECTION_TIMED_OUT

**This is the MOST COMMON Oracle Cloud issue** - Oracle has multiple firewall layers

**Root Cause:** Oracle Cloud has THREE firewall layers:
1. ✅ Security Lists (usually configured correctly)
2. ❌ Network Security Groups (NSG) - often blocks port 80/443
3. ✅ iptables (configured by scripts)

**Solution - Check Network Security Groups:**

#### Step 1: Check if NSG is attached

1. Oracle Cloud Console → **Compute** → **Instances** → Click your instance
2. Scroll to **Resources** → **Attached VNICs**
3. Click on **primaryvnic** (or your VNIC name)
4. Under **Resources** → Click **Network Security Groups**

**Do you see any NSG listed?**

#### Step 2A: If NSG exists - Add port 80/443 rules

1. Click the **NSG name**
2. Click **Add Rule**
3. Add HTTP rule:
   - **Direction**: Ingress
   - **Source Type**: CIDR
   - **Source CIDR**: `0.0.0.0/0`
   - **IP Protocol**: TCP
   - **Destination Port Range**: `80`
   - **Description**: `HTTP`
4. Click **Add Security Rule**
5. Repeat for HTTPS (port `443`)

#### Step 2B: If NO NSG - Check VCN Route Table

1. **Networking** → **Virtual Cloud Networks** → Click your VCN
2. **Route Tables** → **Default Route Table**
3. Verify route exists:
   - **Destination CIDR**: `0.0.0.0/0`
   - **Target Type**: Internet Gateway

If missing:
1. Click **Add Route Rules**
2. Configure:
   - **Target Type**: Internet Gateway
   - **Destination CIDR**: `0.0.0.0/0`
3. Click **Add Route Rules**

#### Step 3: Test port 80

From your local computer:
```bash
curl -v http://YOUR-IP-ADDRESS
# Should connect (even if shows error page)
```

From the server:
```bash
# Start test server
python3 -m http.server 80

# In another terminal/browser, test:
curl http://localhost
```

**If still not working**, check if you selected "Use network security groups to control traffic" when creating the instance. If yes, you MUST add rules to that NSG.

---

## Post-Deployment

### Set Up Automated Backups

```bash
# Configure daily backups at 2 AM
crontab -e

# Add this line:
0 2 * * * cd /home/ubuntu/warehouse-capacity-planner && ./scripts/backup-database.sh >> logs/backup.log 2>&1
```

### Set Up Monitoring

**Free options:**

1. **UptimeRobot** (https://uptimerobot.com)
   - Monitor: `https://mywarehouse.duckdns.org/health`
   - Get email alerts if site goes down

2. **Sentry** (https://sentry.io)
   - Free tier: 5K errors/month
   - Track application errors

### Keep Your System Updated

```bash
# Update packages monthly
sudo apt-get update
sudo apt-get upgrade -y

# Update application
cd ~/warehouse-capacity-planner
git pull origin master
bash scripts/deploy.sh
```

---

## Summary

**What you deployed:**
- ✅ Oracle Cloud Always Free VM (4 cores, 24GB RAM)
- ✅ DuckDNS free subdomain
- ✅ Let's Encrypt SSL certificate
- ✅ Warehouse Capacity Planner application
- ✅ PostgreSQL database
- ✅ nginx reverse proxy
- ✅ Automated backups (when configured)

**Total monthly cost: $0.00**

**Your application is at:**
- 🌐 https://mywarehouse.duckdns.org

**Useful commands:**
```bash
# View logs
docker compose -f docker-compose.prod.yml logs -f

# Restart services
docker compose -f docker-compose.prod.yml restart

# Check health
bash scripts/health-check.sh

# Backup database
bash scripts/backup-database.sh
```

---

## Additional Resources

- Oracle Cloud Documentation: https://docs.oracle.com/en-us/iaas/
- DuckDNS Documentation: https://www.duckdns.org/spec.jsp
- Let's Encrypt Documentation: https://letsencrypt.org/docs/
- Main Deployment Guide: [DEPLOYMENT.md](../../DEPLOYMENT.md)

---

**Congratulations! Your warehouse capacity planner is now running in production, completely free! 🎉**
