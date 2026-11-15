"""Duck race for a GitHub profile README.

A visitor opens an issue titled ``dice|roll|<team>``. The GitHub Action runs
this script, which rolls a die, moves that team's duck, scores the player,
redraws the art and rewrites the game section of README.md. The reply for the
issue is written to COMMENT_PATH.

Run with ``--render`` to redraw everything without rolling.
"""

import json
import os
import re
import secrets
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from art import board_svg, button_svg, duck_front_svg, duck_icon_svg, link_button_svg  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GAME = ROOT / "game"
STATE_PATH = GAME / "state.json"
README_PATH = ROOT / "README.md"

DEFAULT_REPO = "DonaldKLee/DonaldKLee"
TRACK_LENGTH = 20
DICE = ["", "⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]

# The cape duck keeps the key "tophat" so roll links people already used keep working.
TEAMS = {
    "shades": {"emoji": "🕶️", "name": "shades", "accessory": "sunglasses"},
    "tophat": {"emoji": "🦸", "name": "cape", "accessory": "cape"},
}

# square -> what happens when a duck lands on it
TILES = {
    4: {"emoji": "🍞", "move": +2, "name": "bread", "story": "found some bread", "icon": "bread"},
    7: {"emoji": "🐛", "move": -3, "name": "bug", "story": "hit a bug", "icon": "bug"},
    11: {"emoji": "🚀", "move": +3, "name": "ship it", "story": "shipped to prod", "icon": "rocket"},
    14: {"emoji": "🌀", "move": -4, "name": "whirlpool", "story": "got spun around by a whirlpool", "icon": "whirlpool"},
    17: {"emoji": "💤", "move": -2, "name": "nap", "story": "dozed off after an all-nighter", "icon": "nap"},
}

# The rounded link buttons under the intro in README.md: file name -> (label, icon)
LINKS = {
    "portfolio": ("Portfolio", "globe"),
    "linkedin": ("LinkedIn", "linkedin"),
}

POINTS_ROLL = 1
POINTS_WIN = 3  # for everyone who rolled for the winning duck that round
STREAK_CAP = 5
CATCH_UP_GAP = 6  # a duck this far behind gets a boost on its rolls
CATCH_UP_BOOST = 1
LEADERBOARD_SIZE = 10
RECENT_SIZE = 5

START, END = "<!-- DICE:START -->", "<!-- DICE:END -->"
TITLE_RE = re.compile(r"^dice\|roll\|(shades|tophat)$")
LOGIN_RE = re.compile(r"^[A-Za-z0-9-]{1,39}$")  # real accounts only; bot logins contain brackets


def today():
    return datetime.now(timezone.utc).date()


def label(team):
    return f"{TEAMS[team]['emoji']} {TEAMS[team]['name']}"


def signed(n):
    return f"+{n}" if n > 0 else f"−{abs(n)}"


def user_link(user):
    return f"[@{user}](https://github.com/{user})"


def roll_link(team, repo):
    title = quote(f"dice|roll|{team}", safe="")
    body = quote(
        "👇 hit the green **Create** button. that's it! No need to edit anything here, close any issues, etc!\n\n"
        "- 🎲 a bot will roll for your duck and reply here within ~30 seconds\n"
        "- 🏁 first duck to the finish wins the round\n"
        f"- 🤝 you're on team {TEAMS[team]['name']} until the round ends",
        safe="",
    )
    return f"https://github.com/{repo}/issues/new?title={title}&body={body}"


# ---------- state ----------

def new_player():
    return {"points": 0, "rolls": 0, "streak": 0, "last_day": None}


def fresh_state():
    return {
        "round": 1,
        "positions": {team: 0 for team in TEAMS},
        "wins": {team: 0 for team in TEAMS},
        "crew": {team: [] for team in TEAMS},  # who rolled for each duck this round
        "last_roller": None,
        "last_roll_day": None,
        "players": {},
        "recent": [],
        "last_roll": None,  # what happened on the latest roll, shown above the buttons
        "total_rolls": 0,
    }


def load_state():
    if not STATE_PATH.exists():
        return fresh_state()
    saved = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    state = {**fresh_state(), **saved}
    # The first version only counted rolls per user; carry those over as points.
    if "rollers" in saved and "players" not in saved:
        state["players"] = {
            user: {**new_player(), "points": n * POINTS_ROLL, "rolls": n}
            for user, n in saved["rollers"].items()
        }
    state.pop("rollers", None)
    state["players"] = {user: {**new_player(), **p} for user, p in state["players"].items()}
    return state


def save_state(state):
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def team_of(state, user):
    """The duck this player is rolling for this round, if they have picked one."""
    return next((team for team, crew in state["crew"].items() if user in crew), None)


def live_streak(player):
    """A streak is only alive if the player rolled today or yesterday."""
    if not player["last_day"]:
        return 0
    last = datetime.fromisoformat(player["last_day"]).date()
    return player["streak"] if today() - last <= timedelta(days=1) else 0


def leaderboard(state):
    return sorted(
        state["players"].items(),
        key=lambda kv: (-kv[1]["points"], -kv[1]["rolls"], kv[0].lower()),
    )


# ---------- rolling ----------

def roll(state, team, user, repo=DEFAULT_REPO):
    """Apply one roll. Returns (state changed?, reply for the issue)."""
    day = today().isoformat()
    owner = repo.split("/")[0]

    picked = team_of(state, user)
    if picked and picked != team:
        return False, (
            f"hey @{user}, you're on team {label(picked)} this round, so no rolling for the other duck. 🦆\n\n"
            f"[roll for {TEAMS[picked]['name']}]({roll_link(picked, repo)}) instead. you can switch sides next round."
        )
    if state["last_roller"] == user and state["last_roll_day"] == day:
        return False, (
            f"hey @{user}, you just rolled! 🎲 give someone else a turn, or come back tomorrow.\n\n"
            f"want it sooner? send [the pond](https://github.com/{owner}) to a friend."
        )

    other = next(t for t in TEAMS if t != team)
    die = secrets.randbelow(6) + 1
    boost = CATCH_UP_BOOST if state["positions"][other] - state["positions"][team] >= CATCH_UP_GAP else 0
    square = min(state["positions"][team] + die + boost, TRACK_LENGTH)
    story = f"rolled {DICE[die]} **{die}** for {label(team)}"
    if boost:
        story += f", plus {boost} for catching up 💨"
    tile = TILES.get(square)
    if tile:
        square = max(0, min(square + tile["move"], TRACK_LENGTH))
        moved = f"went back {abs(tile['move'])}" if tile["move"] < 0 else f"jumped ahead {tile['move']}"
        story += f", {tile['story']} and {moved} ({signed(tile['move'])}) {tile['emoji']}"

    player = state["players"].setdefault(user, new_player())
    earned = [(POINTS_ROLL, "roll")]
    if player["last_day"] != day:
        yesterday = (today() - timedelta(days=1)).isoformat()
        player["streak"] = player["streak"] + 1 if player["last_day"] == yesterday else 1
        player["last_day"] = day
        earned.append((min(player["streak"], STREAK_CAP), f"🔥 day {player['streak']} streak"))

    crew = state["crew"][team]
    if user not in crew:
        crew.append(user)

    state["positions"][team] = square
    state["last_roller"] = user
    state["last_roll_day"] = day
    state["total_rolls"] += 1
    player["rolls"] += 1

    won = square >= TRACK_LENGTH
    if won:
        story += f" and crossed the finish 🏁 **{TEAMS[team]['name']} wins round {state['round']}!**"
        earned.append((POINTS_WIN, "🤝 your duck won"))
        for mate in crew:
            if mate != user and mate in state["players"]:
                state["players"][mate]["points"] += POINTS_WIN
        where = f"everyone on team {TEAMS[team]['name']} gets +{POINTS_WIN}. new round, pick any duck you like."
        state["wins"][team] += 1
        state["round"] += 1
        state["positions"] = {t: 0 for t in TEAMS}
        state["crew"] = {t: [] for t in TEAMS}
    else:
        gap = square - state["positions"][other]
        if gap:
            where = f"{label(team)} is on square {square}/{TRACK_LENGTH}, {abs(gap)} {'ahead of' if gap > 0 else 'behind'} {label(other)}."
        else:
            where = f"{label(team)} is on square {square}/{TRACK_LENGTH}, tied with {label(other)}."

    gained = sum(points for points, _ in earned)
    player["points"] += gained

    stamp = today().strftime("%b %d").lower()
    state["last_roll"] = f"{user_link(user)} {story}"
    state["recent"] = ([f"{stamp} · {user_link(user)} {story}"] + state["recent"])[:RECENT_SIZE]

    ranked = leaderboard(state)
    rank = next(i for i, (name, _) in enumerate(ranked, 1) if name == user)
    chase = ""
    if rank > 1:
        # Plain name, no @, so the player above doesn't get pinged by every reply.
        ahead, ahead_player = ranked[rank - 2]
        behind = ahead_player["points"] - player["points"]
        chase = f", {behind} behind {ahead}" if behind else f", tied with {ahead}"
    breakdown = " · ".join(f"+{points} {why}" for points, why in earned)
    comment = (
        f"🎲 you {story}{'' if won else '!'}\n\n"
        f"**+{gained} points** ({breakdown}) · **{player['points']} total**\n\n"
        f"you're **#{rank}** of {len(ranked)} on the [leaderboard](https://github.com/{repo}/blob/HEAD/game/leaderboard.md){chase}.\n\n"
        f"{where}\n\n"
        f"roll again tomorrow to keep your 🔥 streak going. [see the pond](https://github.com/{owner}) 🦆"
    )
    return True, comment


# ---------- rendering ----------

def board_name(state):
    return f"board-{state['total_rolls']}.svg"


def render_art(state):
    tiles = {square: (tile["icon"], tile["move"]) for square, tile in TILES.items()}
    board = board_svg(state["positions"], TEAMS, tiles, TRACK_LENGTH, "duck race board")
    # A new filename per roll: GitHub caches README images by URL, so a changed
    # query string can be ignored while a brand-new path always loads fresh.
    for old in GAME.glob("board*.svg"):
        old.unlink()
    (GAME / board_name(state)).write_text(board, encoding="utf-8")
    (GAME / "duck.svg").write_text(duck_front_svg(), encoding="utf-8")
    for team, info in TEAMS.items():
        (GAME / f"roll-{team}.svg").write_text(button_svg(f"Roll for {info['name']}", info["accessory"]), encoding="utf-8")
        (GAME / f"duck-{team}.svg").write_text(duck_icon_svg(info["accessory"]), encoding="utf-8")
    for name, (text, icon) in LINKS.items():
        (GAME / f"link-{name}.svg").write_text(link_button_svg(text, icon), encoding="utf-8")


def standings(state):
    """(leading team, trailing team, squares between them)."""
    first, second = sorted(TEAMS, key=lambda team: -state["positions"][team])
    return first, second, state["positions"][first] - state["positions"][second]


def duck_img(team):
    name = TEAMS[team]["name"]
    return f'<img src="game/duck-{team}.svg" height="24" alt="{name} duck"> {name}'


def avatar_src(user):
    """A round GitHub avatar. README markdown can't round images, so wsrv.nl
    applies the circle mask to the GitHub photo. Nothing is saved in the repo."""
    return f"https://wsrv.nl/?url=github.com/{user}.png&w=40&h=40&fit=cover&mask=circle&output=png"


def player_row(place, user, player, extra=""):
    medal = ["🥇", "🥈", "🥉"][place - 1] if place <= 3 else str(place)
    avatar = f'<img src="{avatar_src(user)}" width="20" height="20" alt="">'
    return f"| {medal} | {avatar} {user_link(user)} | **{player['points']}** | {live_streak(player) or '·'} |{extra}"


def render_leaderboard(state, repo):
    """Every player, so anyone can find themselves once they drop out of the top 10."""
    ranked = leaderboard(state)
    rows = [player_row(place, user, p, f" {p['rolls']} |") for place, (user, p) in enumerate(ranked, 1)]
    table = "| | player | pts | 🔥 streak | rolls |\n|:-:|:--|:-:|:-:|:-:|\n" + "\n".join(rows)
    return (
        "# 🏆 duck race leaderboard\n\n"
        f"{len(ranked)} players, {state['total_rolls']} rolls. "
        f"[back to the pond](https://github.com/{repo.split('/')[0]})\n\n"
        f"{table if rows else 'nobody yet. roll once and you are #1 👀'}\n"
    )


def md_inline(text):
    """Links and bold as HTML, for lines inside an HTML block where markdown isn't parsed."""
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)


def render_readme(state, repo):
    lead, trail, gap = standings(state)
    if gap == 0:
        status = "it's a tie. your roll breaks it!"
    else:
        status = f"{duck_img(lead)} is up by {gap}. {duck_img(trail)} needs you!"

    buttons = "&nbsp;&nbsp;".join(
        f'<a href="{roll_link(team, repo)}"><img src="game/roll-{team}.svg" height="46" alt="🎲 roll for {TEAMS[team]["name"]}"></a>'
        for team in TEAMS
    )
    squares = " · ".join(f"{t['emoji']} {t['name']} {signed(t['move'])}" for _, t in sorted(TILES.items()))

    ranked = leaderboard(state)
    rows = [player_row(place, user, p) for place, (user, p) in enumerate(ranked[:LEADERBOARD_SIZE], 1)]
    if rows:
        board = "| | player | pts | 🔥 streak |\n|:-:|:--|:-:|:-:|\n" + "\n".join(rows)
        board += f"\n\n<sub>not in the top {LEADERBOARD_SIZE}? find yourself on the <a href=\"game/leaderboard.md\">full leaderboard</a> ({len(ranked)} players)</sub>"
    else:
        board = "nobody yet. roll once and you're #1 👀"

    recent = "\n".join(f"- {line}" for line in state["recent"]) or "- no rolls yet. be the first!"
    wins = ", ".join(f"{TEAMS[team]['name']} {state['wins'][team]}" for team in TEAMS)

    last = f'\n<p align="center"><sub>last roll: {md_inline(state["last_roll"])}</sub></p>\n' if state.get("last_roll") else ""

    return f"""{START}
<h3 align="center"><img src="game/duck.svg" height="30" alt="🦆"> Duck race · round {state['round']}</h3>

<p align="center">
  <img src="game/{board_name(state)}" alt="duck race board" width="100%">
</p>

<p align="center">{buttons}</p>

<p align="center"><b>{status}</b></p>
{last}
pick a duck and roll. you're on its team until the round ends.

**points**

- 🎲 +{POINTS_ROLL} for every roll
- 🔥 +1 for each day in a row you've rolled, once a day (max +{STREAK_CAP})
- 🤝 +{POINTS_WIN} if your duck wins the round

**squares:** {squares}

💨 a duck that's {CATCH_UP_GAP}+ squares behind gets +{CATCH_UP_BOOST} on every roll.

**🏆 leaderboard**

{board}

<details>
<summary><b>recent rolls</b> · rounds won: {wins}</summary>

{recent}

</details>
{END}"""


def write_outputs(state, repo):
    text = README_PATH.read_text(encoding="utf-8")
    if START not in text or END not in text:
        sys.exit(f"README.md needs {START} and {END} markers")
    before, rest = text.split(START, 1)
    _, after = rest.split(END, 1)
    README_PATH.write_text(before + render_readme(state, repo) + after, encoding="utf-8")
    (GAME / "leaderboard.md").write_text(render_leaderboard(state, repo), encoding="utf-8")
    render_art(state)
    save_state(state)


def main():
    repo = os.environ.get("REPO", DEFAULT_REPO)
    state = load_state()

    if "--render" in sys.argv:
        write_outputs(state, repo)
        return

    title = os.environ.get("ISSUE_TITLE", "").strip().lower()
    user = os.environ.get("ISSUE_USER", "")
    comment_path = Path(os.environ.get("COMMENT_PATH", "comment.md"))

    match = TITLE_RE.match(title)
    if not match or not LOGIN_RE.match(user):
        comment_path.write_text("🤔 that doesn't look like a roll. use the roll buttons on the profile!", encoding="utf-8")
        return

    changed, comment = roll(state, match.group(1), user, repo)
    if changed:
        write_outputs(state, repo)
    comment_path.write_text(comment, encoding="utf-8")


if __name__ == "__main__":
    main()
