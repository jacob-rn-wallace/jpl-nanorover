#!/usr/bin/env python3
"""Render every pending job in docs/render-jobs.md, mark it done, commit and push.   (the render machine's one command)

    python3 hardware/assembly/render_pending.py                 # pull, render all pending jobs, update the table, commit, push
    python3 hardware/assembly/render_pending.py --dry-run       # pull and show what would be rendered, change nothing else
    python3 hardware/assembly/render_pending.py --jobs R1,R2    # render these jobs whatever their status
    python3 hardware/assembly/render_pending.py --no-push       # render and commit, but do not push
    python3 hardware/assembly/render_pending.py --no-commit     # render and update the table, but do not commit (for testing)
    options --samples N and --res WxH override every job's settings (testing only)

What it does, in order: `git pull --rebase`; reads the Jobs table in docs/render-jobs.md (columns: Id, Image, Settings, Expected, Why, Status, Notes); takes the rows whose
Status starts with "pending"; regenerates the strut and wheel meshes if the repository's .venv exists; for each job runs Blender headless (the Metal GPU on a Mac, the CPU elsewhere)
with the job's settings; checks that the image exists and is not blank; sets the row's Status to "done YYYY-MM-DD" and its Notes to the device, the time and the check result;
commits the images and the table and pushes (pulling and retrying if the push is refused). A job that fails stays pending with the error in its Notes.
It does NOT look at the pictures: open the new images once (docs/images/) and, if one is wrong, set its row back to pending with a note.
Settings are read from the Settings cell: environment assignments in backticks (VIEW=hero, LED=on, BEZEL=black, SUFFIX=-lit ...), a size such as 1500x940 and the sample count.
"""
import argparse, datetime, os, platform, re, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JOBS = ROOT / "docs" / "render-jobs.md"
IMAGES = ROOT / "docs" / "images"
STL = ROOT / "hardware" / "assembly" / "out" / "blender"


def sh(cmd, check=True, **kw):
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=check, **kw)


def parse_table(text):
    """Returns (lines, jobs) where jobs maps Id -> dict(line=index, cells=[...])."""
    lines = text.split("\n")
    jobs = {}
    for i, l in enumerate(lines):
        if re.match(r"^\| R\d+ \|", l):
            cells = [c.strip() for c in l.strip().strip("|").split("|")]
            if len(cells) >= 7:
                jobs[cells[0]] = dict(line=i, cells=cells)
    return lines, jobs


def settings_of(cell):
    env = dict(re.findall(r"\b([A-Z_]+)=([^\s,`]+)", cell))
    res = re.search(r"\b(\d{3,4}x\d{3,4})\b", cell)
    nums = re.findall(r"\b(\d+)\s*samples\b", cell) or re.findall(r",\s*(\d+)\s*(?:`|$)", cell) or re.findall(r"\b(\d{2,3})\b(?!x)", cell.split(",")[-1])
    return env, (res.group(1) if res else "1500x940"), (nums[-1] if nums else "96")


def image_name(env):
    return f"rover-{env.get('VIEW', 'hero')}{env.get('SUFFIX', '')}.png"


def blender_binary():
    for cand in (os.environ.get("BLENDER"), "/Applications/Blender.app/Contents/MacOS/Blender", str(Path.home() / "tools/blender-4.5.9-linux-x64/blender")):
        if cand and Path(cand).exists():
            return cand
    sys.exit("Blender not found: set BLENDER to the binary (see docs/blender-render.md)")


def image_check(path):
    try:
        from PIL import Image
        import numpy as np
        a = np.asarray(Image.open(path).convert("L"), dtype=float)
    except Exception as e:                                   # no Pillow or numpy: skip the check
        return True, f"image written (no pixel check: {type(e).__name__})"
    mean, std = a.mean(), a.std()
    if mean < 3 or mean > 250 or std < 2:
        return False, f"image looks blank (mean {mean:.0f}, spread {std:.0f})"
    return True, f"pixel check ok (mean {mean:.0f})"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--jobs"); ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--no-commit", action="store_true"); ap.add_argument("--samples"); ap.add_argument("--res")
    ap.add_argument("--no-pull", action="store_true")
    a = ap.parse_args()

    if not a.no_pull:
        r = sh(["git", "pull", "--rebase", "--autostash"], check=False)
        print((r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else "git pull: done")
        if r.returncode:
            sys.exit("git pull failed:\n" + r.stdout + r.stderr)
    lines, jobs = parse_table(JOBS.read_text())
    wanted = [j.strip() for j in a.jobs.split(",")] if a.jobs else [i for i, j in jobs.items() if j["cells"][5].lower().startswith("pending")]
    unknown = [w for w in wanted if w not in jobs]
    if unknown:
        sys.exit(f"unknown job(s): {unknown}; the table has {list(jobs)}")
    if not wanted:
        print("no pending jobs: nothing to do"); return
    plan = []
    for jid in wanted:
        env, res, samples = settings_of(jobs[jid]["cells"][2])
        plan.append((jid, env, a.res or res, a.samples or samples))
    print("jobs:", "; ".join(f"{jid} ({image_name(env)}, {res}, {samples} samples)" for jid, env, res, samples in plan))
    if a.dry_run:
        return

    blender = blender_binary()
    device = os.environ.get("DEVICE", "gpu" if platform.system() == "Darwin" else "cpu")
    venv_py = ROOT / ".venv" / "bin" / "python"
    if venv_py.exists():
        r = sh([str(venv_py), "hardware/assembly/blender_export.py"], check=False)
        print("meshes regenerated" if r.returncode == 0 else "mesh regeneration failed (using the existing meshes):\n" + (r.stdout + r.stderr)[-400:])
    for f in ("struts.stl", "wheels.stl"):
        if not (STL / f).exists():
            sys.exit(f"missing {STL / f}: create the venv (docs/blender-render.md, 'Setup on an Apple Silicon Mac') or copy the meshes from the other machine")

    today = datetime.date.today().isoformat()
    done, failed, images = [], [], []
    for jid, env, res, samples in plan:
        t = time.time()
        e = dict(os.environ, **env, RES=res, SAMPLES=samples, DEVICE=device)
        r = subprocess.run([blender, "-b", "-P", str(ROOT / "hardware/assembly/blender_render.py")], cwd=ROOT, env=e, text=True, capture_output=True)
        out = r.stdout + r.stderr
        dev = next((l.split(":", 1)[1].strip() for l in out.splitlines() if l.startswith("render device")), "CPU" if device == "cpu" else "unknown device")
        img = IMAGES / image_name(env)
        secs = time.time() - t
        ok, msg = (img.exists() and "wrote" in out, "")
        if ok:
            ok, msg = image_check(img)
        else:
            msg = "no image written: " + " | ".join(l for l in out.splitlines() if "Error" in l or "Traceback" in l)[-200:]
        cells = jobs[jid]["cells"]
        if ok:
            cells[5] = f"done {today}"; cells[6] = f"automatic ({Path(__file__).name}): {dev}, {secs:.0f} s, {samples} samples; {msg}"
            done.append(jid); images.append(img)
        else:
            cells[6] = f"automatic render failed {today}: {msg}"
            failed.append(jid)
        lines[jobs[jid]["line"]] = "| " + " | ".join(cells) + " |"
        print(f"  {jid}: {'done' if ok else 'FAILED'} in {secs:.0f} s on {dev}; {msg}")
        JOBS.write_text("\n".join(lines))                    # save after every job, so a stop part-way loses nothing

    if a.no_commit or not done:
        print("not committing" + (" (nothing rendered)" if not done else " (--no-commit)")); sys.exit(1 if failed else 0)
    sh(["git", "add", "docs/render-jobs.md"] + [str(p.relative_to(ROOT)) for p in images])
    sh(["git", "commit", "-m", f"Renders {', '.join(done)} (automatic, {dev})"])
    if a.no_push:
        print("committed; not pushed (--no-push)")
    else:
        for attempt in range(3):
            r = sh(["git", "push"], check=False)
            if r.returncode == 0:
                print("pushed"); break
            sh(["git", "pull", "--rebase", "--autostash"], check=False)
        else:
            sys.exit("push failed after three tries:\n" + r.stdout + r.stderr)
    if failed:
        print("failed (still pending):", ", ".join(failed)); sys.exit(1)
    print("Done. Open the new images in docs/images/ and check them (the script cannot look at them).")


if __name__ == "__main__":
    main()
