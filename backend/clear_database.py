"""Clear all data from the database tables."""
from database import SessionLocal
from models import (
    ResourceLikes,
    FinancialResources,
    Notifications,
    Applications,
    Jobs,
    Employers,
    Users,
)


def clear_all_data():
    """Delete all records from all tables in the correct order to respect foreign keys."""
    db = SessionLocal()
    try:
        print("Starting database cleanup...")

        # Delete in order to respect foreign key constraints
        # Start with tables that depend on others

        # Delete resource likes first
        deleted_resource_likes = db.query(ResourceLikes).delete()
        print(f"   Deleted {deleted_resource_likes} resource likes")

        # Delete financial resources
        deleted_resources = db.query(FinancialResources).delete()
        print(f"   Deleted {deleted_resources} financial resources")

        # Delete notifications
        deleted_notifications = db.query(Notifications).delete()
        print(f"   Deleted {deleted_notifications} notifications")

        # Delete applications (depends on jobs and users)
        deleted_applications = db.query(Applications).delete()
        print(f"   Deleted {deleted_applications} applications")

        # Delete jobs (depends on employers)
        deleted_jobs = db.query(Jobs).delete()
        print(f"   Deleted {deleted_jobs} jobs")

        # Delete employers (depends on users)
        deleted_employers = db.query(Employers).delete()
        print(f"   Deleted {deleted_employers} employers")

        # Delete users last
        deleted_users = db.query(Users).delete()
        print(f"   Deleted {deleted_users} users")

        # Commit all deletions
        db.commit()
        print("\nDatabase cleared successfully!")
        print("   Run 'python seed_dummy_users.py' to repopulate with seed data.")

    except Exception as e:
        db.rollback()
        print(f"\nError clearing database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    confirm = input(
        "WARNING: This will delete ALL data from the database. Are you sure? (yes/no): "
    )
    if confirm.lower() == "yes":
        clear_all_data()
    else:
        print("Operation cancelled.")
