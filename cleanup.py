from apscheduler.schedulers.background import BackgroundScheduler
import database
import models
import datetime


TOKEN_EXPIRATION_DURATION = datetime.timedelta(minutes=30)


def delete_expired_tokens():
    db = database.SessionLocal()
    try:
        expired_tokens = db.query(models.PasswordResetToken).all()
        if expired_tokens:
            current_time = datetime.datetime.utcnow()
            for token in expired_tokens:
                if token.used or (
                    token.created_at + TOKEN_EXPIRATION_DURATION <= current_time
                ):
                    db.delete(token)
            db.commit()
            print("Cleaning process successful")
        else:
            print("Nothing to clean")

        now = datetime.datetime.utcnow()
        if now.hour == 18 and now.minute == 49:
            print("Message cleaner is running at 12 AM")

    finally:
        db.close()


# Create an instance of BackgroundScheduler
scheduler = BackgroundScheduler()

# Add the job to the scheduler
scheduler.add_job(delete_expired_tokens, "cron", hour=18, minute=49)

# Start the scheduler
scheduler.start()
