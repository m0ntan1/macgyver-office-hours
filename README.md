![Adventures in STEM](ADVENTURES%20IN%20STEM%20%28960%20x%20600%20px%29.png)

# MacGyver Office Hours

**Real engineering lessons from every MacGyver episode.** Prof. Johan Stemson breaks down the physics, chemistry, and mechanical engineering behind every hack, then turns each episode into a ready-to-teach 60-minute classroom session.

This repo holds the one-page educator site ([`index.html`](index.html)) plus per-episode lesson plans you can download or hand to teachers without making them scroll through the whole site.

macgyverofficehours.com

## Lesson Plans

Season 1 has 10 plans available. Each plan includes the 60-minute schedule, timestamped clips to play in class, NGSS/CCSS standards alignment, and the episode's recurring themes.

| Episode | Title | What's Inside | Markdown | HTML |
|---|---|---|---|---|
| S01E01 | Pilot | Dehydration reactions, alkali metals, and light scattering, anchored by the chocolate-into-sulfuric-acid rescue. | [.md](lessons/S01E01-pilot.md) | [.html](lessons/S01E01-pilot.html) |
| S01E02 | The Golden Triangle | Burma jungle escape built around gas-pressure systems, buoyant decoys, and cable mechanics. | [.md](lessons/S01E02-the-golden-triangle.md) | [.html](lessons/S01E02-the-golden-triangle.html) |
| S01E03 | Thief of Budapest | A Cold War microfilm chase that turns into a tour of refraction, improvised optics, and RF jamming. | [.md](lessons/S01E03-thief-of-budapest.md) | [.html](lessons/S01E03-thief-of-budapest.html) |
| S01E04 | The Gauntlet | Simple machines and materials science culminating in a duct-tape hot air balloon. | [.md](lessons/S01E04-the-gauntlet.md) | [.html](lessons/S01E04-the-gauntlet.html) |
| S01E05 | The Heist | Casino vault job blending probability theory, acoustic resonance, and fiber-optic security. | [.md](lessons/S01E05-the-heist.md) | [.html](lessons/S01E05-the-heist.html) |
| S01E06 | Trumbo's World | An Amazon plantation under army-ant attack opens the door to organic synthesis and combustion energy. | [.md](lessons/S01E06-trumbos-world.md) | [.html](lessons/S01E06-trumbos-world.html) |
| S01E07 | Last Stand | Desert airstrip hostage rescue centered on thermite, phase change, and mechanical advantage. | [.md](lessons/S01E07-last-stand.md) | [.html](lessons/S01E07-last-stand.html) |
| S01E08 | Hellfire | A Wyoming oil-well fire teaches vibration isolation, electrical conductivity, and the chemistry of controlled explosives. | [.md](lessons/S01E08-hellfire.md) | [.html](lessons/S01E08-hellfire.html) |
| S01E09 | The Prodigal | Wilderness pursuit unpacking phase changes (freezing, sublimation) and lever-based traps. | [.md](lessons/S01E09-the-prodigal.md) | [.html](lessons/S01E09-the-prodigal.html) |
| S01E10 | Target MacGyver | Cabin-under-siege survival anchored by structural mechanics, combustion, and projectile physics. | [.md](lessons/S01E10-target-macgyver.md) | [.html](lessons/S01E10-target-macgyver.html) |

Episodes S01E11 through the end of Season 1 (and beyond) are written up on the site with engineering breakdowns, but don't have a packaged classroom lesson plan yet. Those are still being authored.

### Two formats, same content

- **Markdown** renders cleanly here on GitHub. Best for previewing in a browser, copy-pasting into a doc, or piping into another tool.
- **HTML fragment** is a self-contained page with the site's "engineering blueprint" styling. Open it locally in a browser to preview, or print it as a one-pager handout.

## Viewing the site

Open `index.html` in any browser:

```sh
open index.html        # macOS
xdg-open index.html    # Linux
start index.html       # Windows
```

The site is a single self-contained HTML file. No build step, no server required.

## Regenerating the lesson files

The files in `lessons/` are extracted from `index.html` by [`scripts/extract_lessons.py`](scripts/extract_lessons.py). When the site adds or edits a lesson plan, re-run:

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/extract_lessons.py
```

The script is idempotent. Running it twice on an unchanged `index.html` produces no diff.

## Support

If these lesson plans land in your classroom and help, a tip keeps the project going:

- Lightning / Nostr: [primal.net/Montani](https://primal.net/Montani)
- Cash App: [$montanibtc](https://cash.app/$montanibtc)

## License

MIT. See [LICENSE](LICENSE). Use the lesson plans, remix them, hand them out. Credit appreciated.
