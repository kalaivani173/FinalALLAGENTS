# Deploy to javacoderepo – Runbook

## Prerequisites

- Change request (CR) with **changeType** = `field-addition` and **currentStatus** = `Approved`.
- **JAVACODEREPO_ROOT** (optional): path to the Java repo. Default: sibling of `aicode` named `javacoderepo`.
- For Git commit/push: set **DEPLOY_GIT_ENABLED=1** (or **DEPLOY_PUSH_TO_GIT=1**). See [Deploy Git integration](#deploy-git-integration).

## How to deploy

1. **Check eligibility:** `GET /npciswitch/deploy/eligibility/{changeId}`  
   Returns `eligible: true` when the CR is field-addition and Approved.

2. **Optional dry-run:** `POST /npciswitch/deploy/{changeId}?dryRun=true`  
   Returns `wouldDeploy` (target paths and whether each would be backed up). No files or Git are modified.

3. **Deploy:** `POST /npciswitch/deploy/{changeId}`  
   Writes approved files to javacoderepo (backing up existing to `*_old.*`). If Git is enabled, commits and optionally pushes.

## Deploy Git integration

- **Enable:** `DEPLOY_GIT_ENABLED=1` or `DEPLOY_PUSH_TO_GIT=1`.
- **Commit only (no push):** `DEPLOY_GIT_COMMIT_ONLY=1`.
- **Branch:** `DEPLOY_GIT_BRANCH=main` (empty = current branch).
- **Remote:** `DEPLOY_GIT_REMOTE=origin`.
- **Commit message:** `DEPLOY_GIT_COMMIT_MESSAGE_TEMPLATE=Deploy field-addition: {changeId}` (placeholders: `{changeId}`, `{timestamp}`).
- **Allow dirty repo:** `DEPLOY_GIT_ALLOW_DIRTY_REPO=1` (default 0 = fail if repo has other uncommitted changes).
- **Timeouts (seconds):** `DEPLOY_GIT_ADD_TIMEOUT`, `DEPLOY_GIT_COMMIT_TIMEOUT`, `DEPLOY_GIT_PUSH_TIMEOUT` (defaults 30, 30, 60).
- **Push retries:** `DEPLOY_GIT_PUSH_RETRIES=2`.

## Resolving errors

- **REPO_DIRTY:** Repo has uncommitted changes outside the files being deployed. Commit or stash them, or set `DEPLOY_GIT_ALLOW_DIRTY_REPO=1`.
- **GIT_PUSH_FAILED:** Push failed (e.g. network, auth, or non-fast-forward). Check remote and branch; push manually from javacoderepo if needed. Deploy itself succeeded; files are written and status is Deployed.
- **GIT_TIMEOUT:** Git command timed out. Increase timeout env vars or check repo size/network.
- **GIT_NOT_FOUND:** `git` not in PATH on the server.
- **BRANCH_NOT_FOUND:** `DEPLOY_GIT_BRANCH` is set but the branch does not exist locally. Create it or leave unset to use current branch.

## Audit log

- **Location:** `aicode/artifacts/deploy_audit.jsonl`  
- One JSON object per line per deploy: `changeId`, `timestamp`, `deployedFiles` (paths), `gitCommitPush` (ok, branch, commitHash, pushed, errorCode, message). No file contents or credentials.

---

## How to test

### 1. Start the orchestrator

From project root:

```bash
cd aicode
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### 2. Manual API checks

Use `http://localhost:8000` as base. Replace `CHG-XXX` with a real change ID that exists in the change-requests store and is Approved with `files` populated.

**Eligibility (unknown change → 404):**

```bash
curl -s http://localhost:8000/npciswitch/deploy/eligibility/CHG-NONE
# Expect: 404
```

**Eligibility (existing CR):**

```bash
curl -s http://localhost:8000/npciswitch/deploy/eligibility/CHG-XXX
# Expect: { "eligible": true/false, "reason": ..., "crStatus": ..., "changeType": ... }
```

**Deploy dry-run (no writes):**

```bash
curl -s -X POST "http://localhost:8000/npciswitch/deploy/CHG-XXX?dryRun=true"
# Expect: { "dryRun": true, "changeId": "CHG-XXX", "wouldDeploy": [...], "errors": [], "javacoderepoRoot": "..." }
```

**Deploy for real (only if CR is Approved and has files):**

```bash
curl -s -X POST http://localhost:8000/npciswitch/deploy/CHG-XXX
# Expect: { "success": true/false, "deployedFiles": [...], "gitCommitPush": { "ok", "message", "branch?", "commitHash?", "pushed?" }, ... }
```

**Idempotency (deploy same again → 409):**

```bash
curl -s -w "\n%{http_code}" -X POST http://localhost:8000/npciswitch/deploy/CHG-XXX
# After first deploy: 200. Second time: 409 "Change already deployed"
```

**PowerShell (Windows):**

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/npciswitch/deploy/eligibility/CHG-XXX" -Method Get
Invoke-RestMethod -Uri "http://localhost:8000/npciswitch/deploy/CHG-XXX?dryRun=true" -Method Post
```

### 3. Automated tests (pytest)

From project root, with the orchestrator running:

```bash
pip install -r tests/requirements.txt
pytest tests/test_deploy_api.py -v
```

Tests cover: eligibility 404, deploy 404, dry-run response shape (when a valid CR exists), and 409 when status is already Deployed. They skip if the server is not reachable.
