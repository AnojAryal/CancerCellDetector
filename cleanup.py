from apscheduler.schedulers.background import BackgroundScheduler
import database
import models

def delete_expired_tokens():
    db = database.SessionLocal()
    try:
        expired_tokens = db.query(models.PasswordResetToken).all()
        if expired_tokens:
            for token in expired_tokens:
                db.delete(token)
            db.commit()
            print("Cleaning process successful")
        else:
            print("Nothing to clean")
        
       
        now = datetime.datetime.utcnow()
        if now.hour == 0 and now.minute == 0:
            print("Message cleaner is running at 12 AM")
            
    finally:
        db.close()


# Create an instance of BackgroundScheduler
scheduler = BackgroundScheduler()


# Add the job to the scheduler
scheduler.add_job(delete_expired_tokens, "cron", hour=0, minute=0)

# Start the scheduler
scheduler.start()
