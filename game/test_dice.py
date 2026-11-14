"""Tests for the duck race rules. Run with: python3 -m unittest discover game"""

import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import dice

DAY = dt.date(2026, 3, 2)


class RollTest(unittest.TestCase):
    def setUp(self):
        self.state = dice.fresh_state()
        self.day = DAY
        patches = [
            mock.patch.object(dice, "today", lambda: self.day),
            mock.patch.object(dice.secrets, "randbelow", lambda n: self.die - 1),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.die = 1

    def roll(self, team, user, die=1):
        self.die = die
        return dice.roll(self.state, team, user)

    def test_roll_moves_duck_and_scores(self):
        ok, comment = self.roll("shades", "ann", die=3)
        self.assertTrue(ok)
        self.assertEqual(self.state["positions"], {"shades": 3, "tophat": 0})
        # +1 for the roll, +1 for day one of a streak
        self.assertEqual(self.state["players"]["ann"]["points"], 2)
        self.assertIn("#1", comment)

    def test_special_squares_move_the_duck(self):
        self.roll("shades", "ann", die=4)  # bread, +2
        self.assertEqual(self.state["positions"]["shades"], 6)
        self.roll("shades", "bob", die=1)  # 7 is a bug, -3
        self.assertEqual(self.state["positions"]["shades"], 4)

    def test_a_duck_far_behind_gets_a_catch_up_boost(self):
        self.state["positions"] = {"shades": 8, "tophat": 2}
        _, comment = self.roll("tophat", "ann", die=3)  # 6 behind: 3 + 1
        self.assertEqual(self.state["positions"]["tophat"], 6)
        self.assertIn("catching up", comment)
        self.roll("tophat", "bob", die=2)  # only 2 behind now: no boost
        self.assertEqual(self.state["positions"]["tophat"], 8)
        self.roll("shades", "cat", die=2)  # the leader never gets it
        self.assertEqual(self.state["positions"]["shades"], 10)

    def test_cannot_roll_twice_in_a_row_same_day(self):
        self.roll("shades", "ann")
        before = json.dumps(self.state, sort_keys=True)
        ok, comment = self.roll("shades", "ann")
        self.assertFalse(ok)
        self.assertIn("just rolled", comment)
        self.assertEqual(json.dumps(self.state, sort_keys=True), before)

    def test_can_roll_again_the_next_day_even_if_nobody_else_did(self):
        self.roll("shades", "ann")
        self.day = DAY + dt.timedelta(days=1)
        ok, _ = self.roll("shades", "ann")
        self.assertTrue(ok)

    def test_team_is_locked_for_the_round(self):
        self.roll("shades", "ann")
        self.roll("tophat", "bob")
        ok, comment = self.roll("tophat", "ann")
        self.assertFalse(ok)
        self.assertIn("team 🕶️ shades", comment)
        self.assertEqual(self.state["crew"], {"shades": ["ann"], "tophat": ["bob"]})

    def test_team_lock_lifts_after_the_round(self):
        self.state["positions"]["shades"] = 19
        self.roll("shades", "ann")
        self.assertEqual(self.state["round"], 2)
        self.roll("shades", "bob")
        ok, _ = self.roll("tophat", "ann")
        self.assertTrue(ok)

    def test_winning_pays_the_whole_crew_and_resets(self):
        self.roll("shades", "ann")
        self.roll("tophat", "cat")
        self.state["positions"]["shades"] = 18
        self.roll("shades", "bob", die=6)  # overshoots, clamps to the finish
        players = self.state["players"]
        self.assertEqual(players["ann"]["points"], 2 + dice.POINTS_WIN)
        self.assertEqual(players["bob"]["points"], 2 + dice.POINTS_WIN)
        self.assertEqual(players["cat"]["points"], 2)
        self.assertEqual(self.state["wins"], {"shades": 1, "tophat": 0})
        self.assertEqual(self.state["positions"], {"shades": 0, "tophat": 0})
        self.assertEqual(self.state["crew"], {"shades": [], "tophat": []})

    def test_streak_pays_once_a_day_and_caps(self):
        expected = 0
        for offset in range(7):
            self.day = DAY + dt.timedelta(days=offset)
            self.roll("shades", "ann")
            expected += 1 + min(offset + 1, dice.STREAK_CAP)
            self.roll("tophat", "bob")
            self.roll("shades", "ann")  # second roll of the day: no streak bonus
            expected += 1
            self.state["positions"] = {"shades": 0, "tophat": 0}
        self.assertEqual(self.state["players"]["ann"]["points"], expected)
        self.assertEqual(self.state["players"]["ann"]["streak"], 7)

    def test_streak_resets_after_a_missed_day(self):
        self.roll("shades", "ann")
        self.day = DAY + dt.timedelta(days=2)
        self.roll("shades", "ann")
        self.assertEqual(self.state["players"]["ann"]["streak"], 1)
        self.day = DAY + dt.timedelta(days=5)
        self.assertEqual(dice.live_streak(self.state["players"]["ann"]), 0)

    def test_leaderboard_orders_by_points(self):
        self.state["players"] = {
            "low": {**dice.new_player(), "points": 1},
            "high": {**dice.new_player(), "points": 9},
            "mid": {**dice.new_player(), "points": 5},
        }
        self.assertEqual([name for name, _ in dice.leaderboard(self.state)], ["high", "mid", "low"])


class FilesTest(unittest.TestCase):
    """Runs the script end to end against a throwaway copy of the files."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / "game").mkdir()
        (self.root / "README.md").write_text(f"hi\n\n{dice.START}\nold\n{dice.END}\n\nbye\n", encoding="utf-8")
        self.comment = self.root / "comment.md"
        for name, value in {
            "GAME": self.root / "game",
            "STATE_PATH": self.root / "game" / "state.json",
            "README_PATH": self.root / "README.md",
        }.items():
            p = mock.patch.object(dice, name, value)
            p.start()
            self.addCleanup(p.stop)

    def run_issue(self, title, user):
        env = {"ISSUE_TITLE": title, "ISSUE_USER": user, "COMMENT_PATH": str(self.comment), "REPO": "me/me"}
        with mock.patch.dict("os.environ", env), mock.patch("sys.argv", ["dice.py"]):
            dice.main()
        return self.comment.read_text(encoding="utf-8")

    def test_a_roll_writes_every_output(self):
        comment = self.run_issue("dice|roll|shades", "ann")
        self.assertIn("you rolled", comment)
        readme = (self.root / "README.md").read_text(encoding="utf-8")
        self.assertTrue(readme.startswith("hi\n") and readme.endswith("bye\n"))
        self.assertIn("[@ann](https://github.com/ann)", readme)
        self.assertNotIn("old", readme)
        for name in ["board.svg", "duck.svg", "roll-shades.svg", "roll-tophat.svg", "duck-shades.svg", "duck-tophat.svg",
                     "link-portfolio.svg", "link-linkedin.svg"]:
            svg = (self.root / "game" / name).read_text(encoding="utf-8")
            self.assertTrue(svg.startswith("<svg"), name)
            self.assertNotIn("<script", svg)
            self.assertNotIn("http://", svg.replace("http://www.w3.org/2000/svg", ""))
            self.assertNotIn("https://", svg)
        self.assertEqual(json.loads(dice.STATE_PATH.read_text())["total_rolls"], 1)

    def test_everyone_is_on_the_full_leaderboard(self):
        state = dice.fresh_state()
        state["players"] = {f"user{i:02d}": {**dice.new_player(), "points": 50 - i, "rolls": 1} for i in range(14)}
        dice.save_state(state)
        comment = self.run_issue("dice|roll|shades", "newbie")
        readme = (self.root / "README.md").read_text(encoding="utf-8")
        full = (self.root / "game" / "leaderboard.md").read_text(encoding="utf-8")
        self.assertIn("@user09", readme)
        self.assertNotIn("@user10", readme)  # the README stops at the top 10
        self.assertIn("full leaderboard</a> (15 players)", readme)
        for name in ["user00", "user13", "newbie"]:
            self.assertIn(f"[@{name}]", full)
        self.assertIn("**#15** of 15", comment)
        self.assertIn("behind user13", comment)
        self.assertNotIn("@user13", comment)  # no pings

    def test_bad_titles_and_bots_change_nothing(self):
        for title, user in [("dice|roll|nope", "ann"), ("dice|roll|shades", "evil[bot]"), ("dice|roll|shades", "a](x)")]:
            comment = self.run_issue(title, user)
            self.assertIn("doesn't look like a roll", comment)
            self.assertFalse(dice.STATE_PATH.exists())

    def test_old_state_files_are_migrated(self):
        old = {"positions": {"shades": 5, "tophat": 3}, "wins": {"shades": 1, "tophat": 0}, "round": 2,
               "last_roller": "ann", "recent": [], "rollers": {"ann": 4, "bob": 2}, "total_rolls": 6}
        dice.STATE_PATH.write_text(json.dumps(old), encoding="utf-8")
        self.run_issue("dice|roll|tophat", "bob")
        state = json.loads(dice.STATE_PATH.read_text())
        self.assertEqual(state["players"]["ann"]["points"], 4)
        self.assertEqual(state["players"]["bob"]["rolls"], 3)
        self.assertNotIn("rollers", state)
        self.assertEqual(state["crew"]["tophat"], ["bob"])

    def test_render_only_keeps_state(self):
        with mock.patch("sys.argv", ["dice.py", "--render"]):
            dice.main()
        self.assertEqual(json.loads(dice.STATE_PATH.read_text()), dice.fresh_state())


if __name__ == "__main__":
    unittest.main()
