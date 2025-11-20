# 🎅 Santa Mail

Send holiday cheer via `/santa mail`, which randomly selects a non-bot member in the guild and delivers them a Tier 1-100 countryball directly in their DMs. Each delivery is timestamped in Australian (Sydney) time to match the holiday postmark.

## Commands
- `/santa mail` — Picks a random member, rolls a Tier 1-100 enabled ball, creates the instance for them, and attempts delivery via DM.

## Notes
- Requires the bot to have member intents enabled so it can pick a random eligible recipient.
- Delivery summarizes success or failure ephemerally to the command invoker. If DMs are closed, the gift remains owned by the recipient even if the message cannot be delivered.
