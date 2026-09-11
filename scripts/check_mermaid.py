"""Extract mermaid code blocks from Markdown docs and validate they render.

Each fenced ```mermaid block is written to a temp file and compiled with the
mermaid CLI (mmdc). A non-zero mmdc exit code means the diagram is invalid.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MERMAID_BLOCK = re.compile(r"```mermaid\n(.*?)```", re.DOTALL)

DOCS: tuple[str, ...] = (
    "docs/architecture/c4-container.md",
    "docs/architecture/eda-flow.md",
    "docs/architecture/bian-iso20022-mapping.md",
)


def extract_blocks(markdown: str) -> list[str]:
    """Return the mermaid diagram sources found in a Markdown string.

    Args:
        markdown: Full Markdown document content.

    Returns:
        A list of mermaid diagram source strings.
    """
    return [block.strip() for block in MERMAID_BLOCK.findall(markdown)]


def render_block(source: str, mmdc: str) -> subprocess.CompletedProcess[str]:
    """Compile a single mermaid diagram to validate its syntax.

    Args:
        source: The mermaid diagram source.
        mmdc: Path/command used to invoke the mermaid CLI.

    Returns:
        The completed process from the mermaid CLI invocation.
    """
    tmp = Path(tempfile.mkdtemp(prefix="mmd_"))
    try:
        in_path = tmp / "diagram.mmd"
        out_path = tmp / "diagram.svg"
        in_path.write_text(source, encoding="utf-8")
        command = f'{mmdc} -i "{in_path}" -o "{out_path}"'
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=True,
            check=False,
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    """Validate every mermaid block across the architecture docs.

    Returns:
        Process exit code: ``0`` when all diagrams render, ``1`` otherwise.
    """
    root = Path(__file__).resolve().parent.parent
    mmdc = "npx -y @mermaid-js/mermaid-cli@latest"
    failures = 0
    total = 0
    for rel in DOCS:
        blocks = extract_blocks((root / rel).read_text(encoding="utf-8"))
        for index, block in enumerate(blocks):
            total += 1
            result = render_block(block, mmdc)
            if result.returncode != 0:
                failures += 1
                detail = (result.stderr + result.stdout).strip()
                print(f"FAIL {rel} block #{index}:\n{detail}")
            else:
                print(f"OK   {rel} block #{index}")
    print(f"\n{total - failures}/{total} mermaid diagrams valid.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
