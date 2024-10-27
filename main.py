from discord_webhook import DiscordWebhook
import time
from datetime import datetime
import os
from dotenv import load_dotenv


load_dotenv()
_WEBHOOK_URL = os.getenv("WEBHOOK_URL")
_WEBHOOK_REFRESH_RATE = int(os.getenv("WEBHOOK_REFRESH_RATE"))
_DOWN_CHECK_RATE = int(os.getenv("DOWN_CHECK_RATE"))
_HOSTNAME_PING = os.getenv("HOSTNAME_PING")
_NETWORK_ADMIN = int(os.getenv("NETWORK_ADMIN"))
_MINIMUM_DOWN_TIME = int(os.getenv("MINIMUM_DOWN_TIME"))


def get_ping(hostname: str) -> bool:
    """
    Check if host is up
    :param hostname: Hostname to check
    :return: True if host is up, False if host is down
    """
    import subprocess
    import platform

    try:
        subprocess.check_output(
            "ping -{} 1 {}".format('n' if platform.system().lower() == 'windows' else 'c', hostname), shell=True
        )
    except Exception as e:
        return False

    return True


def send_message(ping_host: str):
    """
    Send message to discord if host is down
    :param ping_host: Hostname to check
    :return: None
    """
    if not get_ping(ping_host):
        time.sleep(_MINIMUM_DOWN_TIME)
        if not get_ping(ping_host):
            webhook = DiscordWebhook(url=_WEBHOOK_URL, content=f"<@{_NETWORK_ADMIN}> {ping_host} is down!")
            webhook.execute()
            down_time = time.time()

            while not get_ping(hostname=ping_host):
                time.sleep(_DOWN_CHECK_RATE)

            up_time = time.time()
            delta_time = up_time - down_time
            webhook = DiscordWebhook(
                url=_WEBHOOK_URL,
                content=f"<@{_NETWORK_ADMIN}> {ping_host} is again up! Estimated downtime: {delta_time} seconds."
            )
            webhook.execute()


def main():
    """
    Main function
    :return: None
    """
    while True:
        send_message(_HOSTNAME_PING)
        time.sleep(_WEBHOOK_REFRESH_RATE)


if __name__ == "__main__":
    main()
