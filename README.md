
# 🎮 Fill the Basket - S-400 Missile Catcher Game

A fun hand-tracking based game where you use both your hands to control **two S-400 missile launchers** and catch falling missiles.

---

## 🕹️ How to Play

- Use **left and right hands** in front of your webcam.
- Control **two separate S-400 launchers** using your index fingers.
- Catch the falling **PK Missiles** with either launcher.
- **Miss one missile → Game Over**.
- Press **R** to restart after Game Over.

---

## 📦 Files Needed

Ensure all these files are in the same folder:

- `main.py` → Game logic
- `hand_module.py` → Hand tracking helper
- `S400.png` → Launcher image
- `PK Missile 1.png` → Missile image
- `PK Missile 2.png` to `PK Missile 8.png` → Additional missile designs

---

## 🛠️ Requirements

Install dependencies using:

```bash
pip install opencv-python mediapipe pygame
```

✅ Recommended Python version: **3.8 to 3.10**

---

## 🚀 Run the Game

Make sure your webcam is available and not being used by another app.

```bash
python main.py
```

---

## 💡 Features

- 🧤 Dual S400 launchers (left & right hand control)
- 🎯 Multiple random falling missiles
- 🖼️ Live camera feed as background
- 💥 Game over on a single miss
- 🏁 Final score display
- 🔁 Restartable with one key

---

## 🔧 Possible Upgrades

- 🔊 Add sound effects
- ⏱️ Timer or level mode
- 💣 Bombs to avoid
- 🏆 Leaderboard system

---

> Made with ❤️ using Python, OpenCV, Pygame & MediaPipe
