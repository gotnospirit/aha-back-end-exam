from smtplib import SMTP_SSL
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import render_template, url_for
from www.models import User


class Mailer:
    def __init__(self, host: str, port: int, password: str, sender: str, logger) -> None:
        self.host = host
        self.port = port
        self.password = password
        self.sender = sender
        self.logger = logger

    def send_verification(self, user: User) -> bool:
        self.logger.info("send email to <%s>" % user.email)

        message = MIMEMultipart("alternative")
        message["Subject"] = "Email address verification"
        message["From"] = self.sender
        message["To"] = user.email

        nickname = user.nickname
        activate_url = url_for("activate", email=user.email,
                               key=user.activation_key, _external=True)

        text = render_template(
            'email.txt', nickname=nickname, activate_url=activate_url)
        html = render_template(
            'email.html', nickname=nickname, activate_url=activate_url)

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)

        # Create connection with server and send email
        try:
            ctx = ssl.create_default_context()
            with SMTP_SSL(self.host, port=self.port, context=ctx) as server:
                server.login(self.sender, self.password)
                server.sendmail(
                    self.sender, user.email, message.as_string()
                )
                return True
        except Exception as e:
            self.logger.error(e)
            return False
