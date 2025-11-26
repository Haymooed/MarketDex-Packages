# 🎄 Advent Calendar — BallsDex Package

The **Advent Calendar** package adds a daily reward system for December (1st–25th).  
Each day has a configurable reward that you set using the **BallsDex Admin Panel** (Django).

This package supports:
- Daily claim tracking  
- Custom rewards per day  
- Rewards: selectable balls, random specials, or combined rewards  
- Admin panel integration (inside `/adminpanel`)  
- Works with the BallsDex bot & database

---

## 📦 Installation

1. Download or clone this repository.
2. Place the folder in:  
   ```
   ballsdex/packages/adventcalendar
   ```
3. Add it to your `config.yml`:
   ```yaml
   packages:
     - ballsdex.packages.adventcalendar
   ```

---

## ⚙️ Admin Panel (Django)

This package includes Admin Panel support so you can easily configure all 25 days.

### Location:
All Django admin panel files are inside:
```
adminpanel/adventcalendar/
```

This includes:
- `models.py`
- `admin.py`
- `apps.py`
- `__init__.py`
- `views.py` (empty boilerplate like Crafting Package)
- `migrations/` folder

### How to Enable in Django:

Inside your **BallsDex Django project**:

#### 1. Add the app to `INSTALLED_APPS`  
Open:
```
admin_panel/settings/local.py
```

Add:
```python
INSTALLED_APPS.append("adventcalendar")
,
]
```

#### 2. Run migrations:
```
python manage.py makemigrations
python manage.py migrate
```

#### 3. Restart the admin panel

Visit the admin panel and you will now see:

> Advent Calendar  
> ➜ Calendar Entries (1–25)

Each entry lets you configure:
- Day number  
- Reward type  
- Assigned balls  
- Assigned specials  
- Custom notes  

---

## 🎁 Bot Commands

### `/advent claim`
Users claim the reward for the current day.

### Features:
- Automatically checks the current date
- Prevents re-claiming the same day
- Checks blacklist & staff logic
- Rewards are created as `BallInstance`

---

## 🗂 File Structure

```
adventcalendar/
│
├── cog.py              # Bot logic (slash commands)
├── __init__.py         # Extension loader
│
└── adminpanel/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── views.py
    └── migrations/
```

---

## ✨ Reward Types Supported
Each day can reward:

- **Specific Ball**
- **Random Enabled Ball**
- **Specific Special**
- **Random Special Event**
- **Combo (Ball + Special)**

You configure these yourself in the admin panel.

---

## ❄️ Notes
- Only days **1–25** are valid  
- Users can only claim once per day  
- Staff can use force-commands if added later  
- Blacklisted users are skipped  
- Advent Calendar is December-only (can be changed manually)

---

## 🧑‍🎄 Support
For help setting up or modifying the package, open an issue or message Haymooed 😎

---

