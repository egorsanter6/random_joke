import logging
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver

logger = logging.getLogger('users')
@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    logger.info(f"User {user.username} logged in successfully")

@receiver(user_login_failed)
def log_login_failed(sender, credentials, request, **kwargs):
    username = credentials.get('username', 'unknown')
    logger.warning(f"Failed login attempt for username: {username}")