# SmartOps Teams Connector

Minimal Frappe Helpdesk connector for the standalone [SmartOps Teams Bridge](https://github.com/ealecho/smartops_teams_bridge).

It preserves Helpdesk's normal **Reply** action for Microsoft Teams-linked tickets, sends those replies through the bridge, and leaves ordinary email tickets unchanged.

## Frappe Cloud installation

1. Add this repository as a private app in Frappe Cloud.
2. Install it on the site that already has Frappe Helpdesk.
3. Open **SmartOps Teams Connector Settings**.
4. Enter the bridge URL and the bridge's `CONNECTOR_TOKEN`, enable the connector, and save.

The bridge creates the required read-only fields on `HD Ticket` through this app's install/migrate hook.

## Bench installation

```bash
bench get-app https://github.com/ealecho/smartops_teams_connector
bench --site <site> install-app smartops_teams_connector
bench --site <site> migrate
```

Requires Frappe Helpdesk on Frappe v15.
