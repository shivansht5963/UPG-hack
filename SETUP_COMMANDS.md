# CircuTrade AI - Setup Commands

Run these commands in order to create the Django project structure:

## Step 1: Navigate to Project Directory
```bash
cd "C:\Users\Shivansh\OneDrive\Desktop\UPG hack"
```

## Step 2: Create Django Project
```bash
django-admin startproject circutrade_project circutrade
cd circutrade
```

## Step 3: Create Django Apps

Create all 5 apps for separation of concerns:

```bash
# App 1: User management, authentication, roles, karma
python manage.py startapp accounts

# App 2: Waste listings, material catalog, pricing
python manage.py startapp marketplace

# App 3: Blockchain-style tracking and immutable logs
python manage.py startapp provenance

# App 4: Purchase orders, payment tracking
python manage.py startapp transactions

# App 5: Role-based dashboards and UI views
python manage.py startapp dashboard
```

## Step 4: Create Directories

```bash
# Create templates directory in project root
mkdir templates

# Create templates subdirectories for each app
mkdir templates\dashboard
mkdir templates\marketplace
mkdir templates\provenance
mkdir templates\accounts
mkdir templates\transactions

# Create static files directories
mkdir static
mkdir static\css
mkdir static\js
mkdir static\img

# Create media directory for uploaded files
mkdir media
mkdir media\listings
```

## Step 5: Verify Structure

Your project should now look like this:

```
circutrade/
├── circutrade_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── accounts/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── marketplace/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── provenance/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── transactions/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── dashboard/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── templates/
│   ├── dashboard/
│   ├── marketplace/
│   ├── provenance/
│   ├── accounts/
│   └── transactions/
├── static/
│   ├── css/
│   ├── js/
│   └── img/
├── media/
│   └── listings/
└── manage.py
```

## Step 6: Notify Me

Once you've run all these commands, let me know and I'll start implementing all the code!

---

## Quick Copy-Paste Version (All Commands):

```bash
cd "C:\Users\Shivansh\OneDrive\Desktop\UPG hack"
django-admin startproject circutrade_project circutrade
cd circutrade
python manage.py startapp accounts
python manage.py startapp marketplace
python manage.py startapp provenance
python manage.py startapp transactions
python manage.py startapp dashboard
mkdir templates
mkdir templates\dashboard templates\marketplace templates\provenance templates\accounts templates\transactions
mkdir static
mkdir static\css static\js static\img
mkdir media
mkdir media\listings
```
