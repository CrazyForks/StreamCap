from asyncio import create_task

from ..utils.logger import logger
from .notification_service import NotificationService


class MessagePusher:
    def __init__(self, settings):
        self.settings = settings
        self.notifier = NotificationService()

    def is_any_push_channel_enabled(self):
        """Check if any push channel is enabled"""
        push_channels = [
            "dingtalk_enabled",
            "wechat_enabled",
            "bark_enabled",
            "ntfy_enabled",
            "telegram_enabled",
            "email_enabled",
            "serverchan_enabled"
        ]
        
        return any(self.settings.user_config.get(channel) for channel in push_channels)

    @staticmethod
    def should_push_message(settings, recording, check_manually_stopped=False):
        """
        Check if message should be pushed
        """
        if not recording.enabled_message_push:
            return False
            
        user_config = settings.user_config
        
        # Check if global push settings are enabled
        global_push_enabled = (
            user_config.get("stream_start_notification_enabled") or 
            user_config.get("stream_end_notification_enabled") or 
            user_config.get("only_notify_no_record")
        )
        
        if not global_push_enabled:
            return False
            
        # Check if any push platform is enabled
        push_channels = [
            "dingtalk_enabled",
            "wechat_enabled",
            "bark_enabled",
            "ntfy_enabled",
            "telegram_enabled",
            "email_enabled",
            "serverchan_enabled"
        ]
        
        any_channel_enabled = any(user_config.get(channel) for channel in push_channels)
        
        if not any_channel_enabled:
            return False
            
        # Check if manually stopped status is needed
        if check_manually_stopped and recording.manually_stopped:
            return False
            
        return True

    async def push_messages(self, msg_title: str, push_content: str):
        """Push messages to all enabled notification services"""
        if self.settings.user_config.get("dingtalk_enabled"):
            create_task(
                self.notifier.send_to_dingtalk(
                    url=self.settings.user_config.get("dingtalk_webhook_url"),
                    content=push_content,
                    number=self.settings.user_config.get("dingtalk_at_objects"),
                    is_atall=self.settings.user_config.get("dingtalk_at_all"),
                )
            )
            logger.info("Push DingTalk message successfully")

        if self.settings.user_config.get("wechat_enabled"):
            create_task(
                self.notifier.send_to_wechat(
                    url=self.settings.user_config.get("wechat_webhook_url"), title=msg_title, content=push_content
                )
            )
            logger.info("Push Wechat message successfully")

        if self.settings.user_config.get("bark_enabled"):
            create_task(
                self.notifier.send_to_bark(
                    api=self.settings.user_config.get("bark_webhook_url"),
                    title=msg_title,
                    content=push_content,
                    level=self.settings.user_config.get("bark_interrupt_level"),
                    sound=self.settings.user_config.get("bark_sound"),
                )
            )
            logger.info("Push Bark message successfully")

        if self.settings.user_config.get("ntfy_enabled"):
            create_task(
                self.notifier.send_to_ntfy(
                    api=self.settings.user_config.get("ntfy_server_url"),
                    title=msg_title,
                    content=push_content,
                    tags=self.settings.user_config.get("ntfy_tags"),
                    action_url=self.settings.user_config.get("ntfy_action_url"),
                    email=self.settings.user_config.get("ntfy_email"),
                )
            )
            logger.info("Push Ntfy message successfully")

        if self.settings.user_config.get("telegram_enabled"):
            create_task(
                self.notifier.send_to_telegram(
                    chat_id=self.settings.user_config.get("telegram_chat_id"),
                    token=self.settings.user_config.get("telegram_api_token"),
                    content=push_content,
                )
            )
            logger.info("Push Telegram message successfully")

        if self.settings.user_config.get("email_enabled"):
            create_task(
                self.notifier.send_to_email(
                    email_host=self.settings.user_config.get("smtp_server"),
                    login_email=self.settings.user_config.get("email_username"),
                    password=self.settings.user_config.get("email_password"),
                    sender_email=self.settings.user_config.get("sender_email"),
                    sender_name=self.settings.user_config.get("sender_name"),
                    to_email=self.settings.user_config.get("recipient_email"),
                    title=msg_title,
                    content=push_content,
                )
            )
            logger.info("Push Email message successfully")

        if self.settings.user_config.get("serverchan_enabled"):
            create_task(
                self.notifier.send_to_serverchan(
                    sendkey=self.settings.user_config.get("serverchan_sendkey"),
                    title=msg_title,
                    content=push_content,
                    channel=self.settings.user_config.get("serverchan_channel", 9),
                    tags=self.settings.user_config.get("serverchan_tags", "直播通知"),
                )
            )
            logger.info("Push ServerChan message successfully")
