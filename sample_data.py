"""
JobPortal Sample Data Script
Run: python manage.py shell < sample_data.py
OR:  python manage.py runscript sample_data  (if django-extensions installed)
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')
django.setup()

from django.utils.text import slugify
from accounts.models import User
from companies.models import Company
from jobs.models import Job, JobCategory, JobSkill, JobSkillMapping
from candidates.models import CandidateProfile, Education, WorkExperience, CandidateSkill
from applications.models import Application, ApplicationStatusHistory
from notifications.models import Notification

print("Deleting old sample data...")
Application.objects.all().delete()
Job.objects.all().delete()
JobSkill.objects.all().delete()
JobCategory.objects.all().delete()
Company.objects.all().delete()
CandidateProfile.objects.all().delete()
User.objects.filter(is_staff=False).delete()

print("Creating users...")

# ─── ADMIN ──────────────────────────────────────────────────────────────────
admin = User.objects.create_superuser(
    email='admin@jobportal.com',
    password='Admin@123',
    first_name='Super',
    last_name='Admin',
)

# ─── RECRUITERS ─────────────────────────────────────────────────────────────
recruiters_data = [
    ('hr@tcs.com',        'Priya',    'Sharma',   '9876543210'),
    ('hr@infosys.com',    'Rahul',    'Verma',    '9876543211'),
    ('hr@wipro.com',      'Sneha',    'Nair',     '9876543212'),
    ('hr@amazon.com',     'Arjun',    'Mehta',    '9876543213'),
    ('hr@google.com',     'Kavya',    'Reddy',    '9876543214'),
    ('hr@zomato.com',     'Vikram',   'Singh',    '9876543215'),
    ('hr@swiggy.com',     'Pooja',    'Patel',    '9876543216'),
    ('hr@myntra.com',     'Aditya',   'Kumar',    '9876543217'),
]

recruiters = []
for email, fname, lname, phone in recruiters_data:
    u = User.objects.create_user(
        email=email, password='Recruiter@123',
        first_name=fname, last_name=lname,
        phone=phone, role=User.RECRUITER, is_verified=True
    )
    recruiters.append(u)

print(f"  Created {len(recruiters)} recruiters")

# ─── CANDIDATES ─────────────────────────────────────────────────────────────
candidates_data = [
    ('arun.kumar@gmail.com',    'Arun',     'Kumar',    '9900000001'),
    ('divya.menon@gmail.com',   'Divya',    'Menon',    '9900000002'),
    ('karthik.raj@gmail.com',   'Karthik',  'Raj',      '9900000003'),
    ('meera.iyer@gmail.com',    'Meera',    'Iyer',     '9900000004'),
    ('ravi.shankar@gmail.com',  'Ravi',     'Shankar',  '9900000005'),
    ('anita.das@gmail.com',     'Anita',    'Das',      '9900000006'),
    ('suresh.babu@gmail.com',   'Suresh',   'Babu',     '9900000007'),
    ('lakshmi.priya@gmail.com', 'Lakshmi',  'Priya',    '9900000008'),
    ('mohan.raj@gmail.com',     'Mohan',    'Raj',      '9900000009'),
    ('nisha.thomas@gmail.com',  'Nisha',    'Thomas',   '9900000010'),
    ('prasad.v@gmail.com',      'Prasad',   'Venkat',   '9900000011'),
    ('rohini.k@gmail.com',      'Rohini',   'Krishna',  '9900000012'),
]

candidates = []
for email, fname, lname, phone in candidates_data:
    u = User.objects.create_user(
        email=email, password='Candidate@123',
        first_name=fname, last_name=lname,
        phone=phone, role=User.CANDIDATE, is_verified=True
    )
    candidates.append(u)

print(f"  Created {len(candidates)} candidates")

# ─── JOB CATEGORIES ─────────────────────────────────────────────────────────
categories_data = [
    ('Information Technology', 'bi-laptop',          'information-technology'),
    ('Data Science & AI',      'bi-bar-chart',       'data-science-ai'),
    ('Web Development',        'bi-code-slash',      'web-development'),
    ('Mobile Development',     'bi-phone',           'mobile-development'),
    ('DevOps & Cloud',         'bi-cloud',           'devops-cloud'),
    ('Design & UX',            'bi-palette',         'design-ux'),
    ('Marketing',              'bi-megaphone',       'marketing'),
    ('Finance & Accounts',     'bi-currency-rupee',  'finance-accounts'),
    ('Human Resources',        'bi-people',          'human-resources'),
    ('Sales & Business',       'bi-graph-up',        'sales-business'),
]

categories = {}
for name, icon, slug in categories_data:
    cat = JobCategory.objects.create(name=name, slug=slug, icon=icon)
    categories[slug] = cat

print(f"  Created {len(categories)} job categories")

# ─── JOB SKILLS ─────────────────────────────────────────────────────────────
skills_list = [
    'Python', 'Django', 'Flask', 'FastAPI',
    'JavaScript', 'TypeScript', 'React', 'Vue.js', 'Angular', 'Next.js',
    'Node.js', 'Express.js',
    'Java', 'Spring Boot', 'Kotlin',
    'C++', 'C#', '.NET',
    'PHP', 'Laravel',
    'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite',
    'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes',
    'Git', 'Linux', 'CI/CD', 'Jenkins',
    'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch',
    'Data Analysis', 'Pandas', 'NumPy', 'Scikit-learn',
    'Power BI', 'Tableau', 'Excel',
    'Figma', 'Adobe XD', 'Photoshop',
    'React Native', 'Flutter', 'Android', 'iOS', 'Swift',
    'REST API', 'GraphQL', 'Microservices',
    'Selenium', 'Pytest', 'JUnit',
    'HTML', 'CSS', 'Bootstrap', 'Tailwind CSS',
    'Agile', 'Scrum', 'JIRA',
    'Communication', 'Leadership', 'Problem Solving',
]

skill_objs = {}
for name in skills_list:
    sl = slugify(name)
    if not JobSkill.objects.filter(slug=sl).exists():
        sk = JobSkill.objects.create(name=name, slug=sl)
        skill_objs[name] = sk

print(f"  Created {len(skill_objs)} job skills")

# ─── COMPANIES ───────────────────────────────────────────────────────────────
companies_data = [
    # (recruiter_idx, name, industry, size, city, description)
    (0, 'Tata Consultancy Services', 'Information Technology', '5000+', 'Mumbai',
     'TCS is a global leader in IT services, consulting, and business solutions.'),
    (1, 'Infosys', 'Information Technology', '5000+', 'Bangalore',
     'Infosys is a global leader in next-generation digital services and consulting.'),
    (2, 'Wipro Technologies', 'Information Technology', '5000+', 'Bangalore',
     'Wipro is a leading global information technology, consulting and business process services company.'),
    (3, 'Amazon India', 'E-Commerce & Technology', '5000+', 'Hyderabad',
     'Amazon is guided by four principles: customer obsession, passion for invention, commitment to operational excellence, and long-term thinking.'),
    (4, 'Google India', 'Technology', '5000+', 'Bangalore',
     'Google is a multinational technology company specializing in Internet-related services and products.'),
    (5, 'Zomato', 'Food Technology', '1001-5000', 'Gurugram',
     'Zomato is an Indian multinational restaurant aggregator and food delivery company.'),
    (6, 'Swiggy', 'Food Technology', '1001-5000', 'Bangalore',
     'Swiggy is India\'s leading on-demand delivery platform.'),
    (7, 'Myntra', 'E-Commerce & Fashion', '1001-5000', 'Bangalore',
     'Myntra is India\'s leading fashion e-commerce platform.'),
]

companies = []
for r_idx, name, industry, size, city, desc in companies_data:
    sl = slugify(name)
    c = Company.objects.create(
        recruiter=recruiters[r_idx],
        name=name, slug=sl,
        industry=industry, company_size=size,
        city=city, state='Karnataka' if city == 'Bangalore' else '',
        description=desc,
        website=f'https://www.{sl.replace("-", "")}.com',
        is_verified=True, is_active=True,
    )
    companies.append(c)

print(f"  Created {len(companies)} companies")

# ─── JOBS ────────────────────────────────────────────────────────────────────
jobs_data = [
    # (company_idx, recruiter_idx, category_slug, title, job_type, experience, location,
    #  min_sal, max_sal, description, skill_names)
    (0, 0, 'information-technology',
     'Senior Python Developer', 'full_time', '3-5', 'Chennai',
     1200000, 2000000,
     'We are looking for a Senior Python Developer to join our growing team. You will be responsible for developing and maintaining Python-based applications.\n\nResponsibilities:\n- Design and implement Python applications\n- Write clean, testable code\n- Collaborate with cross-functional teams\n- Code reviews and mentoring junior developers\n\nRequirements:\n- 3-5 years of Python experience\n- Strong knowledge of Django or Flask\n- Experience with REST APIs\n- Good understanding of databases',
     ['Python', 'Django', 'REST API', 'MySQL', 'Git']),

    (0, 0, 'web-development',
     'Full Stack Developer', 'full_time', '1-3', 'Bangalore',
     800000, 1500000,
     'Join TCS as a Full Stack Developer and work on enterprise-grade web applications.\n\nResponsibilities:\n- Build responsive web applications\n- Work on both frontend and backend\n- Database design and optimization\n\nRequirements:\n- Proficiency in React and Node.js\n- Experience with REST APIs\n- Knowledge of SQL databases',
     ['React', 'Node.js', 'JavaScript', 'MySQL', 'HTML', 'CSS']),

    (1, 1, 'data-science-ai',
     'Machine Learning Engineer', 'full_time', '3-5', 'Bangalore',
     1500000, 2500000,
     'Infosys is seeking a passionate Machine Learning Engineer to build AI-powered products.\n\nYou will work on:\n- Building and deploying ML models\n- Data preprocessing and feature engineering\n- Model evaluation and improvement\n\nRequirements:\n- Strong Python skills\n- Experience with TensorFlow or PyTorch\n- Knowledge of statistics',
     ['Python', 'Machine Learning', 'TensorFlow', 'Pandas', 'NumPy', 'Scikit-learn']),

    (1, 1, 'data-science-ai',
     'Data Analyst', 'full_time', '1-3', 'Pune',
     600000, 1000000,
     'We need a Data Analyst to help us make data-driven decisions.\n\nKey Responsibilities:\n- Analyze large datasets\n- Create dashboards and reports\n- Identify trends and patterns\n\nRequired Skills:\n- SQL and Python\n- Power BI or Tableau\n- Strong Excel skills',
     ['Data Analysis', 'Python', 'SQL', 'Power BI', 'Excel', 'Pandas']),

    (2, 2, 'devops-cloud',
     'DevOps Engineer', 'full_time', '3-5', 'Hyderabad',
     1200000, 2200000,
     'Wipro is hiring a DevOps Engineer to help automate and optimize our deployment pipelines.\n\nResponsibilities:\n- Manage CI/CD pipelines\n- Container orchestration with Kubernetes\n- Cloud infrastructure management\n\nRequirements:\n- Experience with Docker and Kubernetes\n- Knowledge of AWS or Azure\n- Shell scripting',
     ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Linux', 'Jenkins', 'Git']),

    (2, 2, 'information-technology',
     'Java Spring Boot Developer', 'full_time', '1-3', 'Noida',
     700000, 1200000,
     'Looking for a Java developer with Spring Boot experience to build microservices.\n\nResponsibilities:\n- Develop RESTful APIs using Spring Boot\n- Write unit tests\n- Database design\n\nRequirements:\n- Core Java knowledge\n- Spring Boot experience\n- Knowledge of microservices',
     ['Java', 'Spring Boot', 'MySQL', 'REST API', 'Microservices', 'Git']),

    (3, 3, 'information-technology',
     'Software Development Engineer II', 'full_time', '3-5', 'Hyderabad',
     2000000, 3500000,
     'Amazon is looking for talented SDE-II engineers to solve complex problems at scale.\n\nAt Amazon you will:\n- Design distributed systems\n- Lead technical projects\n- Mentor junior engineers\n\nRequirements:\n- Strong CS fundamentals\n- Proficiency in any language (Java/Python/C++)\n- Experience with distributed systems',
     ['Java', 'Python', 'AWS', 'Microservices', 'REST API', 'Git', 'Agile']),

    (3, 3, 'devops-cloud',
     'Cloud Solutions Architect', 'full_time', '5-10', 'Bangalore',
     3000000, 5000000,
     'Design and build scalable cloud solutions on AWS for enterprise clients.\n\nResponsibilities:\n- Architect cloud solutions\n- Cost optimization\n- Technical leadership\n\nRequirements:\n- 5+ years cloud experience\n- AWS certifications preferred\n- Strong communication skills',
     ['AWS', 'Azure', 'Docker', 'Kubernetes', 'Microservices', 'Python']),

    (4, 4, 'data-science-ai',
     'AI Research Scientist', 'full_time', '5-10', 'Bangalore',
     3000000, 6000000,
     'Join Google\'s AI research team and work on cutting-edge machine learning research.\n\nResponsibilities:\n- Conduct original research\n- Publish papers at top conferences\n- Collaborate with product teams\n\nRequirements:\n- PhD in ML/AI or equivalent experience\n- Strong publication record\n- Deep expertise in ML',
     ['Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Python', 'Research']),

    (4, 4, 'web-development',
     'Frontend Engineer (React)', 'full_time', '1-3', 'Bangalore',
     1200000, 2000000,
     'Build beautiful, performant user interfaces for Google products used by billions.\n\nResponsibilities:\n- Build React components\n- Performance optimization\n- A/B testing\n\nRequirements:\n- Strong React skills\n- TypeScript experience\n- CSS expertise',
     ['React', 'TypeScript', 'JavaScript', 'CSS', 'HTML', 'Git']),

    (5, 5, 'information-technology',
     'Backend Engineer - Python', 'full_time', '1-3', 'Gurugram',
     900000, 1600000,
     'Build scalable backend systems for Zomato\'s food delivery platform.\n\nYour work will:\n- Handle millions of requests per day\n- Ensure high availability\n- Power real-time features\n\nRequirements:\n- Python expertise\n- Knowledge of caching (Redis)\n- Experience with high-scale systems',
     ['Python', 'Django', 'Redis', 'PostgreSQL', 'REST API', 'Docker']),

    (5, 5, 'mobile-development',
     'Android Developer', 'full_time', '1-3', 'Gurugram',
     800000, 1400000,
     'Build the Zomato Android app used by 50 million users.\n\nResponsibilities:\n- Feature development\n- Performance optimization\n- Writing tests\n\nRequirements:\n- Kotlin/Java experience\n- Understanding of Android SDK\n- Knowledge of MVVM pattern',
     ['Android', 'Kotlin', 'Java', 'Git', 'REST API']),

    (6, 6, 'mobile-development',
     'Flutter Developer', 'full_time', '0-1', 'Bangalore',
     600000, 1000000,
     'Build cross-platform mobile apps for Swiggy using Flutter.\n\nThis is a great opportunity for:\n- Fresh graduates passionate about mobile\n- Developers wanting to learn Flutter\n\nRequirements:\n- Basic Flutter knowledge\n- Dart programming language\n- Understanding of mobile UI',
     ['Flutter', 'Dart', 'Android', 'iOS', 'REST API', 'Git']),

    (6, 6, 'information-technology',
     'QA Automation Engineer', 'full_time', '1-3', 'Bangalore',
     700000, 1200000,
     'Ensure quality of Swiggy\'s platform through automated testing.\n\nResponsibilities:\n- Write automated test cases\n- Maintain test frameworks\n- Report bugs\n\nRequirements:\n- Selenium or similar experience\n- Python or Java for test scripts\n- Understanding of CI/CD',
     ['Selenium', 'Python', 'Java', 'Git', 'CI/CD', 'Pytest']),

    (7, 7, 'design-ux',
     'UI/UX Designer', 'full_time', '1-3', 'Bangalore',
     700000, 1300000,
     'Design delightful user experiences for Myntra\'s fashion platform.\n\nResponsibilities:\n- Create wireframes and prototypes\n- Conduct user research\n- Collaborate with developers\n\nRequirements:\n- Proficiency in Figma\n- Portfolio of past work\n- Understanding of user psychology',
     ['Figma', 'Adobe XD', 'Photoshop', 'CSS']),

    (7, 7, 'web-development',
     'React Developer - Ecommerce', 'full_time', '1-3', 'Bangalore',
     800000, 1500000,
     'Build Myntra\'s frontend shopping experience used by millions of fashion lovers.\n\nResponsibilities:\n- Develop React components\n- Shopping cart and checkout flows\n- Performance optimization\n\nRequirements:\n- Strong React.js skills\n- Redux experience\n- Good eye for design',
     ['React', 'JavaScript', 'Redux', 'HTML', 'CSS', 'Tailwind CSS']),

    (0, 0, 'information-technology',
     'Node.js Backend Developer', 'full_time', '1-3', 'Chennai',
     700000, 1300000,
     'Build high-performance backend APIs using Node.js.\n\nKey Responsibilities:\n- Design RESTful APIs\n- Database optimization\n- Third-party integrations\n\nRequired:\n- Node.js and Express\n- MongoDB or MySQL\n- REST API design',
     ['Node.js', 'Express.js', 'MongoDB', 'REST API', 'JavaScript']),

    (1, 1, 'information-technology',
     'PHP Laravel Developer', 'full_time', '1-3', 'Pune',
     600000, 1100000,
     'Develop web applications using PHP and Laravel framework.\n\nResponsibilities:\n- Backend development\n- Database design\n- API development\n\nRequirements:\n- PHP and Laravel experience\n- MySQL knowledge\n- MVC pattern understanding',
     ['PHP', 'Laravel', 'MySQL', 'HTML', 'CSS', 'JavaScript', 'Git']),

    (2, 2, 'information-technology',
     'Fresher - Software Engineer Trainee', 'full_time', 'fresher', 'Bangalore',
     400000, 600000,
     'Great opportunity for fresh graduates to kickstart their IT career at Wipro.\n\nWhat you will learn:\n- Enterprise software development\n- Agile methodology\n- Professional coding standards\n\nRequirements:\n- B.Tech/BCA in CS or related\n- Basic programming knowledge\n- Good communication skills\n- Eagerness to learn',
     ['Python', 'Java', 'C++', 'HTML', 'CSS', 'Git']),

    (3, 3, 'information-technology',
     'Site Reliability Engineer', 'full_time', '3-5', 'Hyderabad',
     1800000, 3000000,
     'Keep Amazon\'s services running at 99.99% uptime as an SRE.\n\nResponsibilities:\n- Incident response and resolution\n- Capacity planning\n- Automation of manual tasks\n\nRequirements:\n- Strong Linux skills\n- Python or Go for automation\n- Monitoring tools experience',
     ['Linux', 'Python', 'AWS', 'Docker', 'Kubernetes', 'CI/CD']),

    (4, 4, 'information-technology',
     'Product Manager - Tech', 'full_time', '3-5', 'Bangalore',
     2000000, 3500000,
     'Drive product vision and strategy for Google\'s enterprise products.\n\nResponsibilities:\n- Define product roadmap\n- Work with engineering and design\n- Analyze user feedback\n\nRequirements:\n- Technical background\n- Strong analytical skills\n- Experience in product management',
     ['Agile', 'JIRA', 'Scrum', 'Data Analysis', 'Communication', 'Leadership']),

    (5, 5, 'information-technology',
     'Database Administrator', 'full_time', '3-5', 'Gurugram',
     1000000, 1800000,
     'Manage and optimize Zomato\'s databases handling millions of transactions daily.\n\nResponsibilities:\n- Database performance tuning\n- Backup and recovery\n- Query optimization\n\nRequirements:\n- MySQL and PostgreSQL expertise\n- Experience with Redis\n- Performance tuning skills',
     ['MySQL', 'PostgreSQL', 'Redis', 'MongoDB', 'Linux']),

    (6, 6, 'marketing',
     'Digital Marketing Executive', 'full_time', '0-1', 'Bangalore',
     300000, 600000,
     'Drive digital marketing campaigns for Swiggy\'s growth.\n\nResponsibilities:\n- Manage social media\n- Email marketing campaigns\n- SEO/SEM\n\nRequirements:\n- Understanding of digital marketing\n- Google Ads knowledge\n- Content creation skills',
     ['Communication', 'Leadership', 'Problem Solving']),

    (7, 7, 'information-technology',
     'React Native Developer', 'full_time', '1-3', 'Bangalore',
     900000, 1600000,
     'Build Myntra\'s cross-platform mobile shopping app using React Native.\n\nResponsibilities:\n- Feature development\n- Performance optimization\n- Integration with APIs\n\nRequirements:\n- React Native experience\n- JavaScript/TypeScript\n- App Store deployment',
     ['React Native', 'JavaScript', 'TypeScript', 'REST API', 'Git']),

    (0, 0, 'information-technology',
     'Cyber Security Analyst', 'full_time', '1-3', 'Mumbai',
     900000, 1600000,
     'Protect TCS and client infrastructure from cyber threats.\n\nResponsibilities:\n- Security monitoring\n- Vulnerability assessment\n- Incident response\n\nRequirements:\n- Knowledge of security tools\n- Networking fundamentals\n- Security certifications preferred',
     ['Linux', 'Python', 'Git', 'Problem Solving']),

    (1, 1, 'web-development',
     'Django REST API Developer', 'contract', '1-3', 'Remote',
     700000, 1200000,
     'Build and maintain REST APIs using Django REST Framework.\n\nThis is a 6-month contract with possibility of extension.\n\nRequirements:\n- Django and DRF experience\n- PostgreSQL knowledge\n- JWT authentication',
     ['Python', 'Django', 'REST API', 'PostgreSQL', 'Docker']),

    (2, 2, 'information-technology',
     'Salesforce Developer', 'full_time', '1-3', 'Hyderabad',
     800000, 1400000,
     'Develop Salesforce solutions for enterprise clients.\n\nResponsibilities:\n- Apex development\n- Lightning components\n- Salesforce integrations\n\nRequirements:\n- Salesforce certifications preferred\n- Apex and SOQL knowledge\n- REST API integration',
     ['JavaScript', 'REST API', 'Communication']),

    (3, 3, 'information-technology',
     'Golang Backend Developer', 'full_time', '3-5', 'Hyderabad',
     1500000, 2500000,
     'Build high-performance microservices in Go for Amazon\'s backend systems.\n\nResponsibilities:\n- Microservices development\n- Performance optimization\n- API design\n\nRequirements:\n- Proficiency in Go\n- Microservices experience\n- Docker/Kubernetes',
     ['REST API', 'Docker', 'Kubernetes', 'Microservices', 'MySQL', 'Git']),

    (4, 4, 'information-technology',
     'Technical Writer', 'part_time', '0-1', 'Remote',
     200000, 400000,
     'Create clear and comprehensive technical documentation for Google\'s developer products.\n\nResponsibilities:\n- API documentation\n- Developer guides\n- Release notes\n\nRequirements:\n- Excellent English writing\n- Basic technical knowledge\n- Markdown familiarity',
     ['Communication', 'Git', 'Problem Solving']),

    (5, 5, 'information-technology',
     'Internship - Software Engineer', 'internship', 'fresher', 'Gurugram',
     30000, 50000,
     'Six-month internship for final year students at Zomato.\n\nWhat you will do:\n- Work on real features\n- Learn from senior engineers\n- Attend tech talks\n\nRequirements:\n- Final year B.Tech student\n- Any programming language\n- Problem-solving skills',
     ['Python', 'JavaScript', 'Git', 'Problem Solving']),
]

jobs = []
for (co_idx, re_idx, cat_slug, title, jtype, exp, loc, min_sal, max_sal, desc, skill_names) in jobs_data:
    base_slug = slugify(title)
    slug = base_slug
    c = 1
    while Job.objects.filter(slug=slug).exists():
        slug = f'{base_slug}-{c}'; c += 1

    job = Job.objects.create(
        recruiter=recruiters[re_idx],
        company=companies[co_idx],
        category=categories[cat_slug],
        title=title, slug=slug,
        description=desc,
        job_type=jtype,
        experience_required=exp,
        location=loc,
        min_salary=min_sal,
        max_salary=max_sal,
        is_salary_disclosed=True,
        num_openings=3,
        is_active=True,
        is_approved=True,
        is_featured=(co_idx in [3, 4]),
    )
    for sk_name in skill_names:
        if sk_name in skill_objs:
            JobSkillMapping.objects.get_or_create(job=job, skill=skill_objs[sk_name])
    jobs.append(job)

print(f"  Created {len(jobs)} jobs")

# ─── CANDIDATE PROFILES ──────────────────────────────────────────────────────
profiles_data = [
    # (user_idx, headline, city, experience, exp_salary, skills, edu_degree, edu_field, edu_inst, work_co, work_role)
    (0, 'Senior Python Developer | Django Expert | 4 Years',
     'Chennai', 4.0, 2000000, ['Python', 'Django', 'REST API', 'MySQL', 'Git', 'Docker'],
     'B.Tech', 'Computer Science', 'Anna University',
     'Cognizant Technology Solutions', 'Software Engineer'),

    (1, 'Full Stack Developer | React + Node.js | 3 Years',
     'Bangalore', 3.0, 1500000, ['React', 'Node.js', 'JavaScript', 'MySQL', 'HTML', 'CSS'],
     'B.Tech', 'Information Technology', 'VIT University',
     'HCL Technologies', 'Full Stack Developer'),

    (2, 'Machine Learning Engineer | AI Enthusiast | 3 Years',
     'Bangalore', 3.5, 2500000, ['Python', 'Machine Learning', 'TensorFlow', 'Pandas', 'NumPy'],
     'M.Tech', 'Artificial Intelligence', 'IIT Madras',
     'MuSigma', 'Data Scientist'),

    (3, 'Data Analyst | Power BI | Python | Excel Expert',
     'Pune', 2.0, 900000, ['Data Analysis', 'Python', 'Power BI', 'Excel', 'MySQL'],
     'BCA', 'Computer Applications', 'Pune University',
     'Capgemini', 'Junior Analyst'),

    (4, 'DevOps Engineer | AWS Certified | Docker | K8s',
     'Hyderabad', 4.0, 2000000, ['AWS', 'Docker', 'Kubernetes', 'CI/CD', 'Linux', 'Python'],
     'B.Tech', 'Computer Science', 'BITS Pilani',
     'Accenture', 'DevOps Engineer'),

    (5, 'Java Developer | Spring Boot | Microservices | 2 Years',
     'Noida', 2.0, 1100000, ['Java', 'Spring Boot', 'MySQL', 'REST API', 'Git'],
     'B.Tech', 'Computer Science', 'NIT Trichy',
     'Tech Mahindra', 'Java Developer'),

    (6, 'Android Developer | Kotlin | 2 Years Experience',
     'Gurugram', 2.0, 1200000, ['Android', 'Kotlin', 'Java', 'REST API', 'Git'],
     'B.Tech', 'Electronics & CS', 'DTU Delhi',
     'Paytm', 'Android Developer'),

    (7, 'UI/UX Designer | Figma Expert | 3 Years',
     'Bangalore', 3.0, 1100000, ['Figma', 'Adobe XD', 'Photoshop', 'CSS'],
     'B.Des', 'Interaction Design', 'NID Ahmedabad',
     'Flipkart', 'UI/UX Designer'),

    (8, 'React Frontend Developer | 2 Years | Redux',
     'Bangalore', 2.0, 1300000, ['React', 'JavaScript', 'TypeScript', 'HTML', 'CSS', 'Redux'],
     'B.Tech', 'Computer Science', 'Manipal University',
     'Razorpay', 'Frontend Developer'),

    (9, 'QA Engineer | Selenium | Python | Automation',
     'Bangalore', 3.0, 1100000, ['Selenium', 'Python', 'Java', 'Git', 'CI/CD'],
     'B.Tech', 'Information Technology', 'SRM University',
     'Mindtree', 'QA Engineer'),

    (10, 'PHP Laravel Developer | 2 Years | REST APIs',
     'Pune', 2.0, 900000, ['PHP', 'Laravel', 'MySQL', 'JavaScript', 'HTML', 'CSS'],
     'B.Tech', 'Computer Science', 'Pune University',
     'Persistent Systems', 'Web Developer'),

    (11, 'Fresh Graduate | Python | Looking for First Job',
     'Chennai', 0, 500000, ['Python', 'Java', 'HTML', 'CSS', 'Git'],
     'B.Tech', 'Computer Science', 'Anna University',
     None, None),
]

profiles = []
for idx, (u_idx, headline, city, exp, exp_sal, skill_list, degree, field, inst, work_co, work_role) in enumerate(profiles_data):
    p = CandidateProfile.objects.create(
        user=candidates[u_idx],
        headline=headline,
        city=city,
        state='Tamil Nadu' if city == 'Chennai' else 'Karnataka',
        total_experience=exp,
        expected_salary=exp_sal,
        summary=f"Experienced professional with {exp} years of experience. {headline}.",
        notice_period='30',
        preferred_locations='Bangalore,Chennai,Hyderabad,Remote',
        linkedin_url=f'https://linkedin.com/in/{slugify(candidates[u_idx].get_full_name())}',
        github_url=f'https://github.com/{slugify(candidates[u_idx].get_full_name())}',
    )
    # Add skills
    for skill_name in skill_list:
        CandidateSkill.objects.create(
            candidate=p, skill_name=skill_name,
            proficiency='advanced', years_of_experience=max(1, int(exp)),
        )
    # Add education
    Education.objects.create(
        candidate=p, degree=degree, field_of_study=field,
        institution=inst, start_year=2016, end_year=2020,
        percentage=75.5, is_current=False,
    )
    # Add work experience
    if work_co:
        from datetime import date
        WorkExperience.objects.create(
            candidate=p, company_name=work_co, designation=work_role,
            location=city, start_date=date(2021, 7, 1),
            end_date=None, is_current=True,
            description=f'Working as {work_role} at {work_co}. Responsible for development and maintenance of software systems.',
        )
    profiles.append(p)

print(f"  Created {len(profiles)} candidate profiles")

# ─── APPLICATIONS ────────────────────────────────────────────────────────────
applications_data = [
    # (candidate_idx, job_idx, status, cover_letter)
    (0, 0, 'shortlisted',      'I am highly interested in this role. I have 4 years of Python and Django experience.'),
    (0, 1, 'under_review',     'I have worked on multiple full stack projects using React and Node.js.'),
    (0, 4, 'applied',          'I am interested in DevOps and have been learning Docker and Kubernetes.'),
    (1, 1, 'interview_scheduled', 'I have extensive experience building full stack applications.'),
    (1, 9, 'shortlisted',      'React is my primary skill and I have 3 years of professional experience.'),
    (1, 15, 'applied',         'I would love to work on Myntra\'s React platform.'),
    (2, 2, 'selected',         'My ML background at MuSigma makes me a great fit for this role.'),
    (2, 8, 'shortlisted',      'I am passionate about AI research and would love to work at Google.'),
    (3, 3, 'under_review',     'I have strong data analysis skills using Python and Power BI.'),
    (3, 1, 'applied',          'I am looking to transition into full stack development.'),
    (4, 4, 'interview_scheduled', 'AWS certified with hands-on Kubernetes experience.'),
    (4, 7, 'under_review',     'Cloud architecture is my specialty.'),
    (5, 5, 'shortlisted',      'Spring Boot microservices is my core expertise.'),
    (5, 6, 'applied',          'I would love the challenge of working at Amazon scale.'),
    (6, 11, 'under_review',    'Android development with Kotlin is my main skill.'),
    (6, 12, 'applied',         'I want to expand into Flutter development.'),
    (7, 14, 'shortlisted',     'Figma expert with strong portfolio of e-commerce designs.'),
    (7, 15, 'applied',         'I can design and implement beautiful React UIs.'),
    (8, 9, 'interview_scheduled', 'I love building performant React applications.'),
    (8, 15, 'under_review',    'E-commerce frontend is my passion.'),
    (9, 13, 'applied',         'Selenium automation with Python is my strongest skill.'),
    (9, 4, 'under_review',     'I want to move into DevOps and have been learning CI/CD.'),
    (10, 17, 'shortlisted',    'Laravel is my primary framework with 2 years experience.'),
    (10, 16, 'applied',        'I am expanding my skills to Node.js and Express.'),
    (11, 18, 'applied',        'I am a fresh graduate eager to start my software career at Wipro.'),
    (11, 29, 'under_review',   'Internship at Zomato would be a dream start to my career.'),
]

applications = []
for (c_idx, j_idx, status, cover) in applications_data:
    if j_idx < len(jobs):
        app = Application.objects.create(
            candidate=candidates[c_idx],
            job=jobs[j_idx],
            cover_letter=cover,
            status=status,
            is_seen_by_recruiter=(status != 'applied'),
        )
        ApplicationStatusHistory.objects.create(
            application=app, status='applied', changed_by=candidates[c_idx], notes='Application submitted'
        )
        if status != 'applied':
            ApplicationStatusHistory.objects.create(
                application=app, status=status, changed_by=jobs[j_idx].recruiter, notes='Status updated by recruiter'
            )
        applications.append(app)

print(f"  Created {len(applications)} applications")

# ─── NOTIFICATIONS ───────────────────────────────────────────────────────────
for app in applications[:10]:
    if app.status == 'shortlisted':
        Notification.objects.create(
            recipient=app.candidate,
            title=f'You were shortlisted for {app.job.title}',
            message=f'Congratulations! {app.job.company.name} has shortlisted your application.',
            notification_type='shortlist',
            link='/applications/my-applications/',
        )
    elif app.status == 'interview_scheduled':
        Notification.objects.create(
            recipient=app.candidate,
            title=f'Interview scheduled for {app.job.title}',
            message=f'{app.job.company.name} has scheduled an interview with you.',
            notification_type='interview',
            link='/applications/my-applications/',
        )
    elif app.status == 'selected':
        Notification.objects.create(
            recipient=app.candidate,
            title=f'🎉 You are selected for {app.job.title}',
            message=f'Congratulations! You have been selected at {app.job.company.name}.',
            notification_type='general',
            link='/applications/my-applications/',
        )

print(f"  Created notifications")

# ─── SUMMARY ─────────────────────────────────────────────────────────────────
print("\n" + "="*55)
print("  SAMPLE DATA LOADED SUCCESSFULLY")
print("="*55)
print(f"  Admin          : admin@jobportal.com / Admin@123")
print(f"  Recruiters     : hr@tcs.com, hr@infosys.com, hr@google.com ... / Recruiter@123")
print(f"  Candidates     : arun.kumar@gmail.com, divya.menon@gmail.com ... / Candidate@123")
print(f"  Companies      : {Company.objects.count()}")
print(f"  Job Categories : {JobCategory.objects.count()}")
print(f"  Jobs           : {Job.objects.count()}")
print(f"  Skills         : {JobSkill.objects.count()}")
print(f"  Applications   : {Application.objects.count()}")
print(f"  Notifications  : {Notification.objects.count()}")
print("="*55)
print("\n  Open: http://127.0.0.1:8000")
print("  Admin: http://127.0.0.1:8000/admin\n")