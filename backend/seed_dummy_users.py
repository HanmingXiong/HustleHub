"""Seed local development data with predictable users, profiles, and sample jobs."""
from database import SessionLocal
from models import Users, Employers, FinancialResources, Jobs, Applications
from security import hash_password


def get_or_create_user(db, *, username: str, email: str, password: str, role: str, 
                       first_name: str = None, last_name: str = None, phone: str = None, 
                       resume_file: str = None) -> Users:
    # Create a user if missing, otherwise return the existing record
    user = db.query(Users).filter(Users.email == email).first()
    if user:
        print(f"User already exists: {email} (role={user.role})")
        # Update fields if provided
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if phone:
            user.phone = phone
        if resume_file:
            user.resume_file = resume_file
        db.commit()
        return user

    user = Users(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=role,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        resume_file=resume_file,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Created user: {email} (role={role})")
    return user


def get_or_create_employer_profile(db, *, user: Users, company_name: str, description: str = "", 
                                   website: str = None, location: str = None) -> Employers:
    # Ensure the employer profile exists for the given user
    employer = db.query(Employers).filter(Employers.user_id == user.user_id).first()
    if employer:
        print(f"Employer profile already exists for user_id={user.user_id}")
        # Update fields if provided
        employer.company_name = company_name
        employer.description = description
        if website:
            employer.website = website
        if location:
            employer.location = location
        db.commit()
        return employer

    employer = Employers(
        user_id=user.user_id,
        company_name=company_name,
        description=description,
        website=website,
        location=location,
    )
    db.add(employer)
    db.commit()
    db.refresh(employer)
    print(f"Created employer profile for {company_name} (user_id={user.user_id})")
    return employer

def get_or_create_financial_resource(db, *, name: str, website: str, description: str, resource_type: str) -> FinancialResources:
    # Seed a financial resource entry if it doesn't exist
    resource = db.query(FinancialResources).filter(FinancialResources.website == website,
                                                   FinancialResources.resource_type == resource_type).first()

    if resource:
        print(f"Financial resource already exists: {website} ({resource_type})")
        return resource

    resource = FinancialResources(
        name=name,
        website=website,
        description=description,
        resource_type=resource_type,
        likes=0
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    print(f"Created financial resource: {name} ({resource_type})")
    return resource

def get_or_create_job(db, *, employer_profile, title, description, location, pay, job_type):
    """Attach a job to the given employer if it doesn't already exist."""
    job = db.query(Jobs).filter(
        Jobs.title == title, 
        Jobs.employer_id == employer_profile.employer_id
    ).first()
    
    if job:
        print(f"Job already exists: {title}")
        return job
    
    job = Jobs(
        employer_id=employer_profile.employer_id,
        title=title,
        description=description,
        job_type=job_type,
        location=location,
        pay_range=pay,
        is_active=True
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    print(f"Created job: {title}")
    return job

def reset_jobs(db):
    """Remove existing seeded jobs and dependent applications."""
    deleted_apps = db.query(Applications).delete()
    deleted_jobs = db.query(Jobs).delete()
    db.commit()
    print(f"Cleared existing jobs ({deleted_jobs}) and applications ({deleted_apps}).")

def main():
    # Seed baseline users, employers, resources, and fresh job listings
    db = SessionLocal()
    try:
        admin_password = "password123"
        existing_admin = db.query(Users).filter(Users.role == "admin").first()
        if existing_admin:
            print(f"Admin already exists: {existing_admin.email} (user_id={existing_admin.user_id})")
            existing_admin.password_hash = hash_password(admin_password)
            db.commit()
            print("Admin password has been reset to password123.")
            admin = existing_admin
        else:
            admin = get_or_create_user(
                db,
                username="admin",
                email="admin@example.com",
                password=admin_password,
                role="admin",
            )

        # Seed employers with complete profiles - focused on entry-level/low-income jobs
        employer1 = get_or_create_user(
            db,
            username="quickmart_hr",
            email="hiring@quickmart.com",
            password="password123",
            role="employer",
            first_name="Sarah",
            last_name="Johnson",
            phone="555-0101",
        )
        emp_profile1 = get_or_create_employer_profile(
            db,
            user=employer1,
            company_name="QuickMart Grocery",
            description="Local grocery store chain hiring for various positions. We offer flexible scheduling and opportunities for advancement.",
            website="https://www.quickmart.com",
            location="New York, NY",
        )

        employer2 = get_or_create_user(
            db,
            username="burger_palace",
            email="manager@burgerpalace.com",
            password="password123",
            role="employer",
            first_name="Michael",
            last_name="Chen",
            phone="555-0102",
        )
        emp_profile2 = get_or_create_employer_profile(
            db,
            user=employer2,
            company_name="Burger Palace",
            description="Fast food restaurant looking for reliable team members. No experience necessary - we train! Meal discounts and flexible hours.",
            website="https://www.burgerpalace.com",
            location="Brooklyn, NY",
        )

        employer3 = get_or_create_user(
            db,
            username="local_cafe",
            email="manager@localcafe.com",
            password="password123",
            role="employer",
            first_name="Emma",
            last_name="Rodriguez",
            phone="555-0103",
        )
        emp_profile3 = get_or_create_employer_profile(
            db,
            user=employer3,
            company_name="Corner Cafe",
            description="Neighborhood cafe serving coffee and breakfast. Looking for friendly, reliable staff. Tips and flexible scheduling.",
            website="https://www.cornercafe.com",
            location="Queens, NY",
        )

        employer4 = get_or_create_user(
            db,
            username="cleanpro",
            email="jobs@cleanpro.com",
            password="password123",
            role="employer",
            first_name="James",
            last_name="Wilson",
            phone="555-0104",
        )
        emp_profile4 = get_or_create_employer_profile(
            db,
            user=employer4,
            company_name="CleanPro Services",
            description="Professional cleaning company hiring for residential and commercial cleaning. Flexible hours, weekly pay, transportation assistance available.",
            website="https://www.cleanproservices.com",
            location="Bronx, NY",
        )

        employer5 = get_or_create_user(
            db,
            username="delivery_express",
            email="drivers@deliveryexpress.com",
            password="password123",
            role="employer",
            first_name="Lisa",
            last_name="Garcia",
            phone="555-0105",
        )
        emp_profile5 = get_or_create_employer_profile(
            db,
            user=employer5,
            company_name="Delivery Express",
            description="Food and package delivery service. Be your own boss with flexible hours. Earn money on your schedule.",
            website="https://www.deliveryexpress.com",
            location="New York, NY",
        )

        # Seed applicants with complete profiles
        alice = get_or_create_user(
            db,
            username="alice_applicant",
            email="alice@applicants.com",
            password="password123",
            role="applicant",
            first_name="Alice",
            last_name="Williams",
            phone="555-0201",
            resume_file="uploads/resumes/alice_williams_resume.pdf",
        )

        bob = get_or_create_user(
            db,
            username="bob_applicant",
            email="bob@applicants.com",
            password="password123",
            role="applicant",
            first_name="Bob",
            last_name="Martinez",
            phone="555-0202",
            resume_file="uploads/resumes/bob_martinez_resume.pdf",
        )

        charlie = get_or_create_user(
            db,
            username="charlie_dev",
            email="charlie@applicants.com",
            password="password123",
            role="applicant",
            first_name="Charlie",
            last_name="Thompson",
            phone="555-0203",
            resume_file="uploads/resumes/charlie_thompson_resume.pdf",
        )

        diana = get_or_create_user(
            db,
            username="diana_student",
            email="diana@applicants.com",
            password="password123",
            role="applicant",
            first_name="Diana",
            last_name="Patel",
            phone="555-0204",
            resume_file="uploads/resumes/diana_patel_resume.pdf",
        )

        evan = get_or_create_user(
            db,
            username="evan_writer",
            email="evan@applicants.com",
            password="password123",
            role="applicant",
            first_name="Evan",
            last_name="Kim",
            phone="555-0205",
        )

        # Seed financial resources
        get_or_create_financial_resource(
            db,
            name="Credit Karma",
            website="https://www.creditkarma.com",
            description="Free credit scores and reports with personalized recommendations",
            resource_type="credit"
        )
        get_or_create_financial_resource(
            db,
            name="Experian",
            website="https://www.experian.com",
            description="Monitor your credit and get identity theft protection",
            resource_type="credit"
        )
        get_or_create_financial_resource(
            db,
            name="Mint",
            website="https://www.mint.com",
            description="Free budgeting app to track spending and manage finances",
            resource_type="budget"
        )
        get_or_create_financial_resource(
            db,
            name="YNAB (You Need A Budget)",
            website="https://www.ynab.com",
            description="Budgeting software that helps you gain control of your money",
            resource_type="budget"
        )
        get_or_create_financial_resource(
            db,
            name="Robinhood",
            website="https://www.robinhood.com",
            description="Commission-free stock trading and investing platform",
            resource_type="invest"
        )
        get_or_create_financial_resource(
            db,
            name="Fidelity",
            website="https://www.fidelity.com",
            description="Full-service brokerage with research tools and retirement planning",
            resource_type="invest"
        )

        reset_jobs(db)

        # Seed realistic entry-level and low-income jobs
        # QuickMart Grocery jobs
        job1 = get_or_create_job(
            db,
            employer_profile=emp_profile1,
            title="Cashier",
            description="Ring up customer purchases, handle cash and card payments, provide friendly service. No experience required - we provide full training. Must be reliable and have good customer service skills. Flexible shifts available including evenings and weekends.",
            location="New York, NY",
            pay="$15.50/hr",
            job_type="part-time"
        )
        
        job2 = get_or_create_job(
            db,
            employer_profile=emp_profile1,
            title="Stock Clerk",
            description="Unload deliveries, stock shelves, organize inventory, and keep store clean. Early morning shifts (5am-1pm) or evening shifts (2pm-10pm) available. Ability to lift 50lbs required. Great for students or anyone looking for steady part-time work.",
            location="New York, NY",
            pay="$16/hr",
            job_type="part-time"
        )
        
        job3 = get_or_create_job(
            db,
            employer_profile=emp_profile1,
            title="Overnight Stocker",
            description="Stock shelves and organize products during overnight hours (10pm-6am). Overnight differential pay. Perfect for night owls or those with daytime commitments. Quiet work environment.",
            location="New York, NY",
            pay="$17.50/hr",
            job_type="full-time"
        )
        
        # Burger Palace jobs
        job4 = get_or_create_job(
            db,
            employer_profile=emp_profile2,
            title="Crew Member",
            description="Take orders, prepare food, clean dining area. No experience necessary - full training provided! Free meals during shifts. Flexible scheduling perfect for students. Opportunities to advance to shift leader.",
            location="Brooklyn, NY",
            pay="$15/hr",
            job_type="part-time"
        )
        
        job5 = get_or_create_job(
            db,
            employer_profile=emp_profile2,
            title="Kitchen Staff",
            description="Prepare food items, maintain kitchen cleanliness, follow food safety procedures. Fast-paced environment. Evening and weekend shifts available. Meal discounts and flexible hours.",
            location="Brooklyn, NY",
            pay="$15.50/hr",
            job_type="part-time"
        )

        job6 = get_or_create_job(
            db,
            employer_profile=emp_profile2,
            title="Shift Leader",
            description="Supervise crew members, handle cash register, ensure quality service. Previous fast food or retail experience preferred. Leadership opportunity with room for growth. Consistent schedule.",
            location="Brooklyn, NY",
            pay="$17/hr",
            job_type="full-time"
        )
        
        # Corner Cafe jobs
        job7 = get_or_create_job(
            db,
            employer_profile=emp_profile3,
            title="Barista",
            description="Make coffee drinks, serve customers, maintain clean workspace. Friendly atmosphere, regular customers. Tips average $3-5/hr extra. Morning shifts (6am-2pm) or afternoon shifts (12pm-8pm). Will train on espresso machine.",
            location="Queens, NY",
            pay="$15/hr + tips",
            job_type="part-time"
        )

        job8 = get_or_create_job(
            db,
            employer_profile=emp_profile3,
            title="Server/Counter Staff",
            description="Take orders, serve food and drinks, bus tables, handle payments. Weekday and weekend shifts available. Great tips from regular customers. Friendly team environment. Free coffee and meal discounts.",
            location="Queens, NY",
            pay="$15/hr + tips",
            job_type="part-time"
        )

        # CleanPro Services jobs
        job9 = get_or_create_job(
            db,
            employer_profile=emp_profile4,
            title="House Cleaner",
            description="Clean residential homes - dusting, vacuuming, mopping, bathroom/kitchen cleaning. Work independently or with a partner. Flexible schedule - choose your hours. Weekly pay. Cleaning supplies provided. Transportation assistance available for those without cars.",
            location="Bronx, NY",
            pay="$16-$18/hr",
            job_type="part-time"
        )

        job10 = get_or_create_job(
            db,
            employer_profile=emp_profile4,
            title="Office Cleaner",
            description="Clean office buildings in the evening (6pm-10pm). Empty trash, vacuum, clean restrooms, restock supplies. Steady schedule Monday-Friday. No weekends! Reliable and detail-oriented individuals needed.",
            location="Manhattan, NY",
            pay="$16.50/hr",
            job_type="part-time"
        )

        job11 = get_or_create_job(
            db,
            employer_profile=emp_profile4,
            title="Cleaning Team Member",
            description="Join our team cleaning commercial spaces. Day shifts available. Work with experienced team members. All equipment and supplies provided. Opportunity for full-time hours and benefits after 90 days.",
            location="Bronx, NY",
            pay="$17/hr",
            job_type="full-time"
        )

        # Delivery Express jobs
        job12 = get_or_create_job(
            db,
            employer_profile=emp_profile5,
            title="Delivery Driver (Bike)",
            description="Deliver food orders by bicycle in Manhattan and Brooklyn. Set your own schedule - work when you want. Earn $15-25/hr including tips. Must have smartphone and reliable bike. Great way to stay active and earn money. No car needed!",
            location="New York, NY",
            pay="$15-$25/hr with tips",
            job_type="gig"
        )

        job13 = get_or_create_job(
            db,
            employer_profile=emp_profile5,
            title="Delivery Driver (Car)",
            description="Deliver food and packages using your own vehicle. Flexible hours - be your own boss. Earn more during peak hours (lunch and dinner). Gas reimbursement provided. Must have valid driver's license and insurance.",
            location="New York, NY",
            pay="$18-$30/hr with tips",
            job_type="gig"
        )

        job14 = get_or_create_job(
            db,
            employer_profile=emp_profile5,
            title="Package Courier",
            description="Pick up and deliver packages across the city. Same-day delivery service. Use your car, bike, or public transit. Get paid per delivery plus tips. Work as much or as little as you want. Perfect side hustle or full-time gig.",
            location="New York, NY",
            pay="$12-$20/hr + per delivery bonus",
            job_type="gig"
        )

        # Create applications from various applicants
        # Alice applies to 4 retail/service jobs
        app1 = Applications(
            job_id=job2.job_id,
            user_id=alice.user_id,
            cover_letter="I'm interested in the stock clerk position. I'm reliable and don't mind early morning shifts. I can lift 50 lbs and I'm good at staying organized. I'm looking for steady part-time work.",
            status="pending"
        )
        app2 = Applications(
            job_id=job1.job_id,
            user_id=alice.user_id,
            cover_letter="I'd like to apply for the cashier position. I'm good with numbers and have experience handling money from my previous job. I'm honest, dependable, and can work flexible hours including nights and weekends.",
            status="reviewed"
        )
        app3 = Applications(
            job_id=job7.job_id,
            user_id=alice.user_id,
            cover_letter="I'm applying for the barista position. I love coffee and enjoy talking with customers. I'm a quick learner and available for morning and afternoon shifts. I'm looking for steady part-time work.",
            status="accepted"
        )
        app4 = Applications(
            job_id=job8.job_id,
            user_id=alice.user_id,
            cover_letter="I'm interested in the server position. I have 6 months of experience as a server at a diner. I'm good at multitasking and staying calm during busy times. I can work weekends and evenings.",
            status="pending"
        )
        db.add_all([app1, app2, app3, app4])
        print(f"Created 4 applications for Alice")

        # Bob applies to 4 delivery/warehouse jobs
        app5 = Applications(
            job_id=job2.job_id,
            user_id=bob.user_id,
            cover_letter="I'm applying for the stock clerk position. I'm physically fit and can lift heavy boxes. I worked in a warehouse before and know how to stay organized. I'm available for any shift including nights and weekends.",
            status="reviewed"
        )
        app6 = Applications(
            job_id=job13.job_id,
            user_id=bob.user_id,
            cover_letter="I have a clean driver's license and my own reliable car. I've done delivery work before with DoorDash and know the NYC area well. I'm looking for steady delivery work and can work full-time hours.",
            status="accepted"
        )
        app7 = Applications(
            job_id=job12.job_id,
            user_id=bob.user_id,
            cover_letter="I have a good bike and I'm in great shape. I know Manhattan and Brooklyn really well. I'm looking for flexible work where I can set my own hours. I'm reliable and fast.",
            status="pending"
        )
        app8 = Applications(
            job_id=job3.job_id,
            user_id=bob.user_id,
            cover_letter="I'm interested in the overnight stocker position. I'm a night owl and prefer working when it's quiet. I'm dependable and looking for full-time steady work with benefits.",
            status="reviewed"
        )
        db.add_all([app5, app6, app7, app8])
        print(f"Created 4 applications for Bob")

        # Charlie applies to 4 cleaning jobs
        app9 = Applications(
            job_id=job10.job_id,
            user_id=charlie.user_id,
            cover_letter="I'm applying for the office cleaner position. I have 1 year of cleaning experience and know how to do the job right. I'm reliable and can work evening shifts Monday through Friday. I have my own transportation.",
            status="accepted"
        )
        app10 = Applications(
            job_id=job9.job_id,
            user_id=charlie.user_id,
            cover_letter="I'm interested in the house cleaner position. I'm thorough and take pride in my work. I like the flexibility of choosing my own hours. I'm dependable and have good references from previous cleaning jobs.",
            status="reviewed"
        )
        app11 = Applications(
            job_id=job11.job_id,
            user_id=charlie.user_id,
            cover_letter="I'm applying for the cleaning team member position. I'm looking for full-time work with benefits. I work well with others and I'm willing to learn. I'm hardworking and show up on time every day.",
            status="pending"
        )
        app12 = Applications(
            job_id=job5.job_id,
            user_id=charlie.user_id,
            cover_letter="I'm interested in the kitchen staff position. I've worked in restaurant kitchens before and can handle the fast pace. I'm available for any shift and can start right away. I'm a hard worker and team player.",
            status="pending"
        )
        db.add_all([app9, app10, app11, app12])
        print(f"Created 4 applications for Charlie")

        # Diana applies to 4 jobs (student looking for part-time work)
        app13 = Applications(
            job_id=job1.job_id,
            user_id=diana.user_id,
            cover_letter="I'm a college student looking for part-time work. I'm friendly, responsible, and good with customers. I can work 15-20 hours per week, mostly evenings and weekends around my class schedule.",
            status="reviewed"
        )
        app14 = Applications(
            job_id=job4.job_id,
            user_id=diana.user_id,
            cover_letter="I'm interested in the crew member position. This would be my first job but I'm eager to learn and I'm very reliable. I can work evenings and weekends. Free meals would really help with my budget!",
            status="pending"
        )
        app15 = Applications(
            job_id=job7.job_id,
            user_id=diana.user_id,
            cover_letter="I'd love to work as a barista. I'm a people person and enjoy making customers happy. I'm available mornings before class and on weekends. I'm looking for a friendly work environment where I can learn new skills.",
            status="pending"
        )
        app16 = Applications(
            job_id=job8.job_id,
            user_id=diana.user_id,
            cover_letter="I'm applying for the server position. I'm organized, friendly, and good at multitasking. I can work weekend shifts which fit perfectly with my class schedule. I'm available to start immediately.",
            status="reviewed"
        )
        db.add_all([app13, app14, app15, app16])
        print(f"Created 4 applications for Diana")

        # Evan applies to 4 food service/delivery jobs
        app17 = Applications(
            job_id=job7.job_id,
            user_id=evan.user_id,
            cover_letter="I'm interested in the barista position. I'm friendly, energetic, and love working with people. I learn quickly and am available for flexible hours. I'm looking for a positive work environment.",
            status="accepted"
        )
        app18 = Applications(
            job_id=job4.job_id,
            user_id=evan.user_id,
            cover_letter="I'm applying for the crew member position. I'm comfortable working in fast-paced environments and I'm very clean and organized. I follow directions well and work great with a team. Free meals are a big plus!",
            status="reviewed"
        )
        app19 = Applications(
            job_id=job12.job_id,
            user_id=evan.user_id,
            cover_letter="I have a bike and I'm looking for flexible work. I'm in good shape and know the city well. I like the idea of being active while earning money. I can work lunch and dinner rushes for maximum earnings.",
            status="pending"
        )
        app20 = Applications(
            job_id=job14.job_id,
            user_id=evan.user_id,
            cover_letter="I'm interested in the package courier position. I'm reliable and good at time management. I have a bike and know how to use public transit efficiently. I'm looking for a flexible side hustle.",
            status="pending"
        )
        db.add_all([app17, app18, app19, app20])
        print(f"Created 4 applications for Evan")

        db.commit()
        print("\n✅ Seed data complete! Created 14 entry-level minimum wage jobs and 20 applications across 5 applicants and 5 employers.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
