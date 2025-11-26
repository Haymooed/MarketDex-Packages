# 🎄 Advent Calendar Package (MarketDex / BallsDex Custom Package)

A fully-customizable **December 1st → 25th Advent Calendar** for BallsDex-based bots (such as MarketDex).  
This package provides:

- A **Discord extension** (`/advent claim`)
- A **Django admin panel app** to configure rewards per day
- Database models for safe tracking of claims
- Support for random specials, specific balls, or specific ball+special combos

Designed to integrate cleanly with BallsDex without touching `bd_models`.

---

## ✨ Features

### ✔ Daily rewards (Dec 1–25)  
Each day can be configured individually using the admin panel.

### ✔ Reward Types  
For each day, you can choose:

1. **Random Special**  
   - Picks a random `Special` + a random enabled `Ball`

2. **Selected Ball**  
   - Always gives one specific Ball

3. **Selected Ball + Special**  
   - Gives a chosen Ball with a chosen Special applied

### ✔ User Claim Tracking  
- Each user can only claim **once per day**  
- Attempts to re-claim will show an error  
- Blacklisted users are automatically blocked

### ✔ Fully Admin-Controlled  
All 25 days are editable from the web admin panel — no code edits needed.

### ✔ Clean Discord Slash Command  
```
/advent claim
```

---

# 📦 Installation Guide

Follow these steps to integrate the Advent Calendar package into your BallsDex bot.

---

## 1️⃣ Add the package to your bot

Place this folder inside:

```
ballsdex/
 └── packages/
      └── adventcalendar/
           ├── __init__.py
           ├── cog.py
           └── models.py
```

---

## 2️⃣ Add the Django admin app

Place this inside your admin panel:

```
admin_panel/
 └── adventcalendars/
        ├── __init__.py
        ├── admin.py
        ├── apps.py
        ├── models.py
        └── migrations/
```

---

## 3️⃣ Register the Django app

Open:

```
admin_panel/admin_panel/settings/local.py
```

Add:

```python
"adventcalendars",
```

to `INSTALLED_APPS`.

---

## 4️⃣ Register Tortoise ORM models

Open your bot’s main file (`__main__.py` or wherever Tortoise is configured).

Find the model list:

```python
"models": [
    "ballsdex.core.models",
    "ballsdex.packages.crafting.models",
]
```

Add:

```python
"ballsdex.packages.adventcalendar.models",
```

---

## 5️⃣ Enable the package in config.yml

Open your bot’s `config.yml`, and in the `packages:` list, add:

```yaml
  - ballsdex.packages.adventcalendar
```

---

## 6️⃣ Run database migrations

In the admin panel container:

```bash
cd admin_panel
docker compose exec admin-panel python3 manage.py makemigrations adventcalendars
docker compose exec admin-panel python3 manage.py migrate adventcalendars
```

---

## 7️⃣ Restart everything

```bash
docker compose down
docker compose up -d
```

---

## 8️⃣ Configure Days 1–25

In the admin panel (`/admin`):

You will now see:

- **Advent Day Configs**
- **Advent Claims**

Create entries for **Day 1 → Day 25**, assigning reward types and settings.

---

# 🎁 Usage

Users can claim their daily reward with:

```
/advent claim
```

The bot will:

- Detect today’s date (1–25)
- Ensure the user hasn’t already claimed
- Apply blacklists
- Award the configured reward
- Log the claim to the database

---

# ⚠ Notes

- This package **does not modify `bd_models`**, making it safe for updates.
- Days outside December 1–25 return “No reward available today.”
- Blacklisted users cannot claim.
- Follows the same structure as the Crafting package for safe integration.

---

# 🧊 Credits

Created for **MarketDex**, inspired by the Crafting package.  
Simple, powerful, and fully customizable.

