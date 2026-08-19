import frappe
from frappe import _
from helpdesk.helpdesk.doctype.hd_ticket.hd_ticket import HDTicket
from helpdesk.utils import is_agent


class TeamsHDTicket(HDTicket):
    @frappe.whitelist()
    def reply_via_agent(
        self,
        message: str,
        from_email: dict | None = None,
        to: str | None = None,
        cc: str | None = None,
        bcc: str | None = None,
        attachments: list[str] = [],
    ):
        if not self.is_teams_ticket:
            return super().reply_via_agent(message, from_email, to, cc, bcc, attachments)
        if not is_agent():
            frappe.throw(_("You are not permitted to reply as an agent"), frappe.PermissionError)
        if attachments:
            frappe.throw(_("Attachments are not supported for Teams tickets yet"))

        communication = frappe.get_doc(
            {
                "doctype": "Communication",
                "communication_type": "Communication",
                "communication_medium": "Chat",
                "sent_or_received": "Sent",
                "subject": f"Re: {self.subject}",
                "sender": frappe.session.user,
                "recipients": self.raised_by,
                "content": message,
                "status": "Linked",
                "reference_doctype": "HD Ticket",
                "reference_name": self.name,
            }
        ).insert(ignore_permissions=True)
        frappe.enqueue(
            "smartops_teams_connector.ticket.send_to_teams",
            queue="short",
            enqueue_after_commit=True,
            communication_id=communication.name,
        )
        return communication.name


def send_to_teams(communication_id: str):
    import requests

    communication = frappe.get_doc("Communication", communication_id)
    ticket = frappe.get_doc("HD Ticket", communication.reference_name)
    settings = frappe.get_single("SmartOps Teams Connector Settings")
    if not settings.enabled:
        frappe.throw(_("SmartOps Teams Connector is disabled"))

    user_name = frappe.db.get_value("User", communication.sender, "full_name") or communication.sender
    try:
        response = requests.post(
            f"{settings.bridge_url.rstrip('/')}/connector/reply",
            headers={
                "Authorization": f"Bearer {settings.get_password('bridge_token')}",
                "Content-Type": "application/json",
            },
            json={
                "ticket_id": ticket.name,
                "communication_id": communication.name,
                "agent_name": user_name,
                "content": communication.content,
                "team_id": ticket.teams_team_id,
                "channel_id": ticket.teams_channel_id,
                "root_message_id": ticket.teams_root_message_id,
            },
            timeout=20,
        )
        response.raise_for_status()
    except Exception:
        frappe.log_error(
            title=f"Teams reply failed: ticket {ticket.name}",
            message=frappe.get_traceback(),
        )
        comment = frappe.get_doc(
            {
                "doctype": "HD Ticket Comment",
                "reference_ticket": ticket.name,
                "commented_by": "Administrator",
                "content": _("The latest reply could not be delivered to Microsoft Teams. Check the Error Log."),
            }
        )
        comment.insert(ignore_permissions=True)
        raise
