from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from server_stuffs.models.meta import Base
from server_stuffs.models import EmailBlacklistModel
from server_stuffs.scripts.utilities import get_SQS_messages, delete_SQS_messages, removeEmailLabelIfAny
from server_stuffs.scripts.converters import dict_from_row
import os
import configparser
import json

def handleBoucesAndComplaints():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), '../../development.ini'))

    SQSurl = config["app:main"]["sqs.url"]

    DBuri = config["app:main"]["sqlalchemy.url"]
    
    engine = create_engine(DBuri)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    dbsession = Session()

    messagesToDelete = []

    response = get_SQS_messages(SQSurl)

    if response is not None:
        print("messages gotten: " + str(len(response)))
        for item in response:
            body = item.get("Body")
            body = json.loads(body)
            messagesToDelete.append({"Id": item.get("MessageId"), "ReceiptHandle": item.get("ReceiptHandle")})
            message = json.loads(body.get("Message"))

            if message.get("notificationType") == "Bounce":
                if (message.get("bounce")["bounceType"] == "Permanent"):
                    email = message.get("bounce")["bouncedRecipients"][0]["emailAddress"]
                    email = removeEmailLabelIfAny(email)
                    existingEmail = dbsession.query(EmailBlacklistModel)\
                        .filter(EmailBlacklistModel.email == email).one_or_none()
                    if existingEmail is None:
                        newBlacklistedEmail = EmailBlacklistModel()
                        newBlacklistedEmail.email = email
                        dbsession.add(newBlacklistedEmail)
                        dbsession.flush()
                        dbsession.refresh(newBlacklistedEmail)
                        dbsession.commit()

            if message.get("notificationType") == "Complaint":
                email = message.get("complaint")["complainedRecipients"][0]["emailAddress"]
                email = removeEmailLabelIfAny(email)
                existingEmail = dbsession.query(EmailBlacklistModel)\
                    .filter(EmailBlacklistModel.email == email).one_or_none()
                if existingEmail is None:
                        newBlacklistedEmail = EmailBlacklistModel()
                        newBlacklistedEmail.email = email
                        dbsession.add(newBlacklistedEmail)
                        dbsession.flush()
                        dbsession.refresh(newBlacklistedEmail)
                        dbsession.commit()

        deleteResponse = delete_SQS_messages(SQSurl, messagesToDelete)
        print(deleteResponse)


if __name__ == "__main__":
    handleBoucesAndComplaints()