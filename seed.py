from sqlalchemy.orm import Session
from models.relational_models import UserLabels, Setting

""" Creates the seed data for initial setup in the database """
def seed_database(db: Session, user_id: int) -> str:
    # Seed default setting
    settings = db.query(Setting).filter(Setting.user_id == user_id).first()
    check_labels = db.query(UserLabels).filter(UserLabels.user_id == user_id).first()
    
    if not settings:
        initial_setting = Setting(user_id=user_id)
        db.add(initial_setting)

    if not check_labels:
        # default labels
        default_labels = [
            {"label_name": "Finance", "label_description": "Emails related to financial transactions, bills, invoices, and payments."},
            {"label_name": "Work", "label_description": "Professional emails including work correspondence, project updates, and meeting invitations."},
            {"label_name": "Personal", "label_description": "Personal emails from friends, family, and personal interests."},
            {"label_name": "Promotions", "label_description": "Marketing emails, newsletters, and promotional offers."},
            {"label_name": "Social", "label_description": "Notifications from social media platforms and online communities."}
        ]

        for label in default_labels:
            user_label = UserLabels(user_id=user_id, **label)
            db.add(user_label)
        db.commit()
    return "Seeding completed successfully."
    