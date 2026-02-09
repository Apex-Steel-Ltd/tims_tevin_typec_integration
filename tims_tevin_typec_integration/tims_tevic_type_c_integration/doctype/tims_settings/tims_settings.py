# Copyright (c) 2024, Navari Ltd and contributors
# For license information, please see license.txt
import frappe
from frappe.email.queue import flush
from frappe.model.document import Document
from ...tasks.tasks import get_eod_records, resend_invoices


class TIMSSettings(Document):
    # TODO: Provide link to Branch
    
    def validate(self) -> None:
        if self.server_address:
            if not self.server_address.startswith("http"):
                # WARNING: Prepend http for now as hostname is IP address
                self.server_address = f"http://{self.server_address}"
            if not self.server_address.endswith("/api"):
                self.server_address = f"{self.server_address}/api"

    def on_update(self) -> None:
        if self.has_value_changed("flush_email_frequency"):
            if self.flush_email_frequency:
                # Get the job name first using db.get_value
                job_name = frappe.db.get_value(
                    "Scheduled Job Type",
                    {"method": ["like", f"%email%{flush.__name__}%"]},
                    "name"
                )
                
                if job_name:
                    # Now get the document
                    flush_emails_task = frappe.get_doc("Scheduled Job Type", job_name)
                    flush_emails_task.frequency = self.flush_email_frequency
                    if self.flush_email_frequency == "Cron":
                        flush_emails_task.cron_format = self.flush_email_cron
                    flush_emails_task.save()

        if self.has_value_changed("eod_fetch_frequency"):
            if self.eod_fetch_frequency:
                # Get the job name first
                job_name = frappe.db.get_value(
                    "Scheduled Job Type",
                    {"method": ["like", f"%{get_eod_records.__name__}%"]},
                    "name"
                )
                
                if job_name:
                    # Now get the document
                    eod_fetch_task = frappe.get_doc("Scheduled Job Type", job_name)
                    eod_fetch_task.frequency = self.eod_fetch_frequency
                    if self.eod_fetch_frequency == "Cron":
                        eod_fetch_task.cron_format = self.eod_cron
                    eod_fetch_task.save()

        if self.has_value_changed("resend_invoices_frequency"):
            if self.resend_invoices_frequency:
                # Get the job name first
                job_name = frappe.db.get_value(
                    "Scheduled Job Type",
                    {"method": ["like", f"%{resend_invoices.__name__}%"]},
                    "name"
                )
                
                if job_name:
                    # Now get the document
                    resend_invoices_task = frappe.get_doc("Scheduled Job Type", job_name)
                    resend_invoices_task.frequency = self.resend_invoices_frequency
                    if self.resend_invoices_frequency == "Cron":
                        resend_invoices_task.cron_format = self.resend_invoices_cron
                    resend_invoices_task.save()