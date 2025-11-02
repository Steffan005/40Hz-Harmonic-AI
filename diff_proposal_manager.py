#!/usr/bin/env python3
"""
Diff Proposal Manager - Conscious Veto System
Manages the changes.md approval workflow for agent-proposed modifications
"""

import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class DiffProposalManager:
    """
    Manages agent-proposed code changes via changes.md approval workflow.

    Workflow:
    1. Agent proposes change → write to changes.md
    2. Human reviews → marks [APPLY], [REJECT], or [DEFER]
    3. Orchestrator reads status → executes approved changes only
    """

    def __init__(self, changes_file: str = "changes.md"):
        self.changes_file = Path(changes_file)
        self.proposals = []
        self.stats = {
            "total_proposals": 0,
            "applied": 0,
            "rejected": 0,
            "deferred": 0
        }

    def propose_change(
        self,
        variant_id: str,
        arm: str,
        predicted_delta: float,
        file_path: str,
        old_content: str,
        new_content: str,
        rationale: str
    ) -> str:
        """
        Create a new change proposal and append to changes.md.

        Args:
            variant_id: Unique variant identifier
            arm: Bandit arm that generated this change
            predicted_delta: Predicted improvement score
            file_path: Path to file being modified
            old_content: Original file content
            new_content: Proposed new content
            rationale: Agent's explanation for the change

        Returns:
            Proposal ID
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        proposal_id = f"{variant_id}_{int(time.time())}"

        # Generate unified diff
        diff = self._generate_diff(file_path, old_content, new_content)

        # Create proposal entry
        proposal_entry = f"""
## [PENDING] Proposal ID: {proposal_id}
**Timestamp:** {timestamp}
**Variant ID:** {variant_id}
**Arm:** {arm}
**Predicted ΔScore:** +{predicted_delta:.2f}
**Files Modified:** 1

### File: `{file_path}`

### Diff Preview

```diff
{diff}
```

### Rationale
{rationale}

### Human Decision
- [ ] APPLY - Approve and execute this change
- [ ] REJECT - Reject this change (reason: _____________)
- [ ] DEFER - Review later

**Decision Timestamp:**
**Executed By:**
**Actual ΔScore:** (post-execution measurement)

---

"""

        # Append to changes.md
        with open(self.changes_file, 'a') as f:
            f.write(proposal_entry)

        # Track proposal
        self.proposals.append({
            "id": proposal_id,
            "variant_id": variant_id,
            "arm": arm,
            "predicted_delta": predicted_delta,
            "file_path": file_path,
            "status": "PENDING",
            "timestamp": timestamp
        })

        self.stats["total_proposals"] += 1

        return proposal_id

    def _generate_diff(self, file_path: str, old: str, new: str) -> str:
        """
        Generate unified diff between old and new content.

        Args:
            file_path: Path for diff header
            old: Original content
            new: New content

        Returns:
            Unified diff string
        """
        import difflib

        old_lines = old.splitlines(keepends=True)
        new_lines = new.splitlines(keepends=True)

        diff_lines = list(difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm=''
        ))

        if not diff_lines:
            return "(no changes detected)"

        return '\n'.join(diff_lines)

    def check_approval_status(self, proposal_id: str) -> Tuple[str, Optional[str]]:
        """
        Check if a proposal has been approved/rejected/deferred.

        Reads changes.md and looks for status markers:
        - [APPLY] or [x] APPLY → approved
        - [REJECT] or [x] REJECT → rejected
        - [DEFER] or [x] DEFER → deferred
        - Otherwise → pending

        Args:
            proposal_id: Proposal to check

        Returns:
            (status, reason) tuple where status is APPLY|REJECT|DEFER|PENDING
        """
        if not self.changes_file.exists():
            return ("PENDING", None)

        content = self.changes_file.read_text()

        # Find the proposal section
        if f"Proposal ID: {proposal_id}" not in content:
            return ("PENDING", None)

        # Extract the proposal block
        lines = content.split('\n')
        in_proposal = False
        decision_lines = []

        for line in lines:
            if f"Proposal ID: {proposal_id}" in line:
                in_proposal = True
            elif in_proposal and line.startswith("## ["):
                # Hit next proposal
                break
            elif in_proposal and "Human Decision" in line:
                # Start collecting decision lines
                decision_lines.append(line)
            elif in_proposal and decision_lines and line.strip():
                decision_lines.append(line)

        # Check for status markers
        decision_text = '\n'.join(decision_lines)

        if "[x] APPLY" in decision_text or "[APPLY]" in decision_text.upper():
            return ("APPLY", None)
        elif "[x] REJECT" in decision_text or "[REJECT]" in decision_text.upper():
            # Try to extract reason
            reason = None
            for line in decision_lines:
                if "reason:" in line.lower():
                    reason = line.split("reason:", 1)[1].strip()
                    break
            return ("REJECT", reason)
        elif "[x] DEFER" in decision_text or "[DEFER]" in decision_text.upper():
            return ("DEFER", None)

        return ("PENDING", None)

    def execute_approved_changes(self) -> List[Dict]:
        """
        Scan changes.md for approved changes and execute them.

        Returns:
            List of executed changes with results
        """
        executed = []

        for proposal in self.proposals:
            if proposal["status"] != "PENDING":
                continue

            status, reason = self.check_approval_status(proposal["id"])

            if status == "APPLY":
                # Execute the change
                result = self._apply_change(proposal)
                executed.append({
                    "proposal_id": proposal["id"],
                    "file_path": proposal["file_path"],
                    "result": result,
                    "status": "executed"
                })

                proposal["status"] = "APPLIED"
                self.stats["applied"] += 1

            elif status == "REJECT":
                proposal["status"] = "REJECTED"
                proposal["reject_reason"] = reason
                self.stats["rejected"] += 1

            elif status == "DEFER":
                proposal["status"] = "DEFERRED"
                self.stats["deferred"] += 1

        return executed

    def _apply_change(self, proposal: Dict) -> str:
        """
        Apply an approved change to the filesystem.

        Args:
            proposal: Proposal dict with file_path and content

        Returns:
            Result message
        """
        # NOTE: In production, this would actually write the file
        # For now, we just simulate
        return f"[SIMULATED] Would write to {proposal['file_path']}"

    def get_stats(self) -> Dict:
        """Get approval statistics."""
        acceptance_rate = (
            self.stats["applied"] / max(self.stats["total_proposals"], 1)
        ) * 100 if self.stats["total_proposals"] > 0 else 0.0

        return {
            **self.stats,
            "acceptance_rate": acceptance_rate,
            "pending": self.stats["total_proposals"] - (
                self.stats["applied"] + self.stats["rejected"] + self.stats["deferred"]
            )
        }

    def get_pending_count(self) -> int:
        """Get number of pending proposals."""
        return sum(1 for p in self.proposals if p["status"] == "PENDING")


# Example usage
if __name__ == "__main__":
    manager = DiffProposalManager()

    # Simulate a proposal
    proposal_id = manager.propose_change(
        variant_id="variant_123",
        arm="textgrad",
        predicted_delta=5.2,
        file_path="example.py",
        old_content="def old_function():\n    pass\n",
        new_content="def improved_function():\n    return 42\n",
        rationale="Improved function now returns meaningful value"
    )

    print(f"Created proposal: {proposal_id}")
    print(f"Stats: {manager.get_stats()}")
    print(f"Pending: {manager.get_pending_count()}")
