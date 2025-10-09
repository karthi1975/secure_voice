# Claude Code Rules for secure_voice Project

## Deployment Rules

**CRITICAL: Do NOT run deployment commands unless explicitly instructed by the user.**

### Prohibited Actions Without Explicit Permission:
- ❌ `git push` - Do NOT push to git
- ❌ `railway up` - Do NOT deploy to Railway
- ❌ Any command that triggers deployment

### Required Behavior:
- ✅ Always wait for explicit user command: "git push" or "railway up"
- ✅ Ask for permission before deploying
- ✅ Never assume deployment should happen automatically

### Reason:
Multiple simultaneous deployments cause conflicts and long build times. User controls when deployments happen.

---

**Last Updated:** 2025-10-09
