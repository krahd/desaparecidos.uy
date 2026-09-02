from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Literal, Mapping

from .paths import PROJECT_ROOT, display_path

REFUSAL_PARADATA_SCHEMA = "desaparecidos.uy/refusal-paradata/1.0"
OUTPUT_SIDECAR_SCHEMA = "desaparecidos.uy/output-sidecar/3.0"
DEFAULT_REFUSAL_PARADATA_PATH = PROJECT_ROOT / "config" / "refusal-paradata.json"

ArtworkId = Literal[
    "todos-somos-familiares",
    "estan-en-todas-partes",
    "seguimos-buscando",
]
AccessLevel = Literal["public", "restricted"]

_ARTWORK_IDS = {
    "todos-somos-familiares",
    "estan-en-todas-partes",
    "seguimos-buscando",
}
_STABLE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_GIT_COMMIT = re.compile(r"^[0-9a-f]{40,64}$")
_REQUIRED_MANIFEST_ROLES = {
    "todos-somos-familiares": {"target_manifest", "source_manifest"},
    "estan-en-todas-partes": {"target_manifest", "source_manifest"},
    "seguimos-buscando": {"target_manifest", "traversal_manifest"},
}


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _required_text_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field} must be a non-empty list")
    result = [_required_text(item, f"{field}[]") for item in value]
    if len(set(result)) != len(result):
        raise ValueError(f"{field} must not contain duplicates")
    return result


def validate_refusal_paradata(value: Any) -> dict[str, Any]:
    """Validate the artwork-specific refusal record without adding an ontology dependency."""
    if not isinstance(value, dict):
        raise ValueError("refusal paradata must be a JSON object")
    if value.get("schema") != REFUSAL_PARADATA_SCHEMA:
        raise ValueError("unsupported refusal paradata schema")
    policy_id = _required_text(value.get("policy_id"), "policy_id")
    if not _STABLE_ID.fullmatch(policy_id):
        raise ValueError("policy_id must be a stable lower-case hyphenated identifier")
    refusals = value.get("refusals")
    if not isinstance(refusals, list) or not refusals:
        raise ValueError("refusals must be a non-empty list")

    seen_ids: set[str] = set()
    for index, refusal in enumerate(refusals):
        prefix = f"refusals[{index}]"
        if not isinstance(refusal, dict):
            raise ValueError(f"{prefix} must be an object")
        refusal_id = _required_text(refusal.get("id"), f"{prefix}.id")
        if not _STABLE_ID.fullmatch(refusal_id):
            raise ValueError(f"{prefix}.id must be a stable lower-case hyphenated identifier")
        if refusal_id in seen_ids:
            raise ValueError(f"duplicate refusal id: {refusal_id}")
        seen_ids.add(refusal_id)
        if refusal.get("status") != "refused":
            raise ValueError(f"{prefix}.status must be 'refused'")
        scope = _required_text_list(refusal.get("scope"), f"{prefix}.scope")
        unknown_scope = sorted(set(scope) - _ARTWORK_IDS)
        if unknown_scope:
            raise ValueError(f"{prefix}.scope contains unknown artwork ids: {', '.join(unknown_scope)}")
        _required_text(refusal.get("available_operation"), f"{prefix}.available_operation")
        _required_text(refusal.get("relation_refused"), f"{prefix}.relation_refused")
        basis = refusal.get("decision_basis")
        if not isinstance(basis, dict):
            raise ValueError(f"{prefix}.decision_basis must be an object")
        for field in ("purpose", "mandate", "evidence"):
            _required_text(basis.get(field), f"{prefix}.decision_basis.{field}")
        _required_text_list(refusal.get("residual_risks"), f"{prefix}.residual_risks")
        _required_text_list(refusal.get("review_triggers"), f"{prefix}.review_triggers")
        if refusal.get("access") not in {"public", "restricted"}:
            raise ValueError(f"{prefix}.access must be 'public' or 'restricted'")
    return value


def load_refusal_paradata(
    path: str | Path = DEFAULT_REFUSAL_PARADATA_PATH,
) -> dict[str, Any]:
    policy_path = Path(path)
    try:
        value = json.loads(policy_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid refusal paradata JSON: {exc}") from exc
    return validate_refusal_paradata(value)


def applicable_refusal_ids(policy: Mapping[str, Any], artwork: ArtworkId) -> list[str]:
    if artwork not in _ARTWORK_IDS:
        raise ValueError(f"unknown artwork id: {artwork}")
    return [
        str(refusal["id"])
        for refusal in policy.get("refusals", [])
        if isinstance(refusal, dict) and artwork in refusal.get("scope", [])
    ]


def render_refusal_paradata(
    policy: Mapping[str, Any],
    *,
    access: AccessLevel = "public",
    policy_sha256: str | None = None,
) -> str:
    """Render a curatorial Markdown view, filtering restricted records from public output."""
    validate_refusal_paradata(dict(policy))
    if access not in {"public", "restricted"}:
        raise ValueError("access must be 'public' or 'restricted'")
    refusals = [
        refusal
        for refusal in policy["refusals"]
        if access == "restricted" or refusal["access"] == "public"
    ]
    hidden = len(policy["refusals"]) - len(refusals)
    lines = [
        "# Paradata of refusal",
        "",
        "This record documents technically available operations that the artwork deliberately withholds. It distinguishes constitutive boundaries from features that merely have not been implemented.",
        "",
        f"- Schema: `{policy['schema']}`",
        f"- Policy: `{policy['policy_id']}`",
    ]
    if policy_sha256:
        lines.append(f"- Policy SHA-256: `{policy_sha256}`")
    lines.append(f"- Rendering access: `{access}`")
    if hidden:
        lines.append(f"- Restricted records omitted: {hidden}")
    for refusal in refusals:
        basis = refusal["decision_basis"]
        lines.extend([
            "",
            f"## {refusal['id']}",
            "",
            f"Status: `{refusal['status']}`  ",
            f"Access: `{refusal['access']}`  ",
            f"Scope: {', '.join(f'`{item}`' for item in refusal['scope'])}",
            "",
            f"**Available operation:** {refusal['available_operation']}",
            "",
            f"**Relation refused:** {refusal['relation_refused']}",
            "",
            "Decision basis:",
            "",
            f"- Purpose: {basis['purpose']}",
            f"- Mandate: {basis['mandate']}",
            f"- Evidence: {basis['evidence']}",
            "",
            "Residual risks:",
            "",
            *[f"- {item}" for item in refusal["residual_risks"]],
            "",
            "Review triggers:",
            "",
            *[f"- {item}" for item in refusal["review_triggers"]],
        ])
    return "\n".join(lines).rstrip() + "\n"


def _runtime_git_state() -> tuple[str | None, bool | None]:
    try:
        commit = subprocess.run(
            ["git", "-C", str(PROJECT_ROOT), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        dirty = bool(subprocess.run(
            ["git", "-C", str(PROJECT_ROOT), "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        return None, None
    return commit, dirty


def output_sidecar_provenance(
    artwork: ArtworkId,
    input_manifests: Mapping[str, str | Path],
    *,
    policy_path: str | Path = DEFAULT_REFUSAL_PARADATA_PATH,
) -> dict[str, Any]:
    """Build the mandatory refusal and runtime provenance fields for an output sidecar."""
    policy_file = Path(policy_path)
    policy = load_refusal_paradata(policy_file)
    commit, dirty = _runtime_git_state()
    manifests = []
    for role, path_value in sorted(input_manifests.items()):
        path = Path(path_value)
        if not path.exists() or not path.is_file():
            raise ValueError(f"input manifest is missing for {role}: {path}")
        manifests.append({
            "role": role,
            "path": display_path(path),
            "sha256": sha256_file(path),
        })
    return {
        "sidecar_schema": OUTPUT_SIDECAR_SCHEMA,
        "refusal_policy": {
            "schema": policy["schema"],
            "policy_id": policy["policy_id"],
            "sha256": sha256_file(policy_file),
            "applicable_refusal_ids": applicable_refusal_ids(policy, artwork),
        },
        "runtime_provenance": {
            "git_commit": commit,
            "working_tree_dirty": dirty,
            "input_manifests": manifests,
        },
    }


def validate_output_sidecar_provenance(
    sidecar: Any,
    *,
    policy_path: str | Path = DEFAULT_REFUSAL_PARADATA_PATH,
    require_clean_runtime: bool = False,
) -> dict[str, Any]:
    """Validate mandatory v3 provenance before an output can cross a release gate."""
    if not isinstance(sidecar, dict):
        raise ValueError("output sidecar must be a JSON object")
    if sidecar.get("sidecar_schema") != OUTPUT_SIDECAR_SCHEMA:
        raise ValueError("unsupported or stale output sidecar schema")
    artwork = sidecar.get("artwork")
    if artwork not in _ARTWORK_IDS:
        raise ValueError("output sidecar has an unknown artwork id")

    policy_file = Path(policy_path)
    policy = load_refusal_paradata(policy_file)
    recorded_policy = sidecar.get("refusal_policy")
    if not isinstance(recorded_policy, dict):
        raise ValueError("output sidecar has no refusal policy provenance")
    expected_policy = {
        "schema": policy["schema"],
        "policy_id": policy["policy_id"],
        "sha256": sha256_file(policy_file),
        "applicable_refusal_ids": applicable_refusal_ids(policy, artwork),
    }
    if recorded_policy != expected_policy:
        raise ValueError("output sidecar refusal policy provenance does not match the policy record")

    runtime = sidecar.get("runtime_provenance")
    if not isinstance(runtime, dict):
        raise ValueError("output sidecar has no runtime provenance")
    commit = runtime.get("git_commit")
    if not isinstance(commit, str) or not _GIT_COMMIT.fullmatch(commit):
        raise ValueError("output sidecar has no valid runtime commit")
    if runtime.get("working_tree_dirty") not in {True, False}:
        raise ValueError("output sidecar has no working-tree state")
    if require_clean_runtime and runtime["working_tree_dirty"]:
        raise ValueError("publication requires an output rendered from a clean working tree")
    manifests = runtime.get("input_manifests")
    if not isinstance(manifests, list) or not manifests:
        raise ValueError("output sidecar has no input-manifest hashes")
    roles: set[str] = set()
    for record in manifests:
        if not isinstance(record, dict):
            raise ValueError("output sidecar input-manifest record must be an object")
        role = _required_text(record.get("role"), "input manifest role")
        _required_text(record.get("path"), f"input manifest {role} path")
        digest = record.get("sha256")
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            raise ValueError(f"input manifest {role} has no valid SHA-256 digest")
        if role in roles:
            raise ValueError(f"duplicate input manifest role: {role}")
        roles.add(role)
    missing_roles = sorted(_REQUIRED_MANIFEST_ROLES[artwork] - roles)
    if missing_roles:
        raise ValueError(
            "output sidecar is missing required input-manifest roles: "
            + ", ".join(missing_roles)
        )
    return sidecar
