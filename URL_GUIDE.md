# CircuTrade AI - Complete URL Guide

## 🎯 All Available URLs

### 🔐 Authentication & User Management
Base URL: `http://127.0.0.1:8000/accounts/`

| URL | Description | Access |
|-----|-------------|--------|
| `/accounts/register/` | User registration with role selection | Public |
| `/accounts/login/` | Login page | Public |
| `/accounts/logout/` | Logout (GET request) | Authenticated |
| `/accounts/profile/` | Edit your profile | Authenticated |
| `/accounts/profile/<username>/` | View public profile | Public |
| `/accounts/api/check-username/?username=test` | AJAX: Check username availability | Public |
| `/accounts/api/check-email/?email=test@example.com` | AJAX: Check email availability | Public |

### 🛒 Marketplace
Base URL: `http://127.0.0.1:8000/marketplace/`

| URL | Description | Access | Method |
|-----|-------------|--------|--------|
| `/marketplace/feed/` | Browse all waste listings with filters | Public | GET |
| `/marketplace/create/` | Create new waste listing | Generator Only | GET/POST |
| `/marketplace/listing/<id>/` | View listing details | Public | GET |
| `/marketplace/listing/<id>/delete/` | Delete/cancel listing | Owner Only | POST |
| `/marketplace/api/calculate-price/` | AJAX: Real-time price calculator | Public | POST |
| `/marketplace/api/verify/` | AJAX: Mock OpenCV verification | Public | POST |

### 🔗 Provenance (Blockchain Tracking)
Base URL: `http://127.0.0.1:8000/provenance/`

| URL | Description | Status |
|-----|-------------|--------|
| *(Coming in Phase 4)* | Blockchain tracking | Not Yet Implemented |

### 💰 Transactions
Base URL: `http://127.0.0.1:8000/transactions/`

| URL | Description | Status |
|-----|-------------|--------|
| *(Coming in Phase 5)* | Purchase orders, payments | Not Yet Implemented |

### 📊 Dashboard
Base URL: `http://127.0.0.1:8000/`

| URL | Description | Status |
|-----|-------------|--------|
| `/` | Landing page | Not Yet Implemented (Phase 6) |
| *(Role-based dashboards)* | Generator/Buyer/Worker dashboards | Not Yet Implemented (Phase 6) |

### ⚙️ Admin Panel
Base URL: `http://127.0.0.1:8000/admin/`

| URL | Description | Access |
|-----|-------------|--------|
| `/admin/` | Django admin dashboard | Superuser |
| `/admin/accounts/customuser/` | Manage users | Superuser |
| `/admin/marketplace/material/` | Manage materials | Superuser |
| `/admin/marketplace/wastelisting/` | Manage waste listings | Superuser |

---

## 🚀 Quick Start Testing Guide

### Step 1: Create Test Users (Admin Panel)

1. **Login to Admin**: `http://127.0.0.1:8000/admin/`
   - Username: `shivansh@gmail.com`
   - Password: (your password)

2. **Add Test Materials**:
   - Go to: `http://127.0.0.1:8000/admin/marketplace/material/add/`
   - Example materials:
     ```
     Name: PET Plastic
     Base Price: 25.00
     Grade A Multiplier: 1.5
     Grade B Multiplier: 1.0
     Grade C Multiplier: 0.7
     CO2 Saved Per Kg: 2.5
     ```

### Step 2: Register Generator User

1. Go to: `http://127.0.0.1:8000/accounts/register/`
2. Fill form:
   - Role: **Waste Generator**
   - Fill all required fields
3. Auto-login after registration

### Step 3: Create Waste Listing

1. Go to: `http://127.0.0.1:8000/marketplace/create/`
2. Upload image → **AI will auto-verify** (trust score 30-100%)
3. Select material, weight, grade
4. See real-time price calculation
5. Submit → Redirected to dashboard (not implemented yet, will show error)

### Step 4: View Marketplace

1. Go to: `http://127.0.0.1:8000/marketplace/feed/`
2. Browse listings with filters
3. Click any listing to see details

### Step 5: Register Buyer User

1. Logout current user
2. Go to: `http://127.0.0.1:8000/accounts/register/`
3. Role: **Buyer/Manufacturer**
4. Browse marketplace and view listings

---

## 🔥 Testing the Mock OpenCV API

### AJAX Test (using browser console)

```javascript
// Test price calculator
fetch('/marketplace/api/calculate-price/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    },
    body: JSON.stringify({
        material_id: 1,  // Material ID
        grade: 'A',
        weight: 100
    })
})
.then(r => r.json())
.then(data => console.log('Price:', data));
```

### Mock OpenCV Verification
- Upload any image when creating listing
- System generates deterministic trust score (30-100%) based on image hash
- Auto-suggests grade (A/B/C) based on trust score:
  - 80-100% → Grade A
  - 60-79% → Grade B
  - 30-59% → Grade C

---

## 📋 Current Features Checklist

### ✅ Phase 1: Setup (COMPLETE)
- [x] Django 5.1+ project
- [x] Virtual environment
- [x] Base template with Bootstrap 5
- [x] Custom CSS with sustainability theme
- [x] Main.js with animations

### ✅ Phase 2: Accounts (COMPLETE)
- [x] CustomUser with 3 roles (Generator/Buyer/Worker)
- [x] Karma system (0-1000)
- [x] Registration & Login
- [x] Profile management
- [x] Admin panel with badges

### ✅ Phase 3: Marketplace (COMPLETE)
- [x] Material model with pricing engine
- [x] WasteListing with images, trust score
- [x] Mock OpenCV verification (deterministic)
- [x] Real-time price calculator
- [x] Marketplace feed with filters
- [x] Create listing form
- [x] Listing detail page
- [x] Admin panel with colored badges

### ⏳ Phase 4: Provenance (NOT STARTED)
- [ ] ProvenanceLog model
- [ ] SHA-256 hash generation
- [ ] Blockchain-style timeline

### ⏳ Phase 5: Transactions (NOT STARTED)
- [ ] Transaction model
- [ ] Purchase flow
- [ ] Payment tracking

### ⏳ Phase 6: Dashboards (NOT STARTED)
- [ ] Landing page
- [ ] Generator dashboard
- [ ] Buyer dashboard
- [ ] Worker dashboard

---

## 🐛 Known Limitations

1. **No Dashboards Yet**: After creating listing, redirect will fail (Phase 6)
   - Temporary fix: Dashboards redirect to marketplace with info message
2. **No Real OpenCV**: Uses hash-based mock verification
3. **No Transactions**: Can't actually purchase yet (Phase 5)
   - "My Transactions" link in navbar is commented out
4. **No Provenance**: Blockchain tracking coming in Phase 4
   - "Provenance Vault" link in navbar is commented out (Buyer menu)

---

## 💡 Next Steps

1. Add 2-3 materials in admin panel
2. Register as Generator and create listings
3. Register as Buyer and browse marketplace
4. Proceed with Phase 4 (Provenance) or Phase 6 (Dashboards) based on priority
