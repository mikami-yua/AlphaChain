"""
Email notification module
"""
from .email_notifier import EmailNotifier, create_email_notifier_from_config

__all__ = ["EmailNotifier", "create_email_notifier_from_config"]
