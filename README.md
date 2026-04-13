# 🚀 RamKleener

**Kill background bloat. Free your RAM. Stay in control.**

RamKleener is a terminal-based utility designed to scan, highlight, and safely terminate memory-heavy background tasks. Unlike "one-click optimizers" that make risky assumptions, RamKleener puts the decision-making power in your hands.

---

## ✨ Features

- 🔍 **Deep Scan** — Full process visibility with real-time memory usage
- 🛡️ **3-Tier Safety** — Hardcoded protection for OS-critical processes
- 🧹 **System Scrub** — Integrated cleanup for system and user temp folders
- 📊 **Clean UI** — Grouped process views powered by the `rich` library
- ⚙️ **Fully Customizable** — Dynamic kill/protect lists via config or source
- 🖥️ **Cross-Platform** — Native support for Windows, Linux, and macOS

---

## 🧠 The Philosophy

Modern operating systems are cluttered with background updaters, sync tools, and crash handlers you never explicitly started. RamKleener doesn't guess what to kill. It surfaces the data and gives you the surgical tools to decide what stays and what goes.

---

## ⚠️ The Honest Truth

This is not plug-and-play.

Every system is unique. A process that is useless on one machine might be critical on another. If you run this without configuration, it will likely find nothing to clean — that is a feature, not a bug.

RamKleener is built to be customized for your specific workflow.

---

## ⚙️ How It Works

RamKleener uses a strict 3-tier protection model to ensure system stability:

| Tier | Name | Behavior |
|------|------|----------|
| 1 | `NEVER_KILL_CORE` | OS critical processes — hard-locked and never touched |
| 2 | `NEVER_KILL_DEFAULT` | Protected by default (Launchers, AV, Games) |
| 3 | `SAFE_TO_KILL` | Known bloat — eligible for termination if above threshold |

**The Golden Rule:** If a process isn't in a list, it's skipped. Unknown = Safe.

---

## 🚀 Getting Started

### 1. Clone & Install

```bash
git clone https://github.com/pushkarthisside/RamKleener.git
cd RamKleener
pip install -e .
```

### 2. Configure Your Kill List

Open Task Manager → Details tab. Find background processes you don't need (e.g. `brave.exe`, `onedrive.exe`, `spotify.exe`).

Add them to `ramkleener/lists.py`:

```python
SAFE_TO_KILL = {
    "brave",
    "spotify",
    "onedrive",
    # ... add your own
}
```

### 3. Run

```bash
ramkleener
```

> Run as Administrator (Windows) or `sudo` (Linux/Mac) for full cleanup — enables system temp deletion and standby RAM flush.

---

## 📋 Menu

| Option | Action |
|--------|--------|
| `1` Scan | Preview only — nothing is killed |
| `2` Clean | Kill bloat + clear temp files |
| `3` Full Clean | Kill + temp + standby RAM flush + RAM report |
| `4` Help | — |
| `0` Exit | — |

---

## ⚙️ Config

Located at `~/.ramkleener/config.json` — created automatically on first save.

```json
{
  "user_protected": ["my_work_app"],
  "user_kill_list": ["heavy_updater"],
  "threshold_mb": 50
}
```

| Key | Purpose |
|-----|---------|
| `user_protected` | Extra processes to never kill — added to Tier 2 |
| `user_kill_list` | Extra processes to kill — added to Tier 3 |
| `threshold_mb` | Ignore processes using less than this much RAM |

---

## 🧪 Phase 1 — PowerShell Version

Same logic. Windows only. No Python required.

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\Phase1\RamKleener.ps1
```

---

## 📁 Structure

```
RamKleener/
├── Phase1/
│   └── RamKleener.ps1
├── ramkleener/
│   ├── lists.py       ← edit this
│   ├── config.py
│   ├── scanner.py
│   ├── cleaner.py
│   ├── display.py
│   └── cli.py
├── setup.py
├── requirements.txt
└── README.md
```

---

## ⚠️ Known Limitations

- RAM freed is an estimate — Windows memory management is complicated
- Standby flush requires Admin or it silently fails
- Process names vary across Windows versions — always verify in Task Manager Details
- Temp cleanup can lag on first run if your temp folder is large

---

## 🛣️ Roadmap

- [ ] PyInstaller `.exe` build — no Python required
- [ ] Quiet mode (auto-clean when RAM crosses threshold)
- [ ] Interactive list editor in the menu

---

*Built by Pushkar — Phase 1 ✅ Phase 2 ✅ Phase 3 (in tha future maybe).*