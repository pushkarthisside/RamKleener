# 🚀 RamKleener v2.0

> **Kill background bloat. Free your RAM. Stay in control.**

RamKleener is a Python CLI utility that scans system processes, filters them using a strict safety model, and terminates known memory-heavy background tasks with user confirmation — directly from the terminal.

---

## ✨ Features

- **Safe by Design** — Uses a strict two-tier safety model so only known, non-critical processes are targeted.
- **Grouped Process Control** — Apps like Chrome or Edge run multiple processes — RamKleener groups them so you can handle everything in one step.
- **No Accidental Kills (PID Protection)** — Double-checks each process before terminating to avoid mistakes caused by system PID reuse.
- **Interactive Customization** — Add your own protected apps or kill targets directly through the built-in terminal UI (no config files required).
- **Fast Scanning** — Efficient filtering ensures quick results even with hundreds of running processes. *(O(1) Filtering)*
- **Clean Terminal UI** — Displays RAM usage and results clearly with simple bars, tables, and color-coded statuses.

---

## 🛡️ Safety Model

> **If it's not clearly safe, it won't be touched.**

| Tier | What's Included | Behavior |
|---|---|---|
| 🔒 **Protected** | Core system processes, security services, critical apps | Completely locked — cannot be terminated |
| ⚡ **Safe to Kill** | Browsers, updaters, background services | Eligible for termination |
| ❓ **Unknown** | Anything not recognized | Ignored by default |

If a process appears in both categories: **Protected always wins.**

---

## 🚀 Installation

Ensure you have **Python 3** installed on your system.

Open your terminal or command prompt and run:

```bash
git clone https://github.com/pushkarthisside/RamKleener.git
cd RamKleener
pip install .
```

*Note: If you are developing or editing the code yourself, use `pip install -e .` instead.*

Once installed, you can launch the tool from anywhere by simply typing:

```bash
ramkleener
```

---

## 🎮 Usage

When you run RamKleener, you will be greeted with the main menu:

```text
  1. Scan             — show active bloat apps above your RAM threshold
  2. Kill all         — instantly terminate all flagged processes
  3. Kill one by one  — step through groups (y=kill, n=skip, q=quit)
  4. Customize Lists  — interactive UI to manage your Safe and Clean apps
  5. Help             — view color legends and tool documentation
  6. About            — version and author info
  0. Exit             — exits the main menu
```

**Kill one by one** is recommended — it groups processes by app so you decide per application (e.g., all of Chrome at once), not per individual PID.

---

## 🧩 Customize (No Code Required)

RamKleener features a built-in interactive customization menu so you never have to hunt down hidden system folders or edit raw JSON files.

From the main menu, select **`4. Customize Lists`**.

### How it works

When you enter the Customize menu, RamKleener automatically scouts your PC for the heaviest running apps.

- **Smart Toggle:** To manage an app, simply type its `#` number from the table (or type an app name manually like `spotify`).
- If the app is **not** on your list, it gets **added**.
- If the app is **already** on your list, it gets **removed**.

### The Color Legend

RamKleener uses context-aware colors that change depending on which menu you are managing:

#### 📂 Option 1: Clean Apps Menu
- 🟢 **Green (✓ Clean Target):** The app is on your kill list and will be closed if it hogs RAM.
- 🔴 **Red (🔒 Protected):** Critical OS process or blocked by your Safe list. Cannot be added.
- 🟡 **Yellow (❓ Neutral):** Ignored by RamKleener. Type its number/name to add it to the clean list.

#### 🛡️ Option 2: Safe Apps Menu
- 🟢 **Green (✓ Safe/Locked):** Whitelisted app. RamKleener is locked out and the app/process will never get terminated.
- 🔴 **Red (⚠️ Kill Target):** Warning! This app is currently on your kill list.
- 🟡 **Yellow (❓ Neutral):** Ignored by RamKleener. Type its name to secure it on the safe list.

*(Advanced Users: The raw configuration file is still automatically generated and accessible at `~/.ramkleener/config.json` if you prefer manual editing).*

---

## 👤 About

I built it because my 8GB RAM laptop was constantly bloated and I couldn't find a tool that was both safe and customizable enough to trust.

RamKleener is the result. It's tuned to my machine, and with a few clicks in the customization menu, it can be perfectly tuned to yours too.

If you run into any issues — installation, config, or anything else — feel free to [open an issue](https://github.com/pushkarthisside/RamKleener/issues).

Cheers 🙂 — hope it helps.