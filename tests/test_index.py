import unittest

from helpers import INDEX, RepoTestCase, run_tool

HEAD = "| Record | Issue / PR | Summary |\n| --- | --- | --- |\n"
BASE_INDEX = f"""# Verification evidence index

Intro.

## November 2026

{HEAD}| [2026-11-01-old](2026-11-01-old/README.md) | #1 | Kept exactly \\| as written |

## October 2026

{HEAD}| [2026-10-01-old](2026-10-01-old/) | — | Hand written |
| [undated-old](undated-old/) | — | Linked: [nested](linked-in-summary/README.md) |

## Related reports

Prose.

{HEAD}| [Report](../gone.md) | — | Outside |

## Retired experiment records

{HEAD}| [retired-raw](retired-raw/) | — | Retired |
"""
LISTED = ("2026-11-01-old", "2026-10-01-old", "undated-old", "retired-raw")


class IndexTool(RepoTestCase):
    def setUp(self):
        super().setUp()
        self.write("records/README.md", BASE_INDEX)
        for name in LISTED:
            self.write(f"records/{name}/log.txt")

    def replace_index(self, text):
        self.write("records/README.md", text)
        for name in LISTED:
            (self.repo / f"records/{name}/log.txt").unlink()

    def run_index(self, *args, expect=0):
        result = run_tool(INDEX, *args, cwd=self.repo)
        self.assertEqual(result.returncode, expect, result.stderr)
        return result

    def text(self):
        return (self.repo / "records/README.md").read_text(encoding="utf-8")

    def table_rows(self, section):
        text = self.text().split(f"## {section}\n", 1)[1].split("\n## ", 1)[0]
        return [line for line in text.splitlines() if line.startswith("| [")]

    def test_complete_index_is_untouched(self):
        self.commit()
        self.run_index("--check")
        self.run_index()
        self.assertEqual(self.text(), BASE_INDEX)

    def test_row_goes_on_top_of_its_month(self):
        self.write("records/2026-11-02-new/README.md", "# New record (#42, #7) | piped\n")
        self.commit()
        self.run_index()
        self.assertEqual(self.table_rows("November 2026"), [
            "| [2026-11-02-new](2026-11-02-new/README.md) | #7, #42 | "
            "New record (#42, #7) \\| piped |",
            "| [2026-11-01-old](2026-11-01-old/README.md) | #1 | Kept exactly \\| as written |",
        ])

    def test_only_additions(self):
        self.write("records/2026-11-02-new/README.md", "# New\n")
        self.write("records/2026-09-02-older/README.md", "# Older\n")
        self.write("records/2027-01-02-newer/README.md", "# Newer\n")
        self.commit()
        self.run_index()
        # Dropping the added lines must give back the original file exactly.
        added = ("## January 2027", "## September 2026", "| [2026-11-02-new]", "| [2026-09-02-older]",
                 "| [2027-01-02-newer]")
        lines = self.text().split("\n")
        for heading in ("## January 2027", "## September 2026"):
            start = lines.index(heading)
            end = lines.index("| --- | --- | --- |", start)
            del lines[start:end + 3]
        kept = [line for line in lines if not line.startswith(added)]
        self.assertEqual("\n".join(kept), BASE_INDEX)

    def test_check_reports_and_changes_nothing(self):
        self.write("records/2026-11-02-new/README.md", "# New\n")
        self.commit()
        result = self.run_index("--check", expect=1)
        self.assertIn("2026-11-02-new", result.stderr)
        self.assertEqual(self.text(), BASE_INDEX)

    def test_idempotent(self):
        self.write("records/2026-11-02-new/README.md", "# New\n")
        self.write("records/2026-12-02-new/README.md", "# New\n")
        self.commit()
        self.run_index()
        first = self.text()
        self.run_index("--check")
        self.run_index()
        self.assertEqual(self.text(), first)

    def test_new_sections_are_newest_first_before_non_month_sections(self):
        self.write("records/2027-01-02-a/README.md", "# A\n")
        self.write("records/2026-12-02-b/README.md", "# B\n")
        self.write("records/2026-09-02-c/README.md", "# C\n")
        self.commit()
        self.run_index()
        headings = [line for line in self.text().splitlines() if line.startswith("## ")]
        self.assertEqual(headings, [
            "## January 2027", "## December 2026", "## November 2026", "## October 2026",
            "## September 2026", "## Related reports", "## Retired experiment records",
        ])
        section = self.text().split("## September 2026\n", 1)[1].split("## Related", 1)[0]
        self.assertEqual(section, f"\n{HEAD}| [2026-09-02-c](2026-09-02-c/README.md) | — | C |\n\n")

    def test_several_rows_in_one_month_are_newest_first(self):
        self.write("records/2026-11-02-a/README.md", "# A\n")
        self.write("records/2026-11-03-b/README.md", "# B\n")
        self.commit()
        self.run_index()
        names = [row.split("]")[0][3:] for row in self.table_rows("November 2026")]
        self.assertEqual(names, ["2026-11-03-b", "2026-11-02-a", "2026-11-01-old"])

    def test_single_file_records(self):
        self.write("records/2026-11-02-note.md", "intro\n\n# Note title #55\n")
        self.write("records/2026-11-02-data-77.json", "{}\n")
        self.write("records/2026-11-02-shot.png", "x")
        self.commit()
        self.run_index()
        rows = self.table_rows("November 2026")
        self.assertIn("| [2026-11-02-note.md](2026-11-02-note.md) | #55 | Note title #55 |", rows)
        self.assertIn("| [2026-11-02-data-77.json](2026-11-02-data-77.json) | #77 | — |", rows)
        self.assertIn("| [2026-11-02-shot.png](2026-11-02-shot.png) | — | — |", rows)

    def test_issue_number_sources(self):
        cases = {
            "2026-11-02-multihead-380": ("# Title", "#380"),
            "2026-11-02-fix-5": ("# Fix for #5 and #1234", "#5, #1234"),
            "2026-11-02-v26.1105.3906-acceptance": ("# Acceptance", "—"),
            "2026-11-02-v26.1105.3906": ("# Acceptance", "—"),
            "2026-11-02-blockers-299e4b29": ("# Blockers", "—"),
            "2026-11-02-anchors": ("# See page.html#12 and C#7", "—"),
        }
        for name, (title, _) in cases.items():
            self.write(f"records/{name}/README.md", f"{title}\n")
        self.commit()
        self.run_index()
        rows = "\n".join(self.table_rows("November 2026"))
        for name, (title, issues) in cases.items():
            with self.subTest(name=name):
                self.assertIn(f"| [{name}]({name}/README.md) | {issues} | {title[2:]} |", rows)

    def test_title_is_never_truncated(self):
        title = "T" * 500
        self.write("records/2026-11-02-long/README.md", f"# {title}\n")
        self.commit()
        self.run_index()
        self.assertIn(f"| {title} |", self.text())

    def test_directory_without_readme_or_title(self):
        self.write("records/2026-11-02-plain/log.txt")
        self.write("records/2026-11-03-untitled/README.md", "no title\n")
        self.commit()
        self.run_index()
        rows = self.table_rows("November 2026")
        self.assertIn("| [2026-11-02-plain](2026-11-02-plain/) | — | — |", rows)
        self.assertIn("| [2026-11-03-untitled](2026-11-03-untitled/README.md) | — | — |", rows)

    def test_undated_entries_get_their_own_section_after_the_months(self):
        self.write("records/no-date-here/README.md", "# Title\n")
        self.write("records/2026-13-01-bad-month/README.md", "# Title\n")
        self.commit()
        self.run_index()
        headings = [line for line in self.text().splitlines() if line.startswith("## ")]
        self.assertEqual(headings[2:4], ["## Undated", "## Related reports"])
        self.assertEqual(len(self.table_rows("Undated")), 2)

    def test_link_in_a_summary_does_not_count_as_indexed(self):
        self.write("records/linked-in-summary/README.md", "# Now listed\n")
        self.commit()
        self.run_index("--check", expect=1)

    def test_a_retired_or_nested_link_counts_as_indexed(self):
        self.write("records/retired-raw/extra.txt")
        self.commit()
        self.run_index("--check")

    def test_section_at_end_of_file(self):
        self.replace_index("# Index\n\nIntro.\n")
        self.write("records/2026-11-02-new/README.md", "# New\n")
        self.commit()
        self.run_index()
        self.assertEqual(self.text(), (
            "# Index\n\nIntro.\n\n## November 2026\n\n"
            f"{HEAD}| [2026-11-02-new](2026-11-02-new/README.md) | — | New |\n"
        ))

    def test_month_heading_without_a_table_gets_one(self):
        self.replace_index("# Index\n\n## November 2026\n\n## Related\n")
        self.write("records/2026-11-02-new/README.md", "# New\n")
        self.commit()
        self.run_index()
        self.assertEqual(self.table_rows("November 2026"),
                         ["| [2026-11-02-new](2026-11-02-new/README.md) | — | New |"])
        self.run_index("--check")

    def test_missing_index_exits_2(self):
        self.write("records/2026-11-02-new/README.md", "# New\n")
        self.commit()
        (self.repo / "records/README.md").unlink()
        self.run_index(expect=2)

    def test_uncommitted_records_are_not_seen(self):
        self.commit()
        self.write("records/2026-11-02-new/README.md", "# New\n")
        self.run_index("--check")

    def test_works_in_a_sparse_blobless_clone(self):
        self.write("records/2026-11-02-new/README.md", "# New\n")
        self.commit()
        self.git("config", "uploadpack.allowFilter", "true")
        clone = self.scratch / "clone"
        self.git("clone", "-q", "--filter=blob:none", "--no-checkout",
                 f"file://{self.repo}", str(clone), cwd=self.scratch)
        self.git("sparse-checkout", "set", "--no-cone", "/*", "!/records/*", "/records/README.md",
                 cwd=clone)
        self.git("checkout", "-q", "main", cwd=clone)
        self.assertFalse((clone / "records/2026-11-02-new").exists())
        result = run_tool(INDEX, cwd=clone)
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (clone / "records/README.md").read_text(encoding="utf-8")
        self.assertIn("| [2026-11-02-new](2026-11-02-new/README.md) | — | New |", text)
        # Only the README it needed was downloaded.
        missing = self.git("rev-list", "--objects", "--all", "--missing=print", cwd=clone)
        unrelated = self.git("rev-parse", "HEAD:records/retired-raw/log.txt")
        self.assertIn(f"?{unrelated}", missing)


if __name__ == "__main__":
    unittest.main()
