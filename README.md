# League-of-Legends-Summoner-Spell-Ultimate-Tracker
A lightweight overlay for tracking enemy cooldowns in League of Legends. Click summoner spells or ultimates to start timers, and the app shows a compact ready time (e.g., “Ahri Flash - 5:27”) in a single-line log.

## Features  
- **One-click timers**: Automatically tracks Summoner Spells & Ultimates with Ability Haste/Lucidity/Cosmic modifiers.
- **Unleashed Teleport Support**: Automatically swaps Teleport -> Unleashed Teleport when the game timer reaches 10:00 (with appropriate cooldowns).
- **Up-to-date icons & information**: Communicates directly with Riot's Data Dragon API to pull the most recent/accurate icons and cooldowns.
- **Themes**: Default/Dark/Light + a stylish Master/Grandmaster/Challenger with crest watermark and adjustable crest opacity.  
- **Settings**: Window opacity slider and “Always on Top” toggle (great for overlays).
- **Game Configuration**: Manual configuration--pick any 5 champions and their summoners, then apply to the main view.

## Installation  

### Prerequisites  
- Python 3.10+  

## Requirements  

```
PyQt5
requests
```

### Setup  

1. Download ```summoner_tracker.py```:
- Open the file and click Raw → Save As...
- Or run:
   ```sh
   curl.exe -L -o "summoner_tracker.py" "https://raw.githubusercontent.com/Borping/League-of-Legends-Summoner-Spell-Ultimate-Tracker/main/summoner_tracker.py"
   ```  

2. Install dependencies:  
   ```sh
   pip install -r requirements.txt  
   ```  

3. Run the application:  
   ```sh
   python summoner_tracker.py
   ```  

### Visuals
- Main Window
![Main Screen](https://i.imgur.com/GCLgOO1.png)

- Game Configuration
![Game Configuration](https://i.imgur.com/tK1Pwzt.png)

- Pinned Transparent Window
![Transparency/Pinned Window](https://i.imgur.com/uxIogzn.png)

- Themes
![Themes](https://i.imgur.com/HbMaZHh.png)
