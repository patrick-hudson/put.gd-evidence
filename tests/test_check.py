import os
import tempfile
import unittest
from pathlib import Path

from helpers import CHECK, RepoTestCase, run_tool

README = "# Record title\n\nTested on host f44, GNOME Wayland, build abc123.\n"
LONG_BODY = "x" * 80
ZERO = "0" * 40
GOOD = "2026-11-05-good-record"


class RecordCommand(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.scratch = Path(scratch.name)
        self.record = self.scratch / GOOD
        self.record.mkdir()
        (self.record / "README.md").write_text(README)
        (self.record / "log.txt").write_text("log\n")

    def problems(self, *args, path=None, expect=1):
        result = run_tool(CHECK, "record", path or self.record, *args)
        self.assertEqual(result.returncode, expect, result.stderr)
        return result.stderr.splitlines()

    def test_valid_record(self):
        self.assertEqual(self.problems(expect=0), [])

    def test_name_defaults_to_basename_with_trailing_slash_or_dot(self):
        self.problems(path=f"{self.record}/", expect=0)
        result = run_tool(CHECK, "record", ".", cwd=self.record)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_name_option_overrides_basename(self):
        bad = self.scratch / "Not A Name"
        self.record.rename(bad)
        self.assertIn("name must match", self.problems(path=bad)[0])
        self.problems("--name", GOOD, path=bad, expect=0)
        self.assertIn("name must match", self.problems("--name", "2026-11-05-Upper", path=bad)[0])

    def test_name_rule(self):
        for name in ("record", "2026-11-05", "2026-11-05-", "26-11-05-x", "2026-11-05-Up",
                     "2026-11-05--x", "2026-11-05-a_b", "2026-11-05-a b"):
            with self.subTest(name=name):
                self.assertIn("name must match", self.problems("--name", name)[0])
        for name in ("2026-11-05-a", "2026-11-05-v26.1105.3906-acceptance", "2026-11-05-9"):
            with self.subTest(name=name):
                self.problems("--name", name, expect=0)

    def test_missing_directory(self):
        missing = self.scratch / GOOD / "nope"
        self.assertIn("not a directory", self.problems("--name", GOOD, path=missing)[0])

    def test_readme_required_at_top_level(self):
        (self.record / "README.md").unlink()
        (self.record / "sub").mkdir()
        (self.record / "sub" / "README.md").write_text(README)
        self.assertIn("README.md is missing", self.problems()[0])

    def test_title_required(self):
        for text in ("no title\n", "## second level\n", "#nospace\n", "# \n",
                     "```\n# fenced\n```\n"):
            with self.subTest(text=text):
                (self.record / "README.md").write_text(text)
                self.assertIn("no '# ' title", self.problems()[0])

    def test_title_after_a_fence_counts(self):
        (self.record / "README.md").write_text("```\n# fenced\n```\n\n# Real\n")
        self.problems(expect=0)

    def test_readme_only_record_needs_a_real_body(self):
        (self.record / "log.txt").unlink()
        (self.record / "README.md").write_text("# Title\n\n" + "x" * 79 + "\n")
        self.assertIn("no files besides README.md", self.problems()[0])
        (self.record / "README.md").write_text(f"# Title\n\n{LONG_BODY}\n")
        self.problems(expect=0)

    def test_symlinks_rejected(self):
        (self.record / "link.txt").symlink_to("log.txt")
        (self.record / "linkdir").symlink_to(self.scratch)
        problems = self.problems()
        self.assertEqual(len(problems), 2)
        self.assertTrue(all("symlinks are not allowed" in p for p in problems))

    def test_record_directory_symlink_rejected(self):
        link = self.scratch / "2026-11-05-link"
        link.symlink_to(self.record)
        self.assertIn("is a symlink", self.problems(path=link)[0])

    def test_size_limit(self):
        big = self.record / "big.bin"
        with big.open("wb") as handle:
            handle.truncate(50 * 1024 * 1024)
        self.problems(expect=0)
        with big.open("wb") as handle:
            handle.truncate(50 * 1024 * 1024 + 1)
        self.assertIn("over the 50 MiB limit", self.problems()[0])

    def test_forbidden_names(self):
        for name in ("credentials.txt", "creds.txt", ".env", "a.pem", "a.key", "id_rsa",
                     "id_rsa.pub", "id_ed25519", "id_ed25519.pub", "a.kdbx", ".netrc",
                     "a.iso", "a.qcow2", "CREDS.TXT", "A.PEM"):
            with self.subTest(name=name):
                nested = self.record / "deep"
                nested.mkdir(exist_ok=True)
                forbidden = nested / name
                forbidden.write_text("x")
                self.assertIn("forbidden file name", self.problems()[0])
                forbidden.unlink()

    def test_bytecode_rejected(self):
        cache = self.record / "__pycache__"
        cache.mkdir()
        self.assertIn("Python bytecode", self.problems()[0])
        cache.rmdir()
        pyc = self.record / "a.pyc"
        pyc.write_bytes(b"x")
        self.assertIn("Python bytecode", self.problems()[0])

    def test_embedded_git_rejected(self):
        (self.record / ".git").mkdir()
        self.assertIn("embedded git data", self.problems()[0])

    def test_one_problem_per_line_including_odd_file_names(self):
        (self.record / "creds.txt").write_text("x")
        (self.record / "new\nline.pem").write_text("x")
        (self.record / "README.md").write_text("no title\n")
        problems = self.problems()
        self.assertEqual(len(problems), 3)
        self.assertTrue(any("new\\nline.pem" in p for p in problems))


class PushCommand(RepoTestCase):
    def setUp(self):
        super().setUp()
        self.write("records/README.md", "# Index\n")
        self.write("records/imported-record/log.txt")
        self.write("records/imported-record/nested/deep.txt", "only here\n")
        self.write("records/2026-10-01-single.json", "{}\n")
        self.imported = self.commit("Import")

    def push(self, base=None, head="HEAD", expect=0, import_commit=None):
        args = ["push", "--head", head, "--import-commit", import_commit or self.imported]
        if base is not None:
            args += ["--base", base]
        result = run_tool(CHECK, *args, cwd=self.repo)
        self.assertEqual(result.returncode, expect, result.stderr)
        return result.stderr.splitlines()

    def add_good_record(self, name=GOOD):
        self.write(f"records/{name}/README.md", README)
        self.write(f"records/{name}/log.txt")

    def test_valid_new_record(self):
        self.add_good_record()
        self.commit()
        self.assertEqual(self.push(self.imported), [])

    def test_empty_range(self):
        self.push(self.imported, self.imported)

    def test_invalid_new_records(self):
        cases = {
            "name": ("records/Bad_Name/README.md", README, "name must match"),
            "readme": ("records/2026-11-05-no-readme/log.txt", "x", "README.md is missing"),
            "title": ("records/2026-11-05-no-title/README.md", "x\n", "no '# ' title"),
            "trivial": ("records/2026-11-05-trivial/README.md", "# T\n", "no files besides"),
            "file": ("records/2026-11-05-stray.md", README, "must be a directory"),
        }
        for label, (path, content, expected) in cases.items():
            with self.subTest(label):
                self.git("reset", "-q", "--hard", self.imported)
                self.git("clean", "-qfd")
                self.write(path, content)
                self.commit()
                problems = self.push(self.imported, expect=1)
                self.assertTrue(any(expected in p for p in problems), problems)

    def test_forbidden_file_in_new_record(self):
        self.add_good_record()
        self.write(f"records/{GOOD}/.env")
        self.commit()
        self.assertIn("forbidden file name", self.push(self.imported, expect=1)[0])

    def test_symlink_and_oversize_in_new_record(self):
        self.add_good_record()
        (self.repo / "records" / GOOD / "link").symlink_to("log.txt")
        with (self.repo / "records" / GOOD / "big.bin").open("wb") as handle:
            handle.truncate(50 * 1024 * 1024 + 1)
        self.commit()
        problems = "\n".join(self.push(self.imported, expect=1))
        self.assertIn("symlinks are not allowed", problems)
        self.assertIn("over the 50 MiB limit", problems)

    def test_file_added_and_removed_inside_the_range_is_still_rejected(self):
        self.add_good_record()
        self.write(f"records/{GOOD}/creds.txt")
        self.commit()
        (self.repo / "records" / GOOD / "creds.txt").unlink()
        self.commit()
        self.assertIn("forbidden file name", self.push(self.imported, expect=1)[0])

    def test_modify_needs_trailer(self):
        self.write("records/imported-record/log.txt", "changed\n")
        bad = self.commit("Change a record")
        problem = self.push(self.imported, expect=1)[0]
        self.assertIn(bad[:12], problem)
        self.assertIn("records/imported-record/log.txt", problem)
        self.assertIn("Evidence-Amend", problem)

    def test_modify_with_trailer_passes(self):
        self.write("records/imported-record/log.txt", "changed\n")
        self.commit("Correct a record\n\nEvidence-Amend: the log had the wrong host")
        self.assertEqual(self.push(self.imported), [])

    def test_trailer_must_be_a_real_trailer_with_a_reason(self):
        messages = (
            "Evidence-Amend: subject only is not a trailer",
            "Fix\n\nEvidence-Amend:",
            "Fix\n\nEvidence-Amend: reason, then more prose\n\nA last paragraph.",
        )
        for message in messages:
            with self.subTest(message=message):
                self.git("reset", "-q", "--hard", self.imported)
                self.write("records/imported-record/log.txt", "changed\n")
                self.commit(message)
                self.push(self.imported, expect=1)

    def test_delete_and_rename_need_trailer(self):
        (self.repo / "records/imported-record/log.txt").unlink()
        self.commit()
        self.assertIn("log.txt", self.push(self.imported, expect=1)[0])

        self.git("reset", "-q", "--hard", self.imported)
        self.git("mv", "records/imported-record/log.txt", "records/imported-record/renamed.txt")
        self.commit()
        self.assertIn("imported-record/log.txt", self.push(self.imported, expect=1)[0])

        self.git("reset", "-q", "--hard", self.imported)
        self.git("mv", "records/imported-record/log.txt", "records/imported-record/renamed.txt")
        self.commit("Rename\n\nEvidence-Amend: wrong file name")
        self.push(self.imported)

    def test_every_commit_touching_an_existing_file_needs_its_own_trailer(self):
        self.write("records/imported-record/log.txt", "one\n")
        self.commit("First\n\nEvidence-Amend: reason")
        self.write("records/imported-record/log.txt", "two\n")
        second = self.commit("Second, no trailer")
        problems = self.push(self.imported, expect=1)
        self.assertEqual(len(problems), 1)
        self.assertIn(second[:12], problems[0])

    def test_index_is_exempt(self):
        self.write("records/README.md", "# Index\n\nmore\n")
        self.commit("Index")
        self.assertEqual(self.push(self.imported), [])

    def test_adding_files_to_an_existing_record_is_allowed(self):
        self.write("records/imported-record/new.txt")
        self.commit()
        self.assertEqual(self.push(self.imported), [])

    def test_files_added_to_an_existing_record_still_meet_the_file_rules(self):
        self.write("records/imported-record/server.key")
        self.commit()
        self.assertIn("forbidden file name", self.push(self.imported, expect=1)[0])

    def test_file_added_and_changed_inside_the_range_needs_no_trailer(self):
        self.add_good_record()
        self.commit()
        self.write(f"records/{GOOD}/log.txt", "changed\n")
        self.commit()
        self.assertEqual(self.push(self.imported), [])

    def test_changes_after_a_previous_push_need_a_trailer(self):
        self.add_good_record()
        published = self.commit("Publish")
        self.write(f"records/{GOOD}/log.txt", "changed\n")
        self.commit("Change")
        self.assertIn(GOOD, self.push(published, expect=1)[0])

    def test_changes_outside_records_are_ignored(self):
        self.write("tools/x.py")
        self.write("creds.txt")
        self.commit()
        self.assertEqual(self.push(self.imported), [])

    def test_missing_zero_and_empty_base_mean_everything_in_head(self):
        self.add_good_record()
        self.commit()
        self.assertEqual(self.push(), [])
        self.assertEqual(self.push(ZERO), [])
        self.assertEqual(self.push(""), [])
        self.write("records/Not_A_Name/README.md", README)
        self.commit()
        for base in (None, ZERO, ""):
            with self.subTest(base=base):
                self.assertIn("Not_A_Name", self.push(base, expect=1)[0])

    def test_imported_records_are_exempt_from_name_and_readme_only(self):
        self.assertEqual(self.push(ZERO), [])
        # A record present at the import commit keeps the exemption when re-added.
        (self.repo / "records/imported-record/log.txt").unlink()
        (self.repo / "records/imported-record/nested/deep.txt").unlink()
        self.commit("Remove\n\nEvidence-Amend: test")
        removed = self.git("rev-parse", "HEAD")
        self.write("records/imported-record/again.txt")
        self.commit()
        self.assertEqual(self.push(removed), [])

    def test_unexempted_names_fail_when_the_import_commit_does_not_list_them(self):
        (self.repo / "seed").write_text("x")
        self.git("checkout", "-q", "--orphan", "other")
        self.git("rm", "-rqf", "records")
        other = self.commit("No records yet")
        self.git("checkout", "-q", "main")
        problems = self.push(ZERO, expect=1, import_commit=other)
        self.assertTrue(any("imported-record" in p and "name must match" in p for p in problems))
        self.assertTrue(any("2026-10-01-single.json" in p and "must be a directory" in p
                            for p in problems))

    def test_merge_counts_only_changes_of_its_own(self):
        self.add_good_record()
        self.commit("Publish on main")
        self.git("checkout", "-q", "-b", "side", self.imported)
        self.add_good_record("2026-11-05-other")
        self.commit("Publish on side")
        self.git("checkout", "-q", "main")
        self.git("merge", "-q", "--no-edit", "side")
        self.assertEqual(self.push(self.imported), [])

    def test_evil_merge_needs_a_trailer(self):
        self.git("checkout", "-q", "-b", "side")
        self.write("side.txt")
        self.commit("Side")
        self.git("checkout", "-q", "main")
        self.write("main.txt")
        self.commit("Main")
        self.git("merge", "-q", "--no-commit", "--no-ff", "side")
        self.write("records/imported-record/log.txt", "evil\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "Merge")
        problems = self.push(self.imported, expect=1)
        self.assertIn("imported-record/log.txt", problems[0])

    def test_unknown_commits_exit_2(self):
        self.push("0123456789" * 4, expect=2)
        self.push(self.imported, "0123456789" * 4, expect=2)
        self.push(self.imported, import_commit="0123456789" * 4, expect=2)

    def test_not_a_repository_exits_2(self):
        result = run_tool(CHECK, "push", "--head", "HEAD", cwd=self.scratch)
        self.assertEqual(result.returncode, 2)

    def test_real_import_commit_is_the_default(self):
        result = run_tool(CHECK, "push", "--head", "HEAD", cwd=self.repo)
        self.assertEqual(result.returncode, 2)
        self.assertIn("874703b35562c732268c6fe0bc9b42614ffda928", result.stderr)

    def test_works_in_a_sparse_blobless_clone(self):
        self.add_good_record()
        self.write(f"records/{GOOD}/creds.txt")
        self.commit()
        self.git("config", "uploadpack.allowFilter", "true")
        clone = self.scratch / "clone"
        self.git("clone", "-q", "--filter=blob:none", "--no-checkout",
                 f"file://{self.repo}", str(clone), cwd=self.scratch)
        result = run_tool(CHECK, "push", "--base", self.imported, "--head", "origin/main",
                          "--import-commit", self.imported, cwd=clone)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("forbidden file name", result.stderr)
        self.assertNotIn("README.md", result.stderr)
        # Blobs outside the range were not downloaded.
        missing = self.git("rev-list", "--objects", "--all", "--missing=print", cwd=clone)
        unrelated = self.git("rev-parse", f"{self.imported}:records/imported-record/nested/deep.txt")
        self.assertIn(f"?{unrelated}", missing)


if __name__ == "__main__":
    unittest.main()
