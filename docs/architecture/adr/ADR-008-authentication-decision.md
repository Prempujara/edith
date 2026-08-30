# ADR-008 — Authentication Strategy: Deferred for Local MVP

**Author:** Mannan Shah (System Designer & Solutions Architect)  
**Date:** August 30, 2026  
**Status:** PROPOSED — REQUIRES TEAM APPROVAL  

---

## 1. Context
Production SaaS applications require user authentication (OAuth2, JWT, Auth0). We must decide whether to implement authentication for the EDITH college MVP under tight Sprint 1/2 timelines and zero budget.

---

## 2. Decision
We **defer user authentication for the local MVP release**. The local REST API gateway operates as an open local interface (`http://localhost:8000`) without mandatory authentication headers.

---

## 3. Rationale
1. **Focus on Core SPM Value:** The primary goal of EDITH is multi-agent task execution, controlled tool execution, and live orchestration—not user access control management.
2. **Eliminates Unnecessary Friction:** Avoids login screen bottlenecks, token expiration bugs, and session state overhead during live college grading presentations.
3. **Future Extension Boundary:** API routes can easily incorporate authentication dependency injection in future sprints if authentication becomes required.

---

## 4. Consequences
* **Positive:** Reduced code surface area, zero login setup, faster development velocity.
* **Negative:** Suitable only for local single-user or trusted local network development environments.
