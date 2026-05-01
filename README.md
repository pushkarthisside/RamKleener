# 🚀 RamKleener v2.0

> **Kill background bloat. Free your RAM. Stay in control.**

RamKleener is a Python CLI utility that scans system processes, filters them using a strict safety model, and terminates known memory-heavy background tasks with user confirmation — directly from the terminal.

---

## ✨ Features

- **Safe by Design** — Uses a strict two-tier safety model so only known, non-critical processes are targeted.
- **Grouped Process Control** — Apps like Chrome or Edge run multiple processes — RamKleener groups them so you can handle everything in one step.
- **No Accidental Kills (PID Protection)** — Double-checks each process before terminating to avoid mistakes caused by system PID reuse.
- **Fast Scanning** — Efficient filtering ensures quick results even with hundreds of running processes. *(O(1) Filtering)*
- **Clean Terminal UI** — Displays RAM usage and results clearly with simple bars and tables.
- **Customizable** — Add your own protected apps or kill targets through a simple config file.

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

```bash
git clone https://github.com/pushkarthisside/RamKleener.git
cd RamKleener
pip install -e .
```

Then run it:

```bash
ramkleener
```

---

## 🎮 Usage

```
1. Scan             — show flagged processes + RAM usage
2. Kill All         — terminate all flagged processes with summary
3. Kill One by One  — grouped flow per app (y=kill  n=skip  q=quit)
4. Help
5. About
0. Exit
```

**Kill One by One** is recommended — it groups processes by app so you decide per application, not per PID.

---

## 🧩 Customize

RamKleener uses a config file to know what to kill and what to protect on your specific machine.

**Where is it?**

```
Windows:   C:\Users\YourName\.ramkleener\config.json
Mac/Linux: /home/yourname/.ramkleener/config.json
```

This file is created automatically the first time you run RamKleener. Open it with any text editor (Notepad works fine).

---

**How do I know what to add?**

On Windows — open Task Manager → go to the **Details** tab → look for processes using high memory that you don't need running in the background (updaters, sync tools, crash handlers).

Note the name in the **Name** column (e.g. `Spotify.exe`). Remove the `.exe` part and add it lowercase.

---

**Adding a process to kill:**

```json
{
  "user_protected": [],
  "user_kill_list": ["spotify", "discord", "brave"],
  "threshold_mb": 50
}
```

**Protecting something you don't want touched:**

```json
{
  "user_protected": ["docker", "my_work_app"],
  "user_kill_list": [],
  "threshold_mb": 50
}
```

- `user_protected` — RamKleener will never touch these, no matter what
- `user_kill_list` — RamKleener will target these if they're using enough RAM
- `threshold_mb` — processes using less RAM than this are ignored entirely (default: 50 MB, minimum: 10 MB)

Not sure what to add? Run option `1. Scan` first — it shows exactly what RamKleener can already see on your machine. Start from there.

---

## 👤 About

I built it because my 8GB RAM laptop was constantly bloated and I couldn't find a tool that was both safe and customizable enough to trust.

RamKleener is the result. It's tuned to my machine, and with a few config edits, it can be tuned to yours too.

If you run into any issues — installation, config, or anything else — feel free to [open an issue](https://github.com/pushkarthisside/RamKleener/issues).

Cheers 🙂 — hope it helps.
