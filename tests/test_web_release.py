"""Exercise publishing guards against manual runs and partial desktop releases."""

from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

JOBS = yaml.safe_load(Path(".github/workflows/release.yml").read_text())["jobs"]
PUBLISH_JOBS = (
    "release",
    "publish-itch",
    "publish-web",
    "attach-web",
    "attach-installer",
)


def allowed(
    job,
    event="push",
    ref="refs/tags/v0.3.0",
    release="success",
    web="success",
    canceled=False,
):
    expression = JOBS[job]["if"].removeprefix("${{").removesuffix("}}")
    expression = (
        expression.replace("&&", " and ")
        .replace("||", " or ")
        .replace("!", " not ")
        .strip()
    )
    context = dict(
        github=SimpleNamespace(event_name=event, ref=ref),
        needs=SimpleNamespace(
            web=SimpleNamespace(result=web),
            release=SimpleNamespace(result=release),
            installer=SimpleNamespace(result="success"),
        ),
        cancelled=lambda: canceled,  # codespell:ignore cancelled
        startsWith=lambda value, prefix: value.startswith(prefix),
    )
    return eval(expression, {"__builtins__": {}}, context)


@pytest.mark.parametrize("job", PUBLISH_JOBS)
@pytest.mark.parametrize("ref", ["refs/heads/main", "refs/tags/v0.3.0"])
def test_manual_runs_never_publish(job, ref):
    assert not allowed(job, event="workflow_dispatch", ref=ref)


@pytest.mark.parametrize("job", PUBLISH_JOBS)
def test_version_tag_push_can_publish(job):
    assert allowed(job)
    assert not allowed(job, ref="refs/heads/main")


@pytest.mark.parametrize(
    "result",
    ["skipped", "failure", "cancelled"],  # codespell:ignore cancelled
)
def test_web_attachment_needs_a_successful_desktop_release(result):
    assert allowed("attach-web")
    assert not allowed("attach-web", release=result)
    assert not allowed("attach-web", web="failure")
    assert not allowed("attach-web", canceled=True)


@pytest.mark.parametrize("job", ["release", "publish-itch"])
def test_desktop_release_jobs_download_only_the_desktop_zips(job):
    """The web zip and the installer have their own artifacts and attach jobs; a
    plain download-everything here would put them into the desktop release twice."""
    download = next(
        step
        for step in JOBS[job]["steps"]
        if step.get("uses", "").startswith("actions/download-artifact")
    )
    assert download["with"]["pattern"] == "hunted-*"


def test_installer_script_and_workflow_agree_on_names():
    script = Path("packaging/hunted.iss").read_text(encoding="utf-8")
    assert "OutputBaseFilename=hunted-windows-setup" in script
    assert r'Source: "..\dist\hunted\*"' in script
    upload = next(
        step
        for step in JOBS["installer"]["steps"]
        if step.get("uses", "").startswith("actions/upload-artifact")
    )
    assert upload["with"]["path"] == "installer-out/hunted-windows-setup.exe"
    assert Path("packaging/icon.ico").is_file()
