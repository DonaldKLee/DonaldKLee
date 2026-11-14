# Duck race setup

Visitors tap **Roll for shades** or **Roll for cape** on your profile. That opens a pre-filled issue that tells them to press **Create**. A GitHub Action then rolls the die, moves their duck, scores them, redraws the pond, replies with the result and closes the issue. It takes about 30 seconds.

## Install

1. Push these to your profile repo (`DonaldKLee/DonaldKLee`):
   ```
   README.md
   game/
   .github/workflows/dice.yml
   ```
2. **Settings → General → Features:** make sure **Issues** is on.
3. **Settings → Actions → General → Workflow permissions:** choose **Read and write permissions**.
4. Tap a roll button on your own profile to test it.

## Rules

- First duck to square 20 wins the round. Then both ducks go back to the start.
- Once you roll for a duck, you're on its team until the round ends.
- You can't roll twice in a row on the same day. Someone else has to roll first, or you come back the next day.
- A duck that's 6 or more squares behind gets +1 on every roll, so races stay close.
- Points: +1 per roll, a daily streak bonus, and +3 for everyone who rolled for the winning duck. The streak bonus is paid on your first roll of each day (UTC) and equals the number of days in a row you've rolled, up to +5.

## Tweaking

Game settings are at the top of `game/dice.py`:

- `TRACK_LENGTH`: race length.
- `TEAMS`: the two ducks. The cape duck keeps the key `tophat` so old roll links still work. If you rename a key, update `TITLE_RE` too.
- `TILES`: the special squares.
- `POINTS_ROLL`, `POINTS_WIN`, `STREAK_CAP`: the scoring.
- `CATCH_UP_GAP`, `CATCH_UP_BOOST`: the catch-up boost for a duck that's far behind.
- `roll_link()`: the how-to-play text players see when they tap a roll button.
- `LINKS`: the labels and icons of the rounded link buttons under your intro (`game/link-*.svg`). Where each one points is set in `README.md`.
- `LEADERBOARD_SIZE`: how many players the README shows. Everyone is listed in `game/leaderboard.md`, which the README and the bot's replies link to.

Art is in `game/art.py`:

- Colours are the constants at the top (`DUCK`, `BEAK`, `CAPE`, `SHADES`, `WATER`, `BUTTON`).
- `DUCK_PARTS` defines each duck piece once. `duck-sunglasses` and `duck-cape` stack the pieces into each duck. To add an accessory, add its shapes and a `duck-<name>` group, then set `"accessory": "<name>"` for the team in `dice.py`.

Commands:

- Redraw everything without rolling: `python3 game/dice.py --render`
- Start over: delete `game/state.json`, then run `--render`
- Run the tests: `python3 -m unittest discover game`

## Notes

- The roll happens on GitHub's servers with Python's `secrets` module, so nobody can pick their number.
- If two people roll at the same moment, the second roll starts over from the newest state and rolls again, so no roll is lost.
- Each roll adds one commit to your profile repo. Your contribution graph only counts commits by your account, not the bot's.
