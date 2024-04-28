from flask_mail import Mail, Message


mail = Mail()


def send_confirm_url(email, confirm_url):
    message = Message("Confirm Your Email",
                      sender='auth.api@brevo.com', recipients=[email])
    template = "Please click the following link to confirm your email: {}"
    email_body = template.format(confirm_url)
    message.body = email_body
    mail.send(message)


def send_reset_password_url(email, confirm_url):
    message = Message("Reset Your Password",
                      sender='auth.api@brevo.com', recipients=[email])
    template = "Use the following link to update the password: {}"
    email_body = template.format(confirm_url)
    message.body = email_body
    mail.send(message)
