"""
One-time helper script to seed local development data.
Creates: 1 admin, 2 employers (with employer profiles), 2 applicants.

Run from repo root or backend folder:
    cd backend && python seed_dummy_users.py
"""
from database import SessionLocal
from models import Users, Employers, FinancialResources
from security import hash_password


def get_or_create_user(db, *, username: str, email: str, password: str, role: str) -> Users:
    user = db.query(Users).filter(Users.email == email).first()
    if user:
        print(f"User already exists: {email} (role={user.role})")
        return user

    user = Users(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Created user: {email} (role={role})")
    return user


def get_or_create_employer_profile(db, *, user: Users, company_name: str, description: str = "") -> Employers:
    employer = db.query(Employers).filter(Employers.user_id == user.user_id).first()
    if employer:
        print(f"Employer profile already exists for user_id={user.user_id}")
        return employer

    employer = Employers(
        user_id=user.user_id,
        company_name=company_name,
        description=description,
        website=None,
        location=None,
    )
    db.add(employer)
    db.commit()
    db.refresh(employer)
    print(f"Created employer profile for {company_name} (user_id={user.user_id})")
    return employer

def get_or_create_financial_resource(db, *, website: str, resource_type: str) -> FinancialResources:
    resource = db.query(FinancialResources).filter(FinancialResources.resource_type == resource_type).first()

    if resource:
        print(f"Financial resource already exists: {website} ({resource_type})")
        return resource

    resource = FinancialResources(
        website=website,
        resource_type=resource_type
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    print(f"Created financial resource: {website} ({resource_type})")
    return resource


def main():
    db = SessionLocal()
    try:
        # Only create an admin if none exists
        existing_admin = db.query(Users).filter(Users.role == "admin").first()
        if existing_admin:
            print(f"Admin already exists: {existing_admin.email} (user_id={existing_admin.user_id})")
            admin = existing_admin
        else:
            admin = get_or_create_user(
                db,
                username="admin",
                email="admin@example.com",
                password="password123",
                role="admin",
            )

        employer1 = get_or_create_user(
            db,
            username="acme_hr",
            email="hr@acme.com",
            password="password123",
            role="employer",
        )
        get_or_create_employer_profile(
            db,
            user=employer1,
            company_name="Acme Corp",
            description="Acme Corp builds everything.",
        )

        employer2 = get_or_create_user(
            db,
            username="globex_hr",
            email="hr@globex.com",
            password="password123",
            role="employer",
        )
        get_or_create_employer_profile(
            db,
            user=employer2,
            company_name="Globex Inc",
            description="Globex builds future tech.",
        )

        get_or_create_user(
            db,
            username="alice_applicant",
            email="alice@applicants.com",
            password="password123",
            role="applicant",
        )

        get_or_create_user(
            db,
            username="bob_applicant",
            email="bob@applicants.com",
            password="password123",
            role="applicant",
        )

        # Seed financial resources
        get_or_create_financial_resource(
            db,
            website="https://www.creditkarma.com",
            resource_type="credit"
        )
        get_or_create_financial_resource(
            db,
            website="https://www.mint.com",
            resource_type="budget"
        )
        get_or_create_financial_resource(
            db,
            website="https://www.robinhood.com",
            resource_type="invest"
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
