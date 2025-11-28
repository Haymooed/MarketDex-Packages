# 🎄 Reindeer Rush Package  
A fast, fun, fully-animated betting mini-game for BallsDex / MarketDex.  
Players bet on reindeer (balls) and watch them race on a live-updating text track.

This version includes:
- Dynamic racer count (`/admin market setracers`)
- Fully interactive button-based betting
- Automatic reward delivery to winning bettors
- Clean, dependency-free drop-in Cog

---

## ✨ Features
- Button betting UI  
- Dynamic number of racers (2–20)  
- Live race updates every second  
- Awards winners automatically  
- Uses your existing BallsDex balls  
- Works on any server, no extra setup  

---

## 📦 Installation

### 1. Copy the folder  
Place the folder **`reindeerrush`** inside:

```
ballsdex/packages/
```

So the path becomes:

```
ballsdex/packages/reindeerrush
```

---

### 2. Enable it in `config.yml`

```yaml
packages:
  - ballsdex.packages.reindeerrush
```

---

### 3. Add to your bot entry file  
In your bot’s package loader:

```python
await bot.load_extension("ballsdex.packages.reindeerrush")
```

---

## 🦌 Commands

### `/admin market reindeerrace`
Starts a race immediately.

### `/admin market setracers <number>`
Changes how many balls race.

Examples:
```
/admin market setracers 5
/admin market setracers 12
```

---

## 📁 File Structure
```
reindeerrush/
│── __init__.py
│── cog.py
```

---

## ✔ Requirements
- Python 3.10+
- BallsDex
- Enabled balls in the database

---

Enjoy the chaos of Reindeer Rush! 🎄🦌💨
