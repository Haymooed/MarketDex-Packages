# 🎄 AdventCalendar-package-BD  
A full Advent Calendar system for custom BallsDex / MarketDex instances.

This package adds:  
• A Discord slash command: **/advent claim**  
• A full Django admin panel section to configure rewards for **Dec 1–25**  
• Automatic tracking so each player can only claim once per day  

---

## 📌 What’s Included
- Daily reward configuration for **1–25 December**
- Three reward modes:  
  **1)** Random enabled ball + random special  
  **2)** Selected ball  
  **3)** Selected ball + selected special  
- Blacklist support (respects `bot.blacklist`)  
- Logs every claim with timestamp  
- Shared Django + Tortoise ORM models  
- Prevents duplicate daily claims  

---

## ⚠️ Important  
This is a **custom** extension.  
No official BallsDex support will be provided.

For issues, DM **@Haymooed** or ping in the dev server.

---

## 📦 Installation

# Step 1 — Add the package to your bot  
Copy the folder **`adventcalendar`** into:

```
BallsDex-DiscordBot/ballsdex/packages/
```

Your final structure should look like:

```
ballsdex/
 └── packages/
      └── adventcalendar/
          ├── __init__.py
          ├── cog.py
          ├── models.py
          └── ...
```

---

# Step 2 — Enable the package in `config.yml`  
Inside your bot’s main configuration file:

```yml
packages:
  - ballsdex.packages.adventcalendar
```

You MUST list it like other packages.

---

# Step 3 — Update Tortoise ORM (VERY IMPORTANT)

In `ballsdex/__main__.py`, your `TORTOISE_ORM` **models list** must include:

```py
"models": [
    "ballsdex.core.models",
    "ballsdex.packages.adventcalendar.models",
],
```

If this line is missing, the bot will crash on startup.

---

# Step 4 — Add Django Admin support  
Copy the **admin_panel** folder named `adventcalendar` into:

```
BallsDex-DiscordBot/admin_panel/adventcalendar
```

It should look like:

```
admin_panel/
 ├── admin_panel/
 ├── adventcalendar/
 │    ├── __init__.py
 │    ├── admin.py
 │    ├── models.py
 │    └── apps.py
```

---

# Step 5 — Install into Django (admin panel)

Open:

```
admin_panel/admin_panel/settings/local.py
```

Add this line:

```py
INSTALLED_APPS.append("adventcalendar")
```

Then run migrations:

```bash
docker compose exec admin-panel python3 manage.py makemigrations adventcalendar
docker compose exec admin-panel python3 manage.py migrate adventcalendar
```

If you see “orphans”, run:

```bash
docker compose down --remove-orphans
```

---

## 🎨 How to Use in Django Admin

After installation, go to:

```
localhost:8000/admin
```

You will see:

**Advent Calendar → Advent Day Config**  
**Advent Calendar → Advent Claims**

For each day **1–25**, set:

- Day number  
- Enabled  
- Reward type  
- Optional: Ball  
- Optional: Special  
- Optional: Label (small description)

---

## ❄️ `/advent claim` Command Behavior

- Only works **Dec 1–25**  
- Respects blacklist  
- Prevents duplicate claims  
- Rewards user instantly with a BallInstance  
- Logs claim in database  
- Sends a clean embed showing the reward  

### Reward Logic
| Reward Type | What Happens |
|-------------|--------------|
| Random Special | Picks random enabled Ball + random Special |
| Selected Ball | Gives the chosen ball |
| Selected Ball + Special | Gives chosen ball & chosen special |

---

## 🗂 Included Models (Tortoise + Django)

### `AdventDayConfig`
- day (1–25)  
- enabled  
- reward_type  
- ball (optional)  
- special (optional)  
- label (description)  

### `AdventClaim`
- player  
- day  
- claimed_at  
- unique per day per user  

---

## 🎁 Final Notes
- If a day is misconfigured, `/advent claim` warns the user.  
- If a user is blacklisted, the bot refuses the claim.  
- If a player tries claiming twice, the bot blocks it.  
- Works flawlessly once models + admin + config.yml are correct.

---

Enjoy your new Advent Calendar system!
