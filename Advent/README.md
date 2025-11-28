# 🎄 Advent Calendar Package

An Advent Calendar event for BallsDex/MarketDex. It adds a Discord bot cog (`/advent claim`) and a Django admin app so you can configure rewards for December 1–25 and track one claim per user per day.

> [!IMPORTANT]
> More refurbished instructions comming soon

## Features
- Configurable rewards per Advent day (1–25): random special, selected ball, or selected ball with special.
- Blacklist-aware claim handling that respects `bot.blacklist`.
- Shared database tables for both Tortoise (bot) and Django (admin panel) models.
- Prevents duplicate daily claims and logs claim timestamps for auditing.
---
## Bot setup
1. Ensure the package directory lives at `ballsdex/packages/adventcalendar`.
2. Load the extension like other BallsDex packages (add `ballsdex.packages.adventcalendar` to config.yml).
3. Confirm the Tortoise config includes `"ballsdex.packages.adventcalendar.models"` (the provided `ballsdex/__main__.py`).
---
## Admin panel setup
1. Add to`INSTALLED_APPS` in `admin_panel/settings/local.py`: 
INSTALLED_APPS.append("adventcalendar")
2. Run migrations from the admin-panel container:
   - `docker compose exec admin-panel python3 manage.py makemigrations adventcalendars`
   - `docker compose exec admin-panel python3 manage.py migrate adventcalendars`
3. Use the Django admin to create or edit entries for days 1–25, choosing reward type, enabled state, and optional ball/special.
---
## Database models
- `AdventDayConfig` stores the per-day reward setup (day, enabled flag, reward type, optional ball and special, description).
- `AdventClaim` records each player's claim per day and enforces a unique `(player, day)` pair.
---
## Using `/advent claim`
- Valid only during December 1–25; outside that range the command responds that the event is inactive.
- Blacklisted users receive "You are blacklisted from using this event." and cannot claim.
- If no active config exists for the day, the bot replies "There is no active reward for today.".
- Successful claims create a `BallInstance` for the chosen reward and log an `AdventClaim` entry, then reply with an embed showing the reward.

## Notes
- For the `random_special` reward, the bot selects a random enabled `Ball` and a random `Special`.
- For `selected_ball` and `selected_ball_with_special`, make sure the relevant ball (and special) fields are populated for that day; otherwise the bot treats the reward as misconfigured.
