import json

from datetime import datetime, timedelta, timezone

from flask import (
    Blueprint,
    request,
    jsonify,
    url_for,
    session,
    redirect,
    render_template
)

from flask_cors import CORS
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
    create_access_token,
    get_jwt,
    JWTManager
)

from app.persistence.smtp import send_confirm_url, send_reset_password_url
from app.persistence.oauth2 import oauth2
from app.application.jwt import add_token_to_blocklist, is_token_blocklisted
from app.application.auth.anonym import anonym_auth
from app.application.auth.google import google_auth
from app.application.user import delete_user as delete_user_entitie
from app.application.auth.email import (
    email_auth, validate_email, validate_password
)

jwt = JWTManager()
cors = CORS()
api_v1 = Blueprint('api_v1', __name__)


@api_v1.route("/sign-in/email", methods=["POST"])
def email_sign_in():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    access_token, refresh_token, user_id, exp_time = email_auth.authorize(
        email, password)

    if not access_token or not user_id:
        return jsonify(msg="Bad email or password"), 401

    return jsonify(
        user_id=user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=exp_time.isoformat()
    ), 200


@api_v1.route('/sign-in/check', methods=['POST'])
@jwt_required()
def sign_in_check():
    current_user = get_jwt_identity()
    user_id = request.json.get('user_id', None)
    if not user_id:
        return jsonify(msg="Missing user_id"), 400
    if current_user != user_id:
        return jsonify(msg="Unauthorized"), 401

    return jsonify(signed=True), 200


@api_v1.route("/sign-up/email", methods=["POST"])
def email_sign_up():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    sign_in_url = request.json.get('sign_in_url', None)

    if not email or not password:
        return jsonify(msg="Missing email or password"), 400

    is_email_valid, error_message = validate_email(email)
    if not is_email_valid:
        return jsonify(msg=error_message), 400

    is_password_valid, error_message = validate_password(password)
    if not is_password_valid:
        return jsonify(msg=error_message), 400

    confirm_url, status_code = email_auth.register(email, password)
    if status_code == 400:
        return jsonify(msg="Missing email or password"), 400

    if status_code == 409:
        return jsonify(msg="Email already registered"), 409

    if sign_in_url:
        confirm_url += f"?sign_in_url={sign_in_url}"

    send_confirm_url(email, confirm_url)

    message = "User created. Please check your email to confirm registration."
    return jsonify(msg=message), 201


@api_v1.route('/sign-up/email/verification/<token>', methods=['GET'])
def email_verification(token):
    sign_in_url = request.args.get('sign_in_url', None)
    status_code = email_auth.confirm_email(token)
    if status_code == 400:
        return render_template('confirmation.html', success=False)

    return render_template(
        'confirmation.html',
        success=True,
        sign_in_url=sign_in_url
    )


@api_v1.route("/sign-out", methods=["DELETE"])
@jwt_required()
def modify_token():
    add_token_to_blocklist(get_jwt()["jti"])
    return jsonify(msg="JWT revoked")


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    return is_token_blocklisted(jti)


@api_v1.route('/email/password/forgot', methods=['POST'])
def email_forgot_password():
    email = request.json.get('email', None)
    if not email:
        return jsonify(msg="Missing email"), 400

    reset_url, status_code = email_auth.forgot_password(email)
    if status_code == 404:
        return jsonify(msg="Email not found"), 404

    send_reset_password_url(email, reset_url)

    return jsonify(msg="Password reset email sent. Check your inbox."), 200


@api_v1.route('/email/password/reset/<token>', methods=['POST'])
def email_reset_password(token):
    new_password = request.json.get('password', None)
    if not new_password:
        return jsonify(msg="Missing new password"), 400

    status_code = email_auth.reset_password(token, new_password)
    if status_code == 400:
        return jsonify(msg="The reset link is expired."), 400

    message = "Your password has been updated. You may now log in."
    return jsonify(msg=message), 200


@api_v1.route('/sign-up/anonym', methods=['POST'])
def anonym_sign_up():
    access_token, refresh_token, user_id, exp_time = anonym_auth.register()
    return jsonify(
        user_id=user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=exp_time.isoformat()
    ), 201


@api_v1.route('/sign-up/google', methods=['GET'])
def google_sign_up():
    session['redirect_url'] = request.args.get('redirect_url', None)
    redirect_uri = url_for(
        'api_v1.google_authentication', _external=True)
    return oauth2.google.authorize_redirect(redirect_uri)


@api_v1.route('/sign-up/google/auth', methods=['GET'])
def google_authentication():
    access_token, refresh_token, user_id, exp_time = google_auth.register()

    session['jwt_access_credentials'] = json.dumps({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user_id,
        "expires_at": exp_time.isoformat()
    })

    redirect_url = session.get('redirect_url', None)
    if not redirect_url:
        return jsonify(msg="Missing redirect URL"), 400

    session.pop('redirect_url', None)

    return redirect(redirect_url, code=302)


@api_v1.route('/one-time/credentials', methods=['GET'])
def get_one_time_credentials():
    credentials = session.pop('jwt_access_credentials', None)
    if not credentials:
        return jsonify(msg="No credentials found"), 404

    return jsonify(credentials), 200


@api_v1.route('/one-time/credentials/page', methods=['GET'])
def one_time_credentials_page():
    return render_template('one_time_redirect.html')


@api_v1.route('/users/<id_hash>/password', methods=['PUT'])
@jwt_required()
def update_password(id_hash):
    current_user = get_jwt_identity()
    if current_user != id_hash:
        return jsonify(msg="Unauthorized"), 401

    new_password = request.json.get('password', None)
    if not new_password:
        return jsonify(msg="Missing new password"), 400

    is_password_valid, error_message = validate_password(new_password)
    if not is_password_valid:
        return jsonify(msg=error_message), 400

    status_code = email_auth.update_password(id_hash, new_password)
    if status_code == 404:
        return jsonify(msg="User does not have the email authentication"), 404

    return jsonify(msg="Password updated"), 200


@api_v1.route('/users/<id_hash>/email', methods=['PUT'])
@jwt_required()
def update_email(id_hash):
    current_user = get_jwt_identity()
    if current_user != id_hash:
        return jsonify(msg="Unauthorized"), 401

    new_email = request.json.get('email', None)
    if not new_email:
        return jsonify(msg="Missing email"), 400

    is_email_valid, error_message = validate_email(new_email)
    if not is_email_valid:
        return jsonify(msg=error_message), 400

    status_code = email_auth.update_email(id_hash, new_email)
    if status_code == 404:
        return jsonify(msg="User does not have the email authentication"), 404

    return jsonify(msg="Email updated"), 200


@api_v1.route('/users/<id_hash>', methods=['DELETE'])
@jwt_required()
def delete_user(id_hash):
    status_code = delete_user_entitie(id_hash)
    if status_code == 404:
        return jsonify(msg="User not found"), 404
    return jsonify(msg="User deleted"), 200


@api_v1.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    expires_in = timedelta(hours=1)

    access_token = create_access_token(
        identity=user_id,
        expires_delta=expires_in
    )

    expiration_time = datetime.now(timezone.utc) + expires_in

    return jsonify(
        access_token=access_token,
        expires_at=expiration_time.isoformat()
    ), 200


@api_v1.route('/admin', methods=['GET'])
def admin():
    return render_template('admin.html')


@api_v1.route('/admin/sign-in', methods=['GET'])
def admin_sign_in():
    return render_template('admin_sign_in.html')


@api_v1.route('/admin/sign-up', methods=['GET'])
def admin_sign_up():
    return render_template('admin_sign_up.html')
