# BharatiyaAI Mentor

**India's first three-level adaptive AI mentor**  
Built by a student, for every student.

> AI for Bharat Hackathon · Student Track  
> Team Lead: Nitisha Mandar Naigaonkar

---

## Deployment: AWS Asia Pacific (Mumbai) — ap-south-1

### Step 1 — AWS Console: Enable Bedrock Models

1. Go to **AWS Console** → search **Amazon Bedrock**
2. In the left sidebar click **Model access**
3. Click **Modify model access** (top right)
4. Enable both:
   - ✅ `Amazon Nova Lite`
   - ✅ `Anthropic Claude 3.5 Sonnet v2`
5. Click **Save changes** — takes ~2 minutes to activate
6. Make sure region (top-right of console) is **Asia Pacific (Mumbai) ap-south-1**

---

### Step 2 — AWS Console: Create DynamoDB Tables

1. Go to **AWS Console** → search **DynamoDB** → **Create table**
2. Create 3 tables (one at a time):

| Table Name      | Partition Key          | Sort Key |
|----------------|------------------------|----------|
| `baim_users`   | `username` (String)    | none     |
| `baim_cache`   | `prompt_hash` (String) | none     |
| `baim_sessions`| `session_id` (String)  | none     |

For each: leave all other settings as default → **Create table**

---

### Step 3 — AWS Console: Create S3 Bucket

1. Go to **AWS Console** → search **S3** → **Create bucket**
2. Bucket name: `baim-uploads`
3. Region: **Asia Pacific (Mumbai) ap-south-1**
4. Uncheck **Block all public access** → confirm
5. Click **Create bucket**

---

### Step 4 — AWS Console: Create IAM User (get credentials)

1. Go to **AWS Console** → search **IAM** → **Users** → **Create user**
2. Username: `baim-app`
3. Click **Attach policies directly**, add these 4 policies:
   - `AmazonDynamoDBFullAccess`
   - `AmazonS3FullAccess`
   - `AmazonBedrockFullAccess`
   - `AmazonBedrockRuntime` (if shown separately)
4. Create user → click the user → **Security credentials** tab
5. Click **Create access key** → choose **Application running on AWS** → **Create**
6. **COPY both keys NOW** — you won't see the secret again

---

### Step 5 — EC2: Connect to Your Instance

Open your terminal (or use EC2 Instance Connect in browser):

```bash
# If using .pem file
ssh -i your-key.pem ec2-user@YOUR_EC2_PUBLIC_IP

# Or use EC2 Instance Connect:
# AWS Console → EC2 → Instances → select yours → Connect → EC2 Instance Connect
```

---

### Step 6 — EC2: Install Dependencies

```bash
# Update system
sudo yum update -y

# Install Python 3.11 and pip
sudo yum install python3.11 python3.11-pip git -y

# Verify
python3.11 --version
```

---

### Step 7 — EC2: Upload and Set Up the App

**Option A — Upload the zip directly (easiest):**
```bash
# On your LOCAL machine, upload the zip to EC2:
scp -i your-key.pem bharatiyaai-mentor-v5.zip ec2-user@YOUR_EC2_IP:~/

# Back on EC2:
cd ~
unzip bharatiyaai-mentor-v5.zip
mv baim_v5 baim
cd baim
```

**Option B — Use the AWS Console file manager:**
Upload zip to S3, then on EC2:
```bash
aws s3 cp s3://baim-uploads/bharatiyaai-mentor-v5.zip ~/
unzip bharatiyaai-mentor-v5.zip
mv baim_v5 baim && cd baim
```

---

### Step 8 — EC2: Install Python Packages

```bash
cd ~/baim
pip3.11 install -r requirements.txt
```

This takes ~3 minutes. If you get a pip error try:
```bash
python3.11 -m pip install -r requirements.txt
```

---

### Step 9 — EC2: Add Your AWS Credentials

```bash
cd ~/baim
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
nano .streamlit/secrets.toml
```

Replace the values with your real credentials:
```toml
AWS_ACCESS_KEY_ID     = "AKIA..."          # from Step 4
AWS_SECRET_ACCESS_KEY = "your-secret..."   # from Step 4
AWS_REGION            = "ap-south-1"
```

Save: `Ctrl+X` → `Y` → `Enter`

---

### Step 10 — EC2: Open Port 8501

1. AWS Console → **EC2** → **Security Groups**
2. Find the security group attached to your instance
3. Click **Inbound rules** → **Edit inbound rules** → **Add rule**
4. Type: `Custom TCP` | Port: `8501` | Source: `0.0.0.0/0`
5. Save rules

---

### Step 11 — EC2: Run the App (Keep Alive)

```bash
cd ~/baim

# Install tmux (keeps app running after you close terminal)
sudo yum install tmux -y

# Start a persistent session
tmux new -s baim

# Inside tmux, run the app
streamlit run app.py --server.port 8501 --server.headless true --server.address 0.0.0.0

# Detach from tmux (app keeps running): Ctrl+B then D
```

Your app is now live at: `http://YOUR_EC2_PUBLIC_IP:8501`

---

### Step 12 — Verify Everything Works

Open `http://YOUR_EC2_PUBLIC_IP:8501` in browser and test:
- [ ] Login page loads (no raw HTML visible)
- [ ] Guest mode works → goes to onboarding
- [ ] Onboarding step rail shows correctly
- [ ] Generate curriculum calls Bedrock (needs IAM + Bedrock enabled)
- [ ] Dashboard loads

---

### Useful Commands

```bash
# Reconnect to running app after SSH disconnect
tmux attach -t baim

# Stop the app
tmux attach -t baim → Ctrl+C

# Check if app is running
ps aux | grep streamlit

# View app logs
tmux attach -t baim

# Restart app
tmux attach -t baim
# Ctrl+C to stop
streamlit run app.py --server.port 8501 --server.headless true --server.address 0.0.0.0
```

---

## Architecture

```
Student Browser
      ↓
EC2 t2.micro — ap-south-1 (Streamlit :8501)
      ↓
      ├── Bedrock Nova Lite        → Level 1 (simple tasks, cached)
      ├── Bedrock Claude 3.5 Sonnet → Viva, Curriculum, PYQ
      ├── DynamoDB ap-south-1      → baim_users, baim_cache, baim_sessions
      └── S3 ap-south-1            → baim-uploads (PDFs, PYQ papers)
```

## Tech Stack

| Layer | Service |
|-------|---------|
| Frontend | Streamlit on EC2 t2.micro |
| AI Simple | Amazon Bedrock Nova Lite |
| AI Complex | Amazon Bedrock Claude 3.5 Sonnet v2 |
| Database | DynamoDB (3 tables) |
| Storage | S3 bucket baim-uploads |
| Region | ap-south-1 Mumbai |

## Judging Criteria

| Criteria | Implementation |
|----------|---------------|
| Implementation 50% | Auth → Onboarding → 3 Levels → Viva → Profile |
| Technical Depth 20% | Bedrock + DynamoDB cache + S3 + adaptive engine |
| Cost Efficiency 10% | DynamoDB response caching, Nova Lite for simple tasks |
| Impact 10% | Viva examiner for Indian students |
| Business Viability 10% | University-specific, scalable architecture |
