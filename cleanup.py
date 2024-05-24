from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import database
import models

TOKEN_EXPIRY_MINUTES = 30


def delete_expired_tokens():
    db = database.SessionLocal()
    try:
        expiration_time = datetime.datetime.utcnow() - datetime.timedelta(
            minutes=TOKEN_EXPIRY_MINUTES
        )
        expired_tokens = (
            db.query(models.PasswordResetToken)
            .filter(models.PasswordResetToken.created_at < expiration_time)
            .all()
        )
        if expired_tokens:
            for token in expired_tokens:
                db.delete(token)
            db.commit()
            print("Cleaning process successful")
        else:
            print("Nothing to clean")
    finally:
        db.close()


# Create an instance of BackgroundScheduler
scheduler = BackgroundScheduler()


print("Message cleaner is now starting...")

scheduler.add_job(delete_expired_tokens, "cron", hour=0, minute=0)


# Start the scheduler
scheduler.start()
