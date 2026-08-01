# [WIP] QmlVcp Builder — A WYSIWYG drag-and-drop GUI builder for LinuxCNC, looking for contributors

**Short version:** I built a visual GUI builder for LinuxCNC that lets you drag-and-drop controls (DROs, LEDs, buttons, toolpath viewers, etc.) onto a canvas, edit their properties, and export a fully runnable QML project. It works at a basic level, but there's still a lot to improve — and I'd love help from anyone interested.

**GitHub:** [https://github.com/ltwl2016/qmlvcp-builder](https://github.com/ltwl2016/qmlvcp-builder)

---

## What it does

1. **Drag controls** from a palette onto a canvas
2. **Edit properties** — position, size, colors, images, text, fonts
3. **Bind actions** — click a button → execute CNC commands (homing, spindle, coolant, program start, etc.)
4. **Bind status** — LED turns green when axis is homed, DRO shows live position, etc.
5. **Multi-page layout** — main page, side panels, top/bottom bars
6. **One-click export** — generates a self-contained project: copy it to your LinuxCNC machine, configure `[DISPLAY]` in your ini, and it runs

Built with Python + PyQt5 (native to LinuxCNC 2.10). Exported projects use PySide6.

**17 control types currently supported:** ImageButton, SpriteButton, LED, FlashLED, Text_DRO, Text_Label, TextField, MachTextInput, GCodeGraphics (3D toolpath view), GCodeViewer, EmergencyStop, JOGButton, Image, Rectangle, Timer, FileDialog, RunFromHereDialog.

---

## What it looks like (screenshots)

_(todo: add screenshots here — Builder editing canvas + an exported panel running on a LinuxCNC machine)_

---

## Honest status: what works and what doesn't

This is **not a finished product**. It has the core workflow working (drag → configure → export → run on LinuxCNC), but many areas are rough. I built this alone and there's only so much one person can do.

### Done ✅
- Drag-and-drop assembly with real-time preview
- Property panel with dynamic fields
- 17 control types with QML templates
- Action system (CNC commands)
- Status binding system (machine state → UI)
- One-click project export
- Offline PySide6 installation for air-gapped machines
- Basic multi-page architecture

### Needs work ⚠️
- More control types (sliders, knobs, gauges, waveform displays, custom HAL pin widgets)
- Flexible HAL pin mapping (currently only predefined bindings)
- Keyboard shortcuts (undo/redo, copy/paste in Builder)
- Better default styling/QSS
- Touch gesture support
- Video tutorials and better documentation

### Not started ❌
- i18n / multi-language support
- Unit tests / CI
- Real-machine testing across different LinuxCNC versions and screen resolutions
- Control alignment helpers (snap-to-grid, even distribution)

---

## What kind of help I'm looking for

I'm posting this on the LinuxCNC forum because this is the community that actually uses this stuff. Whether you're a Python dev, a QML person, a LinuxCNC power user, a UI/UX enthusiast, or just someone who wants a better custom panel for their machine — there's something you can contribute.

### Developers
- **New controls** — Write QML templates + property definitions for more widget types
- **HAL pin flexibility** — Let users bind arbitrary HAL pins instead of choosing from predefined ones
- **Undo/redo system** — Proper command pattern in the Builder
- **Tests** — pytest for core modules
- **i18n** — Multi-language support

### LinuxCNC users
- **Real-machine testing** — Try it on your setup, report what breaks
- **Example projects** — Build a real CNC panel and contribute it to the repo's `examples/`
- **Feedback** — What controls are missing that you'd actually use?

### Designers / UX
- **Better QSS/CSS** — Polish the Builder and exported project appearance
- **Touch-friendly layout** — Optimize for typical CNC touchscreens

### Anyone
- **Documentation** — Improve the README, add comments, translate between Chinese and English
- **Video tutorials** — Screen recording of the full workflow
- **Bug reports** — Open an issue with steps to reproduce

---

## How to get involved

1. **[Fork the repo](https://github.com/ltwl2016/qmlvcp-builder)**
2. Pick something from the list above (or your own idea)
3. Open an Issue to discuss if it's a big feature
4. Submit a PR

No contribution is too small — even fixing a typo in the docs is appreciated.

---

## Why this exists

I got tired of writing QML by hand every time I wanted a custom LinuxCNC panel. QtPyVCP is great but still requires coding. Gmoccapy works but customizing it is painful. I wanted something closer to a visual designer — think Qt Designer or Glade, but CNC-specific.

This is a passion project. I'm sharing it in the hope that others find it useful and want to help make it better. Even if all you do is try it and tell me what's broken, that's valuable.

---

**GitHub:** [https://github.com/ltwl2016/qmlvcp-builder](https://github.com/ltwl2016/qmlvcp-builder)

Thanks for reading!

---

_Note to self: replace `(todo: add screenshots)` with actual GIFs/images before posting._
