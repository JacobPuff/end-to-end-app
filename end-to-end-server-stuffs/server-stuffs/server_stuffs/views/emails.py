from pyramid.response import Response
from pyramid.view import view_config
from pyramid import httpexceptions
from datetime import datetime, timedelta
from uuid import uuid4
import json

from ..models import UserModel, ResetTokenModel, VerifyTokenModel
from ..scripts.password_hashing import pwd_context
from ..scripts.utilities import (error_dict, datetime_serializer, send_email, send_verification_email,
                            isEmailBlacklisted, removeEmailLabelIfAny, verifyRecaptchaToken)

removals = ['user_pass']


@view_config(route_name="resettokens")
def resettokens(request):
    if request.method == 'POST':
        body = request.json_body

        if body.get("recaptcha_token") is None and request.recaptchaTestToken is None:
            status_code = httpexceptions.HTTPBadRequest.code
            result = error_dict("api_error", "recaptcha_token is required")
        elif not verifyRecaptchaToken(request):
            status_code = httpexceptions.HTTPBadRequest.code
            result = error_dict("api_error", "recaptcha token is invalid")
        elif body.get("user_email") is None and body.get("resettoken") is None:
            status_code = httpexceptions.HTTPBadRequest.code
            result = error_dict("api_error", "user_email or resettoken is required")
        else:
            if body.get("user_email"):
                user = request.dbsession.query(UserModel)\
                    .filter(UserModel.user_email == removeEmailLabelIfAny(body.get("user_email")).lower())\
                    .one_or_none()
            if body.get("resettoken"):
                resettoken = request.dbsession.query(ResetTokenModel)\
                    .filter(ResetTokenModel.token == body.get("resettoken"))\
                    .one_or_none()
                if resettoken is not None:
                    user = request.dbsession.query(UserModel)\
                        .filter(UserModel.user_id == resettoken.user_id)\
                        .one_or_none()
            
            if body.get("resettoken") and resettoken is None:
                status_code = httpexceptions.HTTPNotFound.code
                result = error_dict("api_error", "reset token doesnt exist")
            elif user is None:
                status_code = httpexceptions.HTTPOk.code
                result = "Received an email"
            elif isEmailBlacklisted(user.user_email, request.dbsession):
                status_code = httpexceptions.HTTPBadRequest.code
                result = error_dict("api_error", "email is blacklisted")
            elif user.verified is False:
                # People may try to reset their password when not verified, so let them know with this email
                
                # Make new verification token
                new_token = str(uuid4())
                verifytoken = VerifyTokenModel()
                verifytoken.user_id = user.user_id
                verifytoken.token = new_token
                request.dbsession.add(verifytoken)
                request.dbsession.flush()
                request.dbsession.refresh(verifytoken)
                error = send_verification_email(request, user.user_email, verifytoken, "Please verify your email before password reset")

                if error:
                    status_code = httpexceptions.HTTPBadRequest.code
                    result = error
                else:
                    status_code = httpexceptions.HTTPOk.code
                    result = "Received an email"
            else:
                # Create and add reset token
                resettoken = ResetTokenModel()
                resettoken.user_id = user.user_id
                resettoken.token = str(uuid4())
                request.dbsession.add(resettoken)
                request.dbsession.flush()
                request.dbsession.refresh(resettoken)

                # Set how the email will look
                resetlink = request.application_url + "/passwordreset?resettoken=" + resettoken.token
                subject = "Password reset requested"
                body_text = ("A password reset was requested\r\n"
                             "If you wish to reset your password, go to " + resetlink + "\r\n"
                             "If you did not request to change your password, please feel free to ignore this email"
                             )
                body_html = """
                <html>
                <head></head>
                <body>
                    <p>A password reset was requested</p>
                    <p>If you wish to reset your password, go to 
                        <a href='""" + resetlink + """'>""" + resetlink + """</a></p>
                    <p>If you did not request to change your password, please feel free to ignore this email</p>
                </body>
                </html>
                            """
                error = send_email(user.user_email, subject, body_text, body_html)
                if error:
                    status_code = httpexceptions.HTTPBadRequest.code
                    result = error
                else:
                    status_code = httpexceptions.HTTPOk.code
                    result = "Received an email"

        return Response(
            content_type='application/json',
            charset='UTF-8',
            status_code=status_code,
            body=json.dumps({"d": result}, default=datetime_serializer)
        )

    if request.method == 'PUT':
        body = request.json_body
        if body.get("resettoken") is None:
            status_code = httpexceptions.HTTPBadRequest.code
            result = error_dict("api_error", "resettoken is required")
        else:
            resettoken = request.dbsession.query(ResetTokenModel) \
                .filter(ResetTokenModel.token == body.get("resettoken")).one_or_none()
            if resettoken is None:
                status_code = httpexceptions.HTTPNotFound.code
                result = error_dict("api_error", "reset token doesnt exist")
            elif resettoken.started < (datetime.utcnow() - timedelta(days=1)):
                status_code = httpexceptions.HTTPNotAcceptable.code
                result = error_dict("api_error", "reset token is expired")
            elif body.get("user_pass") is None:
                status_code = httpexceptions.HTTPBadRequest.code
                result = error_dict("api_error", "user_pass is required")
            elif len(body.get("user_pass")) < 8:
                status_code = httpexceptions.HTTPBadRequest.code
                result = error_dict("api_error", "password must be at least 8 characters")
            else:
                # We don't set the password just yet, because if there is an error in sending an email, the password
                # would be reset and the user wouldn't know
                user = request.dbsession.query(UserModel) \
                    .filter(UserModel.user_id == resettoken.user_id).one_or_none()

                # Set how the email will look
                subject = "Password successfully reset"
                body_text = "Your password was successfully reset"
                body_html = """
                            <html>
                            <head></head>
                            <body>
                                <p>Your password was successfully reset</p>
                            </body>
                            </html>
                            """
                error = send_email(user.user_email, subject, body_text, body_html)
                if error:
                    status_code = httpexceptions.HTTPBadRequest.code
                    result = error
                else:
                    request.dbsession.query(ResetTokenModel) \
                        .filter(ResetTokenModel.token == body.get("resettoken")) \
                        .filter(ResetTokenModel.started < (datetime.utcnow() - timedelta(days=1))).delete()

                    request.dbsession.delete(resettoken)

                    user.user_pass = pwd_context.hash(body.get("user_pass"))
                    request.dbsession.flush()
                    request.dbsession.refresh(user)

                    status_code = httpexceptions.HTTPOk.code
                    result = "password successfully reset"

        return Response(
            content_type='application/json',
            charset='UTF-8',
            status_code=status_code,
            body=json.dumps({"d": result}, default=datetime_serializer)
        )
        
    if request.method not in ('POST', 'PUT'):
        return Response(status_code=httpexceptions.HTTPMethodNotAllowed.code)

@view_config(route_name="verifytokens")
def verifytokens(request):
    if request.method == 'POST':
        body = request.json_body
        if body.get("verifytoken") is None:
            status_code = httpexceptions.HTTPBadRequest.code
            result = error_dict("api_error", "verifytoken is required")
        else:
            oldVerifytoken = request.dbsession.query(VerifyTokenModel) \
                .filter(VerifyTokenModel.token == body.get("verifytoken")).one_or_none()
            
            if oldVerifytoken is None:
                status_code = httpexceptions.HTTPNotFound.code
                result = error_dict("api_error", "verify token doesnt exist")
            else:
                user = request.dbsession.query(UserModel)\
                    .filter(UserModel.user_id == oldVerifytoken.user_id)\
                    .one_or_none()

                if user is None:
                    status_code = httpexceptions.HTTPNotFound.code
                    result = error_dict("api_error", "user doesnt exist")
                elif isEmailBlacklisted(user.user_email, request.dbsession):
                    status_code = httpexceptions.HTTPBadRequest.code
                    result = error_dict("api_error", "email is blacklisted")
                elif user.verified is True and oldVerifytoken.temp_email is None:
                    status_code = httpexceptions.HTTPBadRequest.code
                    result = error_dict("api_error", "user already verified")
                else:
                    # Make new verification token
                    new_token = str(uuid4())
                    verifytoken = VerifyTokenModel()
                    verifytoken.user_id = user.user_id
                    verifytoken.token = new_token

                    if oldVerifytoken.temp_email:
                        verifytoken.temp_email = oldVerifytoken.temp_email

                    request.dbsession.add(verifytoken)
                    request.dbsession.flush()
                    request.dbsession.refresh(verifytoken)

                    error = send_verification_email(request, user.user_email, verifytoken)

                    if error:
                        status_code = httpexceptions.HTTPBadRequest.code
                        result = error
                    else:
                        status_code = httpexceptions.HTTPOk.code
                        result = "verification email sent"

        return Response(
            content_type='application/json',
            charset='UTF-8',
            status_code=status_code,
            body=json.dumps({"d": result}, default=datetime_serializer)
        )

    if request.method == 'PUT':
        body = request.json_body
        if body.get("verifytoken") is None:
            status_code = httpexceptions.HTTPBadRequest.code
            result = error_dict("api_error", "verifytoken is required")
        else:
            verifytoken = request.dbsession.query(VerifyTokenModel) \
                .filter(VerifyTokenModel.token == body.get("verifytoken")).one_or_none()

            if verifytoken is None:
                status_code = httpexceptions.HTTPNotFound.code
                result = error_dict("api_error", "verify token doesnt exist")
            elif verifytoken.started < (datetime.utcnow() - timedelta(weeks=1)):
                status_code = httpexceptions.HTTPNotAcceptable.code
                result = error_dict("api_error", "verify token is expired")
            else:
                # We don't set user.verified yet, because if there is an error in sending an email, user.verified
                # would be set and the user wouldn't know
                user = request.dbsession.query(UserModel).filter(UserModel.user_id == verifytoken.user_id).one_or_none()

                # If an error happens, it will not get to refresh the user object
                if verifytoken.temp_email is not None:
                    user.user_email = verifytoken.temp_email
                # Set how the email will look
                subject = "Email successfully verified"
                body_text = "Your email successfully verified"
                body_html = """
                                    <html>
                                    <head></head>
                                    <body>
                                        <p>Your email was successfully verified</p>
                                    </body>
                                    </html>
                                    """
                error = send_email(user.user_email, subject, body_text, body_html)
                if error:
                    status_code = httpexceptions.HTTPBadRequest.code
                    result = error
                else:
                    request.dbsession.query(VerifyTokenModel) \
                        .filter(VerifyTokenModel.started < (datetime.utcnow() - timedelta(weeks=1))).delete()

                    user.verified = True
                    request.dbsession.delete(verifytoken)

                    request.dbsession.flush()
                    request.dbsession.refresh(user)
                    status_code = httpexceptions.HTTPOk.code
                    result = "user successfully verified"

        return Response(
            content_type='application/json',
            charset='UTF-8',
            status_code=status_code,
            body=json.dumps({"d": result})
        )
        
    if request.method not in ('POST', 'PUT'):
        return Response(status_code=httpexceptions.HTTPMethodNotAllowed.code)
