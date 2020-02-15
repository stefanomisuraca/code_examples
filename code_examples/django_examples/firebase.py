import firebase_admin as fb
from firebase_admin import messaging
from django.conf import settings
import logging
import random

logger = logging.getLogger('project_name')


class Firebase:
    """Wrapper for Firebase services."""

    def __init__(self):
        """Set initals settings."""
        self.messaging = fb.messaging
        try:
            self.default_app = fb.initialize_app()
        except ValueError:
            self.default_app = fb.get_app()

    def send_message(self, data, notification_data, condition="", tag=0, topic=None, priority="high"): #noqa
        """
        Send message to specific device.
        Args:
            data (dict): Data to be sent internally
            notification_data (dict): Contains 'title' and 'body', will be shown to the user. #noqa
            tag (str/int): An id used for grouping notifications.
            topic (str): Used to send notifications to specifics user/users

        Raises:
            RuntimeError: ValueError

        Returns:
            response: A notification response from FCM
        """
        assert isinstance(data, dict), "data parameter is not dict"
        assert isinstance(notification_data, dict), "custom_data parameter is not dict" #noqa
        # ------ANDROID CONFIG------
        android_notification_data = {

            "tag": f"scan_id_{tag}"
        }
        android_notification = self.messaging.AndroidNotification(
            **android_notification_data
        )
        android = self.messaging.AndroidConfig(
            priority=priority,
            notification=android_notification
        )

        # ------APSN CONFIG------

        aps_data_config = {
            "thread_id": f"user_id_{tag}"
        }

        aps_data = self.messaging.Aps(
            **aps_data_config
        )
        apns_payload = self.messaging.APNSPayload(
            aps=aps_data
        )
        apns = self.messaging.APNSConfig(
            payload=apns_payload,
            headers={
                "apns-collapse-id": f"user_id_{tag}",
                "apns-priority": "5" if priority == "normal" else "10"
            }
        )
        # ----------------------------
        notification = self.messaging.Notification(
            **notification_data
        )
        if condition:
            message = self.messaging.Message(
                data=data,
                android=android,
                apns=apns,
                notification=notification,
                condition=condition
            )
        else:
            message = self.messaging.Message(
                data=data,
                android=android,
                apns=apns,
                notification=notification,
                topic=topic
            )
        response = self.messaging.send(message)
        return response
