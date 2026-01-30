# Virtual Environment Setup Commands for CircuTrade AI

## Step 1: Create Virtual Environment
```powershell
python -m venv venv
```

## Step 2: Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

**If you get an execution policy error**, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try activating again.

## Step 3: Upgrade pip (inside venv)
```powershell
python -m pip install --upgrade pip
```

## Step 4: Install Requirements
```powershell
pip install -r requirements.txt
```

## Step 5: Run Migrations (Create Database)
```powershell
python manage.py makemigrations
python manage.py migrate
```

## Step 6: Run Development Server
```powershell
python manage.py runserver
```

---

## Quick Copy-Paste Version (All Commands):

```powershell
# Create and activate venv
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Setup database (we'll do this after creating models)
# python manage.py makemigrations
# python manage.py migrate

# Run server
python manage.py runserver
```

---

## To Deactivate Virtual Environment Later:
```powershell
deactivate
```

## To Activate Again in Future Sessions:
```powershell
cd "C:\Users\Shivansh\OneDrive\Desktop\UPG hack"
.\venv\Scripts\Activate.ps1
```

---

**Note:** Once activated, you'll see `(venv)` prefix in your terminal prompt.
