# VideoAutomater — Git & Development Workflow (V1.0)

## 1. Principles & Branching Strategy

VideoAutomater uses a strict **GitHub Feature-Branch Model**.
- The `main` branch is protected and contains production-ready releases.
- Direct commits to `main` are prohibited.
- Every deliverable feature, fix, or improvement must be developed in a dedicated branch, thoroughly tested, and merged only after review.

### Branch Naming Conventions
```text
feat/<feature-slug>        # New user-facing or runtime features
fix/<bug-slug>            # Bug fixes and patches
refactor/<component-slug> # Code restructuring without functional change
test/<test-slug>          # Test framework or test suite additions
docs/<documentation-slug> # Documentation and architectural specifications
infra/<infra-slug>        # CI/CD, Docker, Cloud Run, Cloud Scheduler
chore/<chore-slug>        # Dependencies, scaffolding, project setup
```

Examples:
- `chore/project-bootstrap`
- `feat/content-research-agent`
- `feat/scriptwriting-agent`
- `feat/video-production-engine`
- `feat/video-quality-checker`
- `feat/agent-control-center`
- `feat/publishing-framework`

---

## 2. Feature Development Lifecycle

1. **Baseline Alignment**: Ensure local `main` is synchronized with remote `origin/main`.
2. **Branch Creation**:
   ```bash
   git checkout -b feat/my-new-feature
   ```
3. **Incremental Commits**: Commit logical, clean increments with descriptive Conventional Commit messages:
   ```bash
   git commit -m "feat(research): implement topic scoring matrix and eligibility gates"
   ```
4. **Automated Testing**: Run full test suites locally prior to pushing:
   ```bash
   pytest tests/
   ```
5. **Pushing Remote**:
   ```bash
   git push -u origin feat/my-new-feature
   ```
6. **Pull Request Creation**:
   - Create PR against `main`.
   - Provide summary of changes, data contract updates, test execution proof.
   - Verify all GitHub Actions checks pass.
7. **Director Approval & Merge**: Merge into `main` after explicit Content Director sign-off.

---

## 3. Security & Secret Safeguards

- Never commit secrets, credentials, OAuth tokens, private keys, or API tokens.
- Large media assets (`.mp4`, `.wav`, raw video dumps) are excluded via `.gitignore`.
- All credentials reside in environment variables or Google Secret Manager.
- Use `.env.example` as a template for required configurations.

---

## 4. Parallel Development with Git Worktrees

When multiple development agents work concurrently on isolated components without dirtying working trees:
```bash
git worktree add ../VideoAutomater-research feat/content-research-agent
git worktree add ../VideoAutomater-media feat/video-production-engine
```
Agents must coordinate shared interface definitions in `docs/DATA_CONTRACTS.md` before coding dependent logic.
