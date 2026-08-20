from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.files.base import ContentFile
from datetime import timedelta, date, time
from decimal import Decimal
import io

from accounts.models import User
from students.models import StudentProfile, Project, Certification, Experience
from recruiters.models import Company, RecruiterProfile
from opportunities.models import Opportunity, SavedOpportunity
from applications.models import Application
from interviews.models import Interview
from notifications.models import Notification


def generate_dummy_pdf_content(student_name, skills_str):
    """
    Generates a valid raw PDF byte stream with text for pypdf indexing.
    """
    content = (
        f"%PDF-1.4\n"
        f"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        f"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        f"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n"
        f"4 0 obj << /Length 120 >> stream\n"
        f"BT /F1 12 Tf 50 700 Td ({student_name} Resume - Skills: {skills_str}) Tj ET\n"
        f"endstream\n"
        f"endobj\n"
        f"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
        f"xref\n"
        f"0 6\n"
        f"0000000000 65535 f \n"
        f"0000000010 00000 n \n"
        f"0000000060 00000 n \n"
        f"0000000117 00000 n \n"
        f"0000000234 00000 n \n"
        f"0000000406 00000 n \n"
        f"trailer << /Size 6 /Root 1 0 R >>\n"
        f"startxref\n"
        f"476\n"
        f"%%EOF\n"
    )
    return content.encode('utf-8')


class Command(BaseCommand):
    help = 'Seeds database with realistic demo students, recruiters, companies, opportunities, applications, and interviews.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Starting database seed for InternWorld...'))

        # 1. Create Superuser / Admin
        admin_user, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'username': 'admin@example.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'phone': '+91 9000000001',
            }
        )
        admin_user.set_password('Admin@12345')
        admin_user.save()
        self.stdout.write(self.style.SUCCESS(f'Created Admin: {admin_user.email} (Password: Admin@12345)'))

        # 2. Create Companies & Recruiters
        companies_data = [
            {
                'name': 'Google Cloud India',
                'industry': 'Cloud & Enterprise Computing',
                'website': 'https://cloud.google.com',
                'location': 'Bangalore, Karnataka',
                'description': 'Google Cloud provides organizations with leading infrastructure, platform capabilities, and AI solutions.',
                'recruiter_name': ('Sundar', 'Rajan'),
                'recruiter_email': 'recruiter@example.com',
                'designation': 'Staff University Recruiter',
            },
            {
                'name': 'Microsoft India Development Center',
                'industry': 'Software & Cloud Services',
                'website': 'https://www.microsoft.com',
                'location': 'Hyderabad, Telangana',
                'description': 'Microsoft IDC is one of Microsoft’s largest R&D centers outside Redmond, driving world-class products.',
                'recruiter_name': ('Ananya', 'Deshmukh'),
                'recruiter_email': 'microsoft.recruiter@example.com',
                'designation': 'Lead Campus Talent Specialist',
            },
            {
                'name': 'Amazon Web Services (AWS)',
                'industry': 'Cloud Computing & AI',
                'website': 'https://aws.amazon.com',
                'location': 'Bangalore, Karnataka',
                'description': 'AWS is the world’s most comprehensive and broadly adopted cloud offering millions of customers solutions.',
                'recruiter_name': ('Vikram', 'Malhotra'),
                'recruiter_email': 'amazon.recruiter@example.com',
                'designation': 'Senior Technical Recruiter',
            },
            {
                'name': 'Infosys Technologies',
                'industry': 'IT Services & Consulting',
                'website': 'https://www.infosys.com',
                'location': 'Pune, Maharashtra',
                'description': 'Infosys is a global leader in next-generation digital services and consulting.',
                'recruiter_name': ('Kavita', 'Nair'),
                'recruiter_email': 'infosys.recruiter@example.com',
                'designation': 'Campus Placement Lead',
            },
            {
                'name': 'TechCorp AI Innovations',
                'industry': 'Artificial Intelligence & Robotics',
                'website': 'https://techcorp-ai.example.com',
                'location': 'Bangalore, Karnataka',
                'description': 'Building foundational multimodal generative AI agents and autonomous enterprise automation systems.',
                'recruiter_name': ('Rohan', 'Verma'),
                'recruiter_email': 'techcorp.recruiter@example.com',
                'designation': 'Head of People & Culture',
            },
        ]

        recruiter_users = []
        created_companies = []

        for c_data in companies_data:
            company, _ = Company.objects.get_or_create(
                name=c_data['name'],
                defaults={
                    'industry': c_data['industry'],
                    'website': c_data['website'],
                    'location': c_data['location'],
                    'description': c_data['description'],
                    'verification_status': Company.VerificationStatus.VERIFIED,
                    'verified_at': timezone.now(),
                }
            )
            created_companies.append(company)

            r_user, _ = User.objects.get_or_create(
                email=c_data['recruiter_email'],
                defaults={
                    'username': c_data['recruiter_email'],
                    'first_name': c_data['recruiter_name'][0],
                    'last_name': c_data['recruiter_name'][1],
                    'role': User.Role.RECRUITER,
                    'phone': '+91 9800000000',
                }
            )
            r_user.set_password('Recruiter@12345')
            r_user.save()
            recruiter_users.append(r_user)

            RecruiterProfile.objects.update_or_create(
                user=r_user,
                defaults={
                    'company': company,
                    'designation': c_data['designation'],
                    'department': 'Talent Acquisition & Campus Relations',
                }
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(created_companies)} Companies and {len(recruiter_users)} Recruiters.'))

        # 3. Create 10 Students with complete profiles
        students_data = [
            {
                'email': 'student@example.com',
                'name': ('Aarav', 'Sharma'),
                'college': 'National Institute of Technology, Trichy',
                'degree': 'B.Tech',
                'department': 'Computer Science and Engineering',
                'year': 2025,
                'cgpa': Decimal('8.85'),
                'skills': 'Python, Django, React, PostgreSQL, Docker, Git, REST API',
                'soft_skills': 'Problem Solving, Communication, Leadership',
                'bio': 'Passionate full-stack Python and Django developer with deep interest in distributed systems, backend architectures, and modern web applications.',
                'pref_role': 'Full Stack Developer, Backend Engineer',
                'pref_loc': 'Bangalore, Hyderabad, Remote',
                'projects': [
                    {'title': 'Campus Placement Automation Platform', 'tech': 'Django, PostgreSQL, Bootstrap 5', 'desc': 'Engineered real-time recruitment pipeline with candidate compatibility scoring.'},
                    {'title': 'Distributed Task Queue System', 'tech': 'Python, Redis, Docker', 'desc': 'Asynchronous job worker processing 10k background tasks per minute.'}
                ]
            },
            {
                'email': 'riya.patel@example.com',
                'name': ('Riya', 'Patel'),
                'college': 'Birla Institute of Technology and Science (BITS), Pilani',
                'degree': 'B.Tech',
                'department': 'Information Technology',
                'year': 2025,
                'cgpa': Decimal('9.15'),
                'skills': 'Python, PyTorch, Scikit-learn, TensorFlow, Data Analysis, SQL, Pandas',
                'soft_skills': 'Analytical Thinking, Teamwork',
                'bio': 'AI/ML Enthusiast dedicated to developing transformer-based natural language models and scalable data pipelines.',
                'pref_role': 'Machine Learning Engineer, Data Scientist',
                'pref_loc': 'Bangalore, Pune',
                'projects': [
                    {'title': 'Resume Skill Extractor & Matcher', 'tech': 'Python, spaCy, PyPDF', 'desc': 'Automated information extraction parser analyzing semantic similarity across tech resumes.'}
                ]
            },
            {
                'email': 'karthik.iyer@example.com',
                'name': ('Karthik', 'Iyer'),
                'college': 'Indian Institute of Information Technology (IIIT), Hyderabad',
                'degree': 'B.Tech',
                'department': 'Computer Science and Engineering',
                'year': 2025,
                'cgpa': Decimal('8.60'),
                'skills': 'JavaScript, React, Vue.js, TypeScript, HTML5, CSS3, TailwindCSS, Next.js',
                'soft_skills': 'UI/UX Design, Agile Methodologies',
                'bio': 'Frontend engineer obsessed with high-performance responsive web apps, accessibility, and micro-frontends.',
                'pref_role': 'Frontend Developer, UI/UX Engineer',
                'pref_loc': 'Bangalore, Chennai, Remote',
                'projects': [
                    {'title': 'Enterprise Analytics Dashboard', 'tech': 'React, Chart.js, Tailwind', 'desc': 'Interactive analytics dashboard visualizing real-time financial telemetry.'}
                ]
            },
            {
                'email': 'sneha.reddy@example.com',
                'name': ('Sneha', 'Reddy'),
                'college': 'Vellore Institute of Technology (VIT), Vellore',
                'degree': 'B.Tech',
                'department': 'Electronics and Communication Engineering',
                'year': 2026,
                'cgpa': Decimal('7.90'),
                'skills': 'AWS, Docker, Kubernetes, Linux, Terraform, CI/CD, Python, Bash',
                'soft_skills': 'Systems Troubleshooting, Reliability Engineering',
                'bio': 'Aspiring Cloud & DevOps Engineer specializing in container orchestration, infrastructure as code, and automated deployment pipelines.',
                'pref_role': 'DevOps Engineer, Cloud Architect Intern',
                'pref_loc': 'Hyderabad, Bangalore',
                'projects': [
                    {'title': 'Multi-Cloud Kubernetes Deployment', 'tech': 'Kubernetes, Terraform, AWS', 'desc': 'Automated zero-downtime microservices cluster provisioning with monitoring.'}
                ]
            },
            {
                'email': 'varun.sen@example.com',
                'name': ('Varun', 'Sen'),
                'college': 'Delhi Technological University (DTU)',
                'degree': 'MCA',
                'department': 'Computer Applications',
                'year': 2025,
                'cgpa': Decimal('8.30'),
                'skills': 'Java, Spring Boot, MySQL, Microservices, Kafka, Hibernate, REST API',
                'soft_skills': 'Critical Thinking, Persistence',
                'bio': 'Backend developer with strong foundations in object-oriented design patterns, enterprise Java, and event-driven messaging.',
                'pref_role': 'Java Backend Developer, Software Engineer',
                'pref_loc': 'Delhi NCR, Noida, Gurgaon',
                'projects': [
                    {'title': 'E-Commerce Order Processing Engine', 'tech': 'Spring Boot, Kafka, MySQL', 'desc': 'Resilient distributed payment and inventory processing system.'}
                ]
            },
            {
                'email': 'meera.joshi@example.com',
                'name': ('Meera', 'Joshi'),
                'college': 'College of Engineering, Pune (COEP)',
                'degree': 'B.Tech',
                'department': 'Computer Science and Engineering',
                'year': 2025,
                'cgpa': Decimal('9.40'),
                'skills': 'Python, C++, Data Structures, Algorithms, SQL, Django, Machine Learning',
                'soft_skills': 'Competitive Programming, Communication',
                'bio': 'Gold medalist academic and competitive coder with strong problem-solving skills across algorithmic challenges and systems programming.',
                'pref_role': 'Software Development Engineer (SDE-1)',
                'pref_loc': 'Bangalore, Mumbai, Pune',
                'projects': [
                    {'title': 'High-Throughput Graph Shortest-Path Engine', 'tech': 'C++, Multithreading', 'desc': 'Parallelized transit route optimizer handling 1M node network graphs.'}
                ]
            },
            {
                'email': 'aditya.singh@example.com',
                'name': ('Aditya', 'Singh'),
                'college': 'PSG College of Technology, Coimbatore',
                'degree': 'B.Tech',
                'department': 'Information Technology',
                'year': 2026,
                'cgpa': Decimal('7.75'),
                'skills': 'Flutter, Dart, Firebase, Android, iOS, REST API, SQLite',
                'soft_skills': 'Product Management, Mobile UI Design',
                'bio': 'Cross-platform mobile app architect crafting seamless mobile experiences for both iOS and Android platforms.',
                'pref_role': 'Mobile App Developer, Flutter Engineer',
                'pref_loc': 'Chennai, Bangalore, Remote',
                'projects': [
                    {'title': 'Campus Events & Community App', 'tech': 'Flutter, Firebase, Cloud Functions', 'desc': 'Social calendar and notification hub for 12,000 university students.'}
                ]
            },
            {
                'email': 'pooja.hegde@example.com',
                'name': ('Pooja', 'Hegde'),
                'college': 'Manipal Institute of Technology (MIT)',
                'degree': 'B.Tech',
                'department': 'Data Science and Engineering',
                'year': 2025,
                'cgpa': Decimal('8.70'),
                'skills': 'Python, SQL, Tableau, PowerBI, Data Visualization, Excel, Statistics',
                'soft_skills': 'Business Acumen, Presentation Skills',
                'bio': 'Data Analyst extracting meaningful business insights from complex, messy datasets through visual dashboards and predictive modeling.',
                'pref_role': 'Business Analyst, Data Analyst Intern',
                'pref_loc': 'Bangalore, Mumbai',
                'projects': [
                    {'title': 'University Placement Trends & Salary Forecaster', 'tech': 'Python, Tableau, Regression', 'desc': 'Analyzed 5-year campus placement statistics to identify industry demand patterns.'}
                ]
            },
            {
                'email': 'nikhil.das@example.com',
                'name': ('Nikhil', 'Das'),
                'college': 'Jadavpur University, Kolkata',
                'degree': 'B.Tech',
                'department': 'Computer Science and Engineering',
                'year': 2025,
                'cgpa': Decimal('8.55'),
                'skills': 'Cybersecurity, Ethical Hacking, Linux, Network Security, Python, Wireshark, Cryptography',
                'soft_skills': 'Attention to Detail, Ethical Judgement',
                'bio': 'Cybersecurity enthusiast passionate about vulnerability assessments, penetration testing, and secure software architecture.',
                'pref_role': 'Security Analyst, Security Engineer Intern',
                'pref_loc': 'Kolkata, Bangalore, Remote',
                'projects': [
                    {'title': 'Automated Web Vulnerability Scanner', 'tech': 'Python, Requests, BeautifulSoup', 'desc': 'Engineered scanner targeting OWASP Top 10 security misconfigurations.'}
                ]
            },
            {
                'email': 'tanvi.gupta@example.com',
                'name': ('Tanvi', 'Gupta'),
                'college': 'Thapar Institute of Engineering and Technology',
                'degree': 'B.Tech',
                'department': 'Computer Science and Engineering',
                'year': 2026,
                'cgpa': Decimal('8.20'),
                'skills': 'Python, Selenium, PyTest, QA Automation, Postman, JIRA, CI/CD',
                'soft_skills': 'Quality Assurance, Test Planning, Documentation',
                'bio': 'QA automation engineer focusing on end-to-end regression frameworks, API testing, and performance validation.',
                'pref_role': 'SDET Intern, QA Engineer',
                'pref_loc': 'Chandigarh, Delhi NCR, Remote',
                'projects': [
                    {'title': 'Full-Stack E2E Automated Test Suite', 'tech': 'PyTest, Selenium, GitHub Actions', 'desc': 'Automated 120 regression scenarios integrated with continuous delivery.'}
                ]
            },
        ]

        student_users = []
        for s_data in students_data:
            s_user, _ = User.objects.get_or_create(
                email=s_data['email'],
                defaults={
                    'username': s_data['email'],
                    'first_name': s_data['name'][0],
                    'last_name': s_data['name'][1],
                    'role': User.Role.STUDENT,
                    'phone': '+91 9700000000',
                }
            )
            s_user.set_password('Student@12345')
            s_user.save()
            student_users.append(s_user)

            # Generate and attach PDF resume
            pdf_bytes = generate_dummy_pdf_content(f"{s_data['name'][0]} {s_data['name'][1]}", s_data['skills'])
            pdf_file = ContentFile(pdf_bytes, name=f"{s_user.username}_resume.pdf")

            profile, _ = StudentProfile.objects.update_or_create(
                user=s_user,
                defaults={
                    'college': s_data['college'],
                    'degree': s_data['degree'],
                    'department': s_data['department'],
                    'graduation_year': s_data['year'],
                    'cgpa': s_data['cgpa'],
                    'skills': s_data['skills'],
                    'soft_skills': s_data['soft_skills'],
                    'bio': s_data['bio'],
                    'preferred_role': s_data['pref_role'],
                    'preferred_location': s_data['pref_loc'],
                    'resume': pdf_file,
                    'resume_extracted_text': f"Resume text for {s_data['name'][0]} {s_data['name'][1]}. Skills: {s_data['skills']}. Education: {s_data['degree']} in {s_data['department']} from {s_data['college']}.",
                    'github_url': f"https://github.com/{s_data['name'][0].lower()}{s_data['name'][1].lower()}",
                    'linkedin_url': f"https://linkedin.com/in/{s_data['name'][0].lower()}-{s_data['name'][1].lower()}",
                }
            )

            # Add projects
            for p in s_data.get('projects', []):
                Project.objects.get_or_create(
                    student=profile,
                    title=p['title'],
                    defaults={
                        'technologies': p['tech'],
                        'description': p['desc'],
                        'project_url': 'https://github.com/example/project'
                    }
                )

            # Add sample certification & experience
            Certification.objects.get_or_create(
                student=profile,
                name=f"Certified Specialist in {s_data['skills'].split(',')[0]}",
                defaults={
                    'issuing_organization': 'Professional Certification Institute',
                    'issue_date': date(2024, 6, 15),
                    'credential_url': 'https://cert.example.com/verify/12345'
                }
            )

            Experience.objects.get_or_create(
                student=profile,
                company='Tech Startup Labs',
                role='Software Intern',
                defaults={
                    'start_date': date(2024, 5, 1),
                    'end_date': date(2024, 7, 31),
                    'is_current': False,
                    'description': 'Assisted engineering team in microservice optimization and unit testing.'
                }
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(student_users)} Students with complete profiles and PDF resumes.'))

        # 4. Create 20 Opportunities (12 Internships, 8 Placements)
        opportunities_data = [
            # Google Cloud (recruiter_users[0], created_companies[0])
            {
                'recruiter': recruiter_users[0],
                'company': created_companies[0],
                'title': 'Full Stack Python & Django Developer Intern',
                'type': Opportunity.OpportunityType.INTERNSHIP,
                'role': 'Full Stack Developer',
                'desc': 'Join our Google Cloud platform developer tools team building modern management dashboards, backend APIs, and developer productivity plugins.',
                'resp': 'Design RESTful APIs, develop intuitive frontend views using Bootstrap and JavaScript, write high-coverage tests, and participate in code reviews.',
                'req': 'Strong knowledge of Python, Django, SQL databases, and web fundamentals. Good understanding of Git version control.',
                'skills': 'Python, Django, PostgreSQL, REST API, Git, JavaScript',
                'loc': 'Bangalore, Karnataka',
                'mode': Opportunity.WorkMode.HYBRID,
                'stipend': '₹45,000 / month',
                'salary': '',
                'dur': '6 Months',
                'min_cgpa': Decimal('7.50'),
                'deg': 'B.Tech, M.Tech, MCA',
                'dept': 'Computer Science, Information Technology',
                'grad': 2025,
                'openings': 3,
                'deadline': timezone.now().date() + timedelta(days=30),
            },
            {
                'recruiter': recruiter_users[0],
                'company': created_companies[0],
                'title': 'Cloud Infrastructure & DevOps Engineer (Full-Time)',
                'type': Opportunity.OpportunityType.PLACEMENT,
                'role': 'Cloud Engineer',
                'desc': 'Seeking brilliant graduates to manage resilient cloud architectures, Kubernetes clusters, and automated continuous delivery pipelines.',
                'resp': 'Architect cloud solutions, automate infrastructure using Terraform, monitor telemetry metrics, and maintain 99.99% uptime.',
                'req': 'Hands-on experience with Linux, AWS/GCP, Docker, Kubernetes, and scripting languages (Python/Bash).',
                'skills': 'AWS, Docker, Kubernetes, Linux, Terraform, Python, CI/CD',
                'loc': 'Bangalore, Karnataka',
                'mode': Opportunity.WorkMode.ON_SITE,
                'stipend': '',
                'salary': '₹16 - 22 LPA',
                'dur': 'Permanent Full-time',
                'min_cgpa': Decimal('7.80'),
                'deg': 'B.Tech, M.Tech',
                'dept': 'Computer Science, IT, Electronics',
                'grad': 2025,
                'openings': 2,
                'deadline': timezone.now().date() + timedelta(days=25),
            },
            {
                'recruiter': recruiter_users[0],
                'company': created_companies[0],
                'title': 'AI & Machine Learning Research Intern',
                'type': Opportunity.OpportunityType.INTERNSHIP,
                'role': 'Machine Learning Intern',
                'desc': 'Work alongside top AI researchers on state-of-the-art multimodal generative models and deep learning optimization.',
                'resp': 'Train deep neural networks, curate high-quality benchmark datasets, fine-tune models, and write technical reports.',
                'req': 'Strong background in Linear Algebra, Probability, Python, PyTorch/TensorFlow, and data manipulation libraries.',
                'skills': 'Python, PyTorch, Scikit-learn, TensorFlow, Data Analysis, SQL',
                'loc': 'Bangalore, Karnataka',
                'mode': Opportunity.WorkMode.REMOTE,
                'stipend': '₹50,000 / month',
                'salary': '',
                'dur': '6 Months',
                'min_cgpa': Decimal('8.50'),
                'deg': 'B.Tech, M.Tech, M.Sc',
                'dept': 'Computer Science, Data Science, IT',
                'grad': 2025,
                'openings': 2,
                'deadline': timezone.now().date() + timedelta(days=20),
            },
            {
                'recruiter': recruiter_users[0],
                'company': created_companies[0],
                'title': 'Frontend UI/UX Engineering Intern',
                'type': Opportunity.OpportunityType.INTERNSHIP,
                'role': 'Frontend Developer',
                'desc': 'Build accessible, pixel-perfect user interfaces and interactive data visualizers for millions of active cloud users.',
                'resp': 'Implement UI features using modern JavaScript/React, optimize web performance metrics, and build reusable UI components.',
                'req': 'Proficiency with HTML5, CSS3, JavaScript (ES6+), React or Vue, and responsive layout styling.',
                'skills': 'JavaScript, React, HTML5, CSS3, TailwindCSS, TypeScript',
                'loc': 'Hyderabad, Telangana',
                'mode': Opportunity.WorkMode.HYBRID,
                'stipend': '₹40,000 / month',
                'salary': '',
                'dur': '3 Months',
                'min_cgpa': Decimal('7.00'),
                'deg': 'All Degrees',
                'dept': 'All Departments',
                'grad': 2025,
                'openings': 4,
                'deadline': timezone.now().date() + timedelta(days=35),
            },

            # Microsoft (recruiter_users[1], created_companies[1])
            {
                'recruiter': recruiter_users[1],
                'company': created_companies[1],
                'title': 'Software Development Engineer - 1 (SDE-1 Placement)',
                'type': Opportunity.OpportunityType.PLACEMENT,
                'role': 'Software Engineer',
                'desc': 'Direct campus placement hiring for our core engineering teams working on Office 365, Teams, and Azure services.',
                'resp': 'Design modular software components, implement performant algorithms, review team code, and troubleshoot production issues.',
                'req': 'Exceptional problem-solving skills in Data Structures and Algorithms. Proficiency in C++, Java, or Python.',
                'skills': 'Python, C++, Data Structures, Algorithms, SQL, Java',
                'loc': 'Hyderabad, Telangana',
                'mode': Opportunity.WorkMode.HYBRID,
                'stipend': '',
                'salary': '₹18 - 24 LPA',
                'dur': 'Permanent Full-time',
                'min_cgpa': Decimal('8.00'),
                'deg': 'B.Tech, M.Tech, MCA',
                'dept': 'Computer Science, IT, Electronics',
                'grad': 2025,
                'openings': 5,
                'deadline': timezone.now().date() + timedelta(days=28),
            },
            {
                'recruiter': recruiter_users[1],
                'company': created_companies[1],
                'title': 'Data Analytics & Business Intelligence Intern',
                'type': Opportunity.OpportunityType.INTERNSHIP,
                'role': 'Data Analyst',
                'desc': 'Translate complex user behavioral data into actionable business intelligence dashboards and executive reports.',
                'resp': 'Build automated reporting pipelines, create interactive PowerBI/Tableau dashboards, and write complex analytical SQL queries.',
                'req': 'Proficiency in SQL, Python, Excel, PowerBI/Tableau, and statistical data modeling.',
                'skills': 'Python, SQL, Tableau, PowerBI, Data Visualization, Excel',
                'loc': 'Hyderabad, Telangana',
                'mode': Opportunity.WorkMode.HYBRID,
                'stipend': '₹38,000 / month',
                'salary': '',
                'dur': '6 Months',
                'min_cgpa': Decimal('7.50'),
                'deg': 'B.Tech, B.Sc, MCA, MBA',
                'dept': 'All Departments',
                'grad': 2025,
                'openings': 3,
                'deadline': timezone.now().date() + timedelta(days=15),
            },
            {
                'recruiter': recruiter_users[1],
                'company': created_companies[1],
                'title': 'Cybersecurity & Application Security Intern',
                'type': Opportunity.OpportunityType.INTERNSHIP,
                'role': 'Security Analyst',
                'desc': 'Protect millions of enterprise users by auditing security architectures, identifying vulnerabilities, and automating threat detection.',
                'resp': 'Perform code security audits, run dynamic penetration tests, develop security scanning tools, and investigate alerts.',
                'req': 'Fundamental knowledge of network security, OWASP Top 10, Linux, Python scripting, and cryptographic protocols.',
                'skills': 'Cybersecurity, Ethical Hacking, Linux, Network Security, Python',
                'loc': 'Bangalore, Karnataka',
                'mode': Opportunity.WorkMode.REMOTE,
                'stipend': '₹42,000 / month',
                'salary': '',
                'dur': '6 Months',
                'min_cgpa': Decimal('7.80'),
                'deg': 'B.Tech, M.Tech',
                'dept': 'Computer Science, IT, Cybersecurity',
                'grad': 2025,
                'openings': 2,
                'deadline': timezone.now().date() + timedelta(days=22),
            },
            {
                'recruiter': recruiter_users[1],
                'company': created_companies[1],
                'title': 'Software Development Engineer in Test (SDET Placement)',
                'type': Opportunity.OpportunityType.PLACEMENT,
                'role': 'SDET',
                'desc': 'Build scalable automated testing frameworks, load generation tools, and continuous validation pipelines.',
                'resp': 'Write automated integration & regression test suites, create test harness tools, and integrate tests with CI/CD.',
                'req': 'Experience in Python/Java, Selenium/Playwright, PyTest, REST API validation, and Git.',
                'skills': 'Python, Selenium, PyTest, QA Automation, Postman, CI/CD',
                'loc': 'Hyderabad, Telangana',
                'mode': Opportunity.WorkMode.ON_SITE,
                'stipend': '',
                'salary': '₹12 - 16 LPA',
                'dur': 'Permanent Full-time',
                'min_cgpa': Decimal('7.50'),
                'deg': 'B.Tech, MCA',
                'dept': 'Computer Science, Information Technology',
                'grad': 2025,
                'openings': 3,
                'deadline': timezone.now().date() + timedelta(days=18),
            },

            # Amazon AWS (recruiter_users[2], created_companies[2])
            {
                'recruiter': recruiter_users[2],
                'company': created_companies[2],
                'title': 'Backend Systems Development Intern (Python / Go)',
                'type': Opportunity.OpportunityType.INTERNSHIP,
                'role': 'Backend Engineer',
                'desc': 'Help build high-throughput, low-latency distributed microservices for AWS compute and storage services.',
                'resp': 'Implement scalable backend services, optimize database queries, write comprehensive unit tests, and debug concurrency bottlenecks.',
                'req': 'Solid understanding of backend frameworks (Django/Flask/FastAPI), SQL database indexing, and object-oriented principles.',
                'skills': 'Python, Django, PostgreSQL, Docker, REST API, Git',
                'loc': 'Bangalore, Karnataka',
                'mode': Opportunity.WorkMode.ON_SITE,
                'stipend': '₹48,000 / month',
                'salary': '',
                'dur': '6 Months',
                'min_cgpa': Decimal('8.00'),
                'deg': 'B.Tech, M.Tech',
                'dept': 'Computer Science, Information Technology',
                'grad': 2025,
                'openings': 4,
                'deadline': timezone.now().date() + timedelta(days=26),
            },
            {
                'recruiter': recruiter_users[2],
                'company': created_companies[2],
                'title': 'Cloud Support Associate (Placement)',
                'type': Opportunity.OpportunityType.PLACEMENT,
                'role': 'Cloud Engineer',
                'desc': 'Troubleshoot complex cloud architectures for enterprise customers leveraging AWS services worldwide.',
                'resp': 'Diagnose network configurations, container crashes, database locks, and advise customers on best architectural practices.',
                'req': 'Good understanding of Operating Systems (Linux), Computer Networks (DNS, TCP/IP), AWS services, and scripting.',
                'skills': 'AWS, Linux, Python, Docker, Network Security',
                'loc': 'Bangalore, Karnataka',
                'mode': Opportunity.WorkMode.HYBRID,
                'stipend': '',
                'salary': '₹14 - 18 LPA',
                'dur': 'Permanent Full-time',
                'min_cgpa': Decimal('7.00'),
                'deg': 'B.Tech, B.E, MCA',
                'dept': 'All Engineering Branches',
                'grad': 2025,
                'openings': 6,
                'deadline': timezone.now().date() + timedelta(days=40),
            },
            {
                'recruiter': recruiter_users[2],
                'company': created_companies[2],
                'title': 'Mobile Applications Development Intern (Flutter/React Native)',
                'type': Opportunity.OpportunityType.INTERNSHIP,
                'role': 'Mobile Developer',
                'desc': 'Build customer-facing mobile application features used by millions of delivery and warehouse partners globally.',
                'resp': 'Develop polished mobile screens in Flutter/React Native, integrate backend REST APIs, and manage offline data caching.',
                'req': 'Experience with Dart/Flutter or React Native, state management libraries, and REST APIs.',
                'skills': 'Flutter, Dart, Firebase, Android, REST API',
                'loc': 'Bangalore, Karnataka',
                'mode': Opportunity.WorkMode.HYBRID,
                'stipend': '₹35,000 / month',
                'salary': '',
                'dur': '4 Months',
                'min_cgpa': Decimal('7.20'),
                'deg': 'B.Tech, BCA, MCA',
                'dept': 'Computer Science, IT',
                'grad': 2026,
                'openings': 2,
                'deadline': timezone.now().date() + timedelta(days=19),
            },
            {
                'recruiter': recruiter_users[2],
                'company': created_companies[2],
                'title': 'Enterprise Java Developer (Full-Time Placement)',
                'type': Opportunity.OpportunityType.PLACEMENT,
                'role': 'Java Developer',
                'desc': 'Design and maintain high-volume transaction processing microservices on Spring Boot and AWS ECS.',
                'resp': 'Write clean enterprise Java code, maintain event queues on Apache Kafka, and optimize relational databases.',
                'req': 'Strong knowledge of Core Java, Spring Boot, JPA/Hibernate, SQL, and microservices architecture.',
                'skills': 'Java, Spring Boot, MySQL, Microservices, Kafka, Hibernate',
                'loc': 'Bangalore, Karnataka',
                'mode': Opportunity.WorkMode.ON_SITE,
                'stipend': '',
                'salary': '₹15 - 20 LPA',
                'dur': 'Permanent Full-time',
                'min_cgpa': Decimal('7.50'),
                'deg': 'B.Tech, MCA',
                'dept': 'Computer Science, IT',
                'grad': 2025,
                'openings': 4,
                'deadline': timezone.now().date() + timedelta(days=32),
            },

            # Infosys (recruiter_users[3], created_companies[3])
            {
                'recruiter': recruiter_users[3],
                'company': created_companies[3],
                'title': 'Systems Engineer Trainee (Campus Placement)',
                'type': Opportunity.OpportunityType.PLACEMENT,
                'role': 'Systems Engineer',
                'desc': 'Mass campus placement drive for engineering and computer application graduates across India.',
                'resp': 'Participate in our world-renowned Mysore training program in Full Stack Development, Cloud, and Enterprise Engineering.',
                'req': 'Graduating in 2025 from recognized engineering college. Sound analytical thinking and problem-solving aptitude.',
                'skills': 'Python, Java, SQL, HTML5, CSS3, JavaScript',
                'loc': 'Pune, Maharashtra',
                'mode': Opportunity.WorkMode.ON_SITE,
                'stipend': '',
                'salary': '₹6.5 - 9.5 LPA',
                'dur': 'Permanent Full-time',
                'min_cgpa': Decimal('6.50'),
                'deg': 'All Degrees',
                'dept': 'All Departments',
                'grad': 2025,
                'openings': 20,
                'deadline': timezone.now().date() + timedelta(days=45),
            },
            {
                'recruiter': recruiter_users[3],
                'company': created_companies[3],
                'title': 'Full Stack Web Development Intern',
                'type': Opportunity.OpportunityType.INTERNSHIP,
                'role': 'Web Developer',
                'desc': 'Hands-on live project internship building client portal prototypes using Django and React.',
                'resp': 'Build web pages, connect database endpoints, document APIs, and write clean unit test cases.',
                'req': 'Knowledge of HTML, CSS, JavaScript, Python, Django, and relational databases.',
                'skills': 'Python, Django, React, PostgreSQL, Git',
                'loc': 'Pune, Maharashtra',
                'mode': Opportunity.WorkMode.HYBRID,
                'stipend': '₹25,000 / month',
                'salary': '',
                'dur': '6 Months',
                'min_cgpa': Decimal('7.00'),
                'deg': 'B.Tech, BCA, MCA',
                'dept': 'Computer Science, IT',
                'grad': 2025,
                'openings': 8,
                'deadline': timezone.now().date() + timedelta(days=21),
            },
            {
                'recruiter': recruiter_users[3],
                'company': created_companies[3],
                'title': 'Data Science & Business Analytics Specialist (Placement)',
                'type': Opportunity.OpportunityType.PLACEMENT,
                'role': 'Data Scientist',
                'desc': 'Develop predictive statistical models, regression forecasters, and automated enterprise NLP summarization agents.',
                'resp': 'Clean and prepare big data sets, train statistical models, build analytics charts, and present insights to stakeholders.',
                'req': 'Degree in Data Science, Statistics, or Computer Science. Strong knowledge of Python, Pandas, SQL, and machine learning.',
                'skills': 'Python, Scikit-learn, SQL, Tableau, Pandas, Data Analysis',
                'loc': 'Bangalore, Karnataka',
                'mode': Opportunity.WorkMode.HYBRID,
                'stipend': '',
                'salary': '₹10 - 14 LPA',
                'dur': 'Permanent Full-time',
                'min_cgpa': Decimal('7.50'),
                'deg': 'B.Tech, M.Tech, M.Sc',
                'dept': 'Data Science, Computer Science, IT',
                'grad': 2025,
                'openings': 3,
                'deadline': timezone.now().date() + timedelta(days=29),
            },
            {
                'recruiter': recruiter_users[3],
                'company': created_companies[3],
                'title': 'Quality Assurance & Automated Testing Intern',
                'type': Opportunity.OpportunityType.INTERNSHIP,
                'role': 'QA Intern',
                'desc': 'Learn professional quality engineering methodologies, test design, and automated regression scripting.',
                'resp': 'Design test cases, execute manual tests, write Selenium automation scripts, and file bug reports on JIRA.',
                'req': 'Familiarity with software testing life cycle, basic Python or Java, and web browsers.',
                'skills': 'Python, Selenium, PyTest, QA Automation, Git',
                'loc': 'Pune, Maharashtra',
                'mode': Opportunity.WorkMode.ON_SITE,
                'stipend': '₹22,000 / month',
                'salary': '',
                'dur': '3 Months',
                'min_cgpa': Decimal('6.80'),
                'deg': 'B.Tech, BCA, MCA',
                'dept': 'All Departments',
                'grad': 2026,
                'openings': 5,
                'deadline': timezone.now().date() + timedelta(days=14),
            },

            # TechCorp AI (recruiter_users[4], created_companies[4])
            {
                'recruiter': recruiter_users[4],
                'company': created_companies[4],
                'title': 'Generative AI & LLM Systems Engineer Intern',
                'type': Opportunity.OpportunityType.INTERNSHIP,
                'role': 'AI Engineer',
                'desc': 'Build autonomous AI agents, retrieval-augmented generation (RAG) pipelines, and vector database embeddings.',
                'resp': 'Integrate LLM APIs, construct embedding vectors, benchmark reasoning accuracy, and optimize inference latencies.',
                'req': 'Expertise in Python, PyTorch/TensorFlow, vector databases (Pinecone/Chroma), and prompt engineering.',
                'skills': 'Python, PyTorch, TensorFlow, Scikit-learn, REST API, Git',
                'loc': 'Bangalore, Karnataka',
                'mode': Opportunity.WorkMode.REMOTE,
                'stipend': '₹55,000 / month',
                'salary': '',
                'dur': '6 Months',
                'min_cgpa': Decimal('8.00'),
                'deg': 'B.Tech, M.Tech, MS',
                'dept': 'Computer Science, AI, IT',
                'grad': 2025,
                'openings': 2,
                'deadline': timezone.now().date() + timedelta(days=17),
            },
            {
                'recruiter': recruiter_users[4],
                'company': created_companies[4],
                'title': 'Full Stack Product Engineer (Placement)',
                'type': Opportunity.OpportunityType.PLACEMENT,
                'role': 'Full Stack Developer',
                'desc': 'Take end-to-end ownership of fast-moving product features across our web platform, APIs, and microservices.',
                'resp': 'Develop responsive web applications, design performant database models, build APIs, and deploy cloud containers.',
                'req': 'Proficiency in Python, Django, React, PostgreSQL, Docker, and modern CI/CD tooling.',
                'skills': 'Python, Django, React, PostgreSQL, Docker, Git, REST API',
                'loc': 'Bangalore, Karnataka',
                'mode': Opportunity.WorkMode.HYBRID,
                'stipend': '',
                'salary': '₹15 - 22 LPA',
                'dur': 'Permanent Full-time',
                'min_cgpa': Decimal('7.80'),
                'deg': 'B.Tech, M.Tech, MCA',
                'dept': 'Computer Science, IT',
                'grad': 2025,
                'openings': 3,
                'deadline': timezone.now().date() + timedelta(days=24),
            },
            {
                'recruiter': recruiter_users[4],
                'company': created_companies[4],
                'title': 'Frontend React & UI Engineer Intern',
                'type': Opportunity.OpportunityType.INTERNSHIP,
                'role': 'Frontend Developer',
                'desc': 'Help create lightning-fast, beautiful generative AI workspace user interfaces in React and TypeScript.',
                'resp': 'Code interactive web interfaces, write modular components, optimize rendering performance, and integrate WebSockets.',
                'req': 'Hands-on experience with React, TypeScript, modern CSS, state management, and REST APIs.',
                'skills': 'JavaScript, React, TypeScript, HTML5, CSS3, TailwindCSS',
                'loc': 'Bangalore, Karnataka',
                'mode': Opportunity.WorkMode.REMOTE,
                'stipend': '₹40,000 / month',
                'salary': '',
                'dur': '3 Months',
                'min_cgpa': Decimal('7.50'),
                'deg': 'All Degrees',
                'dept': 'Computer Science, IT',
                'grad': 2025,
                'openings': 2,
                'deadline': timezone.now().date() + timedelta(days=12),
            },
            {
                'recruiter': recruiter_users[4],
                'company': created_companies[4],
                'title': 'Cloud DevOps & Site Reliability Engineer (Placement)',
                'type': Opportunity.OpportunityType.PLACEMENT,
                'role': 'DevOps Engineer',
                'desc': 'Oversee automated GPU cluster provisioning, cloud scalability, observability metrics, and automated deployments.',
                'resp': 'Manage Kubernetes clusters, automate infrastructure with Terraform, monitor latency, and maintain system security.',
                'req': 'Strong background in AWS/GCP, Docker, Kubernetes, Linux systems administration, and Terraform.',
                'skills': 'AWS, Docker, Kubernetes, Linux, Terraform, CI/CD, Python',
                'loc': 'Bangalore, Karnataka',
                'mode': Opportunity.WorkMode.HYBRID,
                'stipend': '',
                'salary': '₹16 - 24 LPA',
                'dur': 'Permanent Full-time',
                'min_cgpa': Decimal('7.50'),
                'deg': 'B.Tech, M.Tech',
                'dept': 'Computer Science, IT, Electronics',
                'grad': 2025,
                'openings': 2,
                'deadline': timezone.now().date() + timedelta(days=31),
            },
        ]

        created_opportunities = []
        for o_data in opportunities_data:
            opp, _ = Opportunity.objects.get_or_create(
                title=o_data['title'],
                company=o_data['company'],
                defaults={
                    'recruiter': o_data['recruiter'],
                    'opportunity_type': o_data['type'],
                    'job_role': o_data['role'],
                    'description': o_data['desc'],
                    'responsibilities': o_data['resp'],
                    'requirements': o_data['req'],
                    'required_skills': o_data['skills'],
                    'location': o_data['loc'],
                    'work_mode': o_data['mode'],
                    'stipend': o_data['stipend'],
                    'salary': o_data['salary'],
                    'duration': o_data['dur'],
                    'min_cgpa': o_data['min_cgpa'],
                    'eligible_degree': o_data['deg'],
                    'eligible_department': o_data['dept'],
                    'graduation_year': o_data['grad'],
                    'openings_count': o_data['openings'],
                    'application_deadline': o_data['deadline'],
                    'status': Opportunity.Status.APPROVED,
                }
            )
            created_opportunities.append(opp)

        self.stdout.write(self.style.SUCCESS(f'Created {len(created_opportunities)} Opportunities.'))

        # 5. Create Sample Applications across various stages
        demo_student = student_users[0] # Aarav Sharma (student@example.com)
        
        # Application 1: Shortlisted for Full Stack Intern at Google
        app1, _ = Application.objects.get_or_create(
            student=demo_student,
            opportunity=created_opportunities[0],
            defaults={
                'status': Application.Status.SHORTLISTED,
                'resume': demo_student.student_profile.resume,
                'cover_letter': 'I have built multiple production-grade Django web apps and would love to contribute to Google Cloud tools.',
                'recruiter_notes': 'Strong GitHub portfolio and excellent Django fundamentals. High match score.',
            }
        )

        # Application 2: Interview Scheduled for Full Stack Product Engineer at TechCorp AI
        app2, _ = Application.objects.get_or_create(
            student=demo_student,
            opportunity=created_opportunities[17], # TechCorp Full Stack Product Engineer
            defaults={
                'status': Application.Status.INTERVIEW_SCHEDULED,
                'resume': demo_student.student_profile.resume,
                'cover_letter': 'Very excited about generative AI application development and distributed web frameworks.',
                'recruiter_notes': 'Impressive resume project on Campus Placement Automation. Proceeding to Technical Round.',
            }
        )

        # Application 3: Selected for Full Stack Intern at Infosys
        app3, _ = Application.objects.get_or_create(
            student=demo_student,
            opportunity=created_opportunities[13], # Infosys Full Stack Intern
            defaults={
                'status': Application.Status.SELECTED,
                'resume': demo_student.student_profile.resume,
                'cover_letter': 'Looking forward to learning enterprise application practices at Infosys.',
                'recruiter_notes': 'Selected after technical and HR evaluation rounds. Offer letter extended.',
            }
        )

        # Application 4: Under Review at AWS
        app4, _ = Application.objects.get_or_create(
            student=demo_student,
            opportunity=created_opportunities[8], # AWS Backend Intern
            defaults={
                'status': Application.Status.UNDER_REVIEW,
                'resume': demo_student.student_profile.resume,
                'cover_letter': 'Passionate about distributed microservices and database query optimization.',
                'recruiter_notes': 'Resume passed initial screening.',
            }
        )

        # Additional applications from other students
        app5, _ = Application.objects.get_or_create(
            student=student_users[1], # Riya Patel (AI/ML)
            opportunity=created_opportunities[2], # Google AI Intern
            defaults={
                'status': Application.Status.SHORTLISTED,
                'resume': student_users[1].student_profile.resume,
                'cover_letter': 'Dedicated to research in multimodal embeddings and neural network architectures.',
                'recruiter_notes': 'Outstanding CGPA (9.15) and hands-on PyTorch project experience.',
            }
        )

        app6, _ = Application.objects.get_or_create(
            student=student_users[2], # Karthik Iyer (Frontend)
            opportunity=created_opportunities[3], # Google UI Intern
            defaults={
                'status': Application.Status.INTERVIEW_SCHEDULED,
                'resume': student_users[2].student_profile.resume,
                'cover_letter': 'Specialized in modern responsive UI, TailwindCSS, and accessible components.',
                'recruiter_notes': 'Clean portfolio and strong component architecture mastery.',
            }
        )

        app7, _ = Application.objects.get_or_create(
            student=student_users[3], # Sneha Reddy (DevOps)
            opportunity=created_opportunities[1], # Google Cloud DevOps Placement
            defaults={
                'status': Application.Status.UNDER_REVIEW,
                'resume': student_users[3].student_profile.resume,
                'cover_letter': 'Certified in cloud containerization with Terraform experience.',
            }
        )

        app8, _ = Application.objects.get_or_create(
            student=student_users[5], # Meera Joshi (SDE)
            opportunity=created_opportunities[4], # Microsoft SDE-1 Placement
            defaults={
                'status': Application.Status.SELECTED,
                'resume': student_users[5].student_profile.resume,
                'cover_letter': 'Academic topper and competitive coder ready to build high-scale cloud platforms.',
                'recruiter_notes': 'Exceptional problem-solving abilities and algorithmic fluency. Top candidate of the batch.',
            }
        )

        self.stdout.write(self.style.SUCCESS('Created Sample Applications across different statuses.'))

        # 6. Create Sample Interviews
        Interview.objects.get_or_create(
            application=app2,
            recruiter=recruiter_users[4],
            student=demo_student,
            defaults={
                'interview_date': timezone.now().date() + timedelta(days=3),
                'interview_time': time(14, 30),
                'interview_type': Interview.InterviewType.ONLINE,
                'meeting_link': 'https://meet.google.com/abc-internworld-demo',
                'instructions': 'Technical Deep-Dive Round: Please be prepared to discuss your Django architecture, PostgreSQL indexing, and walk through your resume projects.',
                'status': Interview.Status.SCHEDULED,
            }
        )

        Interview.objects.get_or_create(
            application=app6,
            recruiter=recruiter_users[0],
            student=student_users[2],
            defaults={
                'interview_date': timezone.now().date() + timedelta(days=5),
                'interview_time': time(11, 00),
                'interview_type': Interview.InterviewType.ONLINE,
                'meeting_link': 'https://meet.google.com/xyz-google-demo',
                'instructions': 'Frontend UI Design & Coding: Live coding in React / JavaScript and discussion on Web Vitals.',
                'status': Interview.Status.SCHEDULED,
            }
        )

        self.stdout.write(self.style.SUCCESS('Created Sample Scheduled Interviews.'))

        # 7. Create Sample Saved Opportunities for demo student
        SavedOpportunity.objects.get_or_create(student=demo_student, opportunity=created_opportunities[1])
        SavedOpportunity.objects.get_or_create(student=demo_student, opportunity=created_opportunities[4])
        SavedOpportunity.objects.get_or_create(student=demo_student, opportunity=created_opportunities[11])

        # 8. Create Sample Notifications
        Notification.objects.get_or_create(
            user=demo_student,
            title="Interview Scheduled: Full Stack Product Engineer",
            defaults={
                'message': f"An online video interview has been scheduled by TechCorp AI Innovations for {timezone.now().date() + timedelta(days=3)} at 2:30 PM.",
                'notification_type': Notification.NotificationType.INTERVIEW,
                'link_url': '/interviews/',
                'is_read': False,
            }
        )
        Notification.objects.get_or_create(
            user=demo_student,
            title="Candidate Selected! 🎉",
            defaults={
                'message': "Congratulations! Infosys Technologies has marked your application as Selected for the Full Stack Web Development role.",
                'notification_type': Notification.NotificationType.APPLICATION,
                'link_url': '/applications/my-applications/',
                'is_read': False,
            }
        )
        Notification.objects.get_or_create(
            user=demo_student,
            title="Application Shortlisted: Google Cloud",
            defaults={
                'message': "Your application for Full Stack Python & Django Developer Intern has been shortlisted by Google Cloud India!",
                'notification_type': Notification.NotificationType.APPLICATION,
                'link_url': '/applications/my-applications/',
                'is_read': True,
            }
        )

        Notification.objects.get_or_create(
            user=recruiter_users[4],
            title="New Application Received",
            defaults={
                'message': f"Aarav Sharma has applied for 'Full Stack Product Engineer'.",
                'notification_type': Notification.NotificationType.APPLICATION,
                'link_url': '/recruiters/applicants/',
                'is_read': False,
            }
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded InternWorld with complete sample data!'))
        self.stdout.write(self.style.SUCCESS('--- DEMO ACCOUNTS ---'))
        self.stdout.write(self.style.SUCCESS('Admin:     admin@example.com     / Admin@12345'))
        self.stdout.write(self.style.SUCCESS('Student:   student@example.com   / Student@12345'))
        self.stdout.write(self.style.SUCCESS('Recruiter: recruiter@example.com / Recruiter@12345'))
