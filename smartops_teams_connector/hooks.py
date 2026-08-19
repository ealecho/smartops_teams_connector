app_name = "smartops_teams_connector"
app_title = "SmartOps Teams Connector"
app_publisher = "ERP Champions"
app_description = "Routes Teams-linked Helpdesk replies through the standalone bridge"
app_email = ""
app_license = "MIT"

required_apps = ["helpdesk"]

after_install = "smartops_teams_connector.setup.install"
after_migrate = "smartops_teams_connector.setup.install"

override_doctype_class = {
    "HD Ticket": "smartops_teams_connector.ticket.TeamsHDTicket",
}
