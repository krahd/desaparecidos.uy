from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from desaparecidos.refusal_paradata import (
    applicable_refusal_ids,
    load_refusal_paradata,
    output_sidecar_provenance,
    render_refusal_paradata,
    sha256_file,
    validate_output_sidecar_provenance,
    validate_refusal_paradata,
)


def test_canonical_refusal_policy_has_stable_unique_identifiers() -> None:
    policy = load_refusal_paradata()
    ids = [record["id"] for record in policy["refusals"]]

    assert policy["policy_id"] == "memorial-refusals-2026-01"
    assert len(ids) == len(set(ids))
    assert "generative-facial-completion" in ids
    assert applicable_refusal_ids(policy, "seguimos-buscando") == [
        "generative-facial-completion",
        "biometric-identification",
        "anticipatory-traversal-assembly",
    ]


def test_tracked_public_render_matches_policy() -> None:
    policy = load_refusal_paradata()
    policy_path = Path("config/refusal-paradata.json")
    expected = render_refusal_paradata(
        policy,
        access="public",
        policy_sha256=sha256_file(policy_path),
    )
    assert Path("doc/refusal-paradata.md").read_text(encoding="utf-8") == expected


def test_refusal_validator_rejects_missing_fields_and_unstable_ids() -> None:
    missing = deepcopy(load_refusal_paradata())
    del missing["refusals"][0]["decision_basis"]["evidence"]
    with pytest.raises(ValueError, match="decision_basis.evidence"):
        validate_refusal_paradata(missing)

    unstable = deepcopy(load_refusal_paradata())
    unstable["refusals"][0]["id"] = "Generative Facial Completion"
    with pytest.raises(ValueError, match="stable lower-case"):
        validate_refusal_paradata(unstable)

    duplicate = deepcopy(load_refusal_paradata())
    duplicate["refusals"][1]["id"] = duplicate["refusals"][0]["id"]
    with pytest.raises(ValueError, match="duplicate refusal id"):
        validate_refusal_paradata(duplicate)


def test_public_render_omits_restricted_records() -> None:
    policy = deepcopy(load_refusal_paradata())
    restricted = deepcopy(policy["refusals"][0])
    restricted["id"] = "restricted-curatorial-decision"
    restricted["access"] = "restricted"
    policy["refusals"].append(restricted)

    public = render_refusal_paradata(policy, access="public")
    curatorial = render_refusal_paradata(policy, access="restricted")

    assert "restricted-curatorial-decision" not in public
    assert "Restricted records omitted: 1" in public
    assert "restricted-curatorial-decision" in curatorial


def test_sidecar_provenance_records_policy_commit_and_manifest_hashes(tmp_path) -> None:
    targets = tmp_path / "targets.csv"
    sources = tmp_path / "places.csv"
    targets.write_text("id\nexample\n", encoding="utf-8")
    sources.write_text("id\nsource\n", encoding="utf-8")

    provenance = output_sidecar_provenance(
        "estan-en-todas-partes",
        {"target_manifest": targets, "source_manifest": sources},
    )
    sidecar = {**provenance, "artwork": "estan-en-todas-partes"}
    validate_output_sidecar_provenance(sidecar)

    manifests = {
        record["role"]: record for record in provenance["runtime_provenance"]["input_manifests"]
    }
    assert provenance["sidecar_schema"] == "desaparecidos.uy/output-sidecar/3.0"
    assert provenance["runtime_provenance"]["git_commit"]
    assert manifests["target_manifest"]["sha256"] == sha256_file(targets)
    assert manifests["source_manifest"]["sha256"] == sha256_file(sources)

    missing_role = deepcopy(sidecar)
    missing_role["runtime_provenance"]["input_manifests"] = [
        manifests["target_manifest"]
    ]
    with pytest.raises(ValueError, match="source_manifest"):
        validate_output_sidecar_provenance(missing_role)

    sidecar["runtime_provenance"]["working_tree_dirty"] = True
    with pytest.raises(ValueError, match="clean working tree"):
        validate_output_sidecar_provenance(sidecar, require_clean_runtime=True)

    sidecar["refusal_policy"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="refusal policy provenance"):
        validate_output_sidecar_provenance(sidecar)
