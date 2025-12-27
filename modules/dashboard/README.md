
# DevShield-AI Dashboard & Backend

> _"See your team's security at a glance. Manage users, policies, and analytics—all in one place."_

This dashboard is part of the [DevShield-AI](../../README.md) suite, providing a web-based UI and backend API for visualizing and managing secret detection, risk metrics, users, and policies.

## Folder Structure
```
dashboard/
├── app.py                # Flask backend server with API and dashboard
├── templates/
│   └── index.html        # Dashboard UI (HTML)
├── static/
│   ├── css/
│   │   └── style.css     # Dashboard styles
│   └── js/
│       └── dashboard.js  # Dashboard interactivity
└── README.md             # Documentation and instructions
```


---

## What It Does

- **Web dashboard**: total secrets blocked, secret type breakdown, risk score charts, timeline/activity feed
- **Backend API**: receives and serves data from Developer Guard & AI Risk Engine
- **User & policy management**: add users, set policies, view analytics
- **Demo-ready**: comes with mock/sample dataset, ready for real integration

---

## Getting Started

```sh
cd dashboard_web
python app.py
# Visit http://localhost:5050 for analytics and admin tools
```

---

## Integration & Extending

- Connects with all DevShield-AI clients (VS Code, browser, CLI, backend)
- Ready for Azure deployment and team onboarding
- See [DevShield-AI main README](../../README.md) for full-stack integration

---

**See your security story. [Learn more about DevShield-AI →](../../README.md)**
