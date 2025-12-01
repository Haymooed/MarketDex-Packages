

# 🎅 SantaMail – BallsDex Package

The **SantaMail** package adds a festive, Christmas-themed event to your BallsDex bot.  
Players can receive random seasonal items directly into their BallsDex inventory during the event.

This package is fully modular, configurable, and ready to plug into any BallsDex project, including forks like **MarketDex**, **FruitDex**, or others.

---

## ✨ Features

- 📬 **SantaMail Event** — Users receive random Christmas items.  
- 🎁 **Fully Integrated Rewards** — Items go directly into BallsDex inventory.  
- ⚙️ **Configurable** — Modify event channels, rarity, and drop rates.  
- 👑 **Admin Controls** — Admins can trigger or refresh SantaMail drops.  
- 🎄 **Festive Fun** — Perfect for holiday events in your server.

---

## ⚙️ Setup

1. **Drop the package** into your BallsDex bot directory:
ballsdex/packages/santamail/
2. **Ensure these files exist:**
- `cog.py` — the core SantaMail logic.  
- `__init__.py` — registers the cog.  
- `config.toml` — optional settings for drops and channels.  

3. **Add this to `config.toml`:**
```toml
# Channel ID where SantaMail drops appear
event_channel = 123456789012345678

# Maximum rarity of items in SantaMail
max_rarity = 200

# Role IDs allowed to trigger/refresh SantaMail
admin_roles = [123456789012345678]
