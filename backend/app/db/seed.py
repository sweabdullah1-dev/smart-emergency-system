"""
Database seed: demo users, Saudi hospitals, ambulances, traffic zones.
Runs automatically on first startup if tables are empty.
"""
from app.core.security import get_password_hash
from app.db.session import SessionLocal, engine, Base
from app.models.ambulance import Ambulance, AmbulanceStatus
from app.models.citizen import Citizen
from app.models.dispatcher import Dispatcher
from app.models.driver import Driver
from app.models.hospital import Hospital, HospitalType
from app.models.traffic import TrafficLevel, TrafficZone
from app.models.user import User, UserRole

# Major hospitals across Saudi Arabia
HOSPITALS_DATA = [
    ("King Fahad Medical City", "مدينة الملك فهد الطبية", "Riyadh", 24.6877, 46.7219, 500, HospitalType.TRAUMA),
    ("King Saud Medical City", "مدينة الملك سعود الطبية", "Riyadh", 24.6408, 46.7728, 400, HospitalType.GENERAL),
    ("King Faisal Specialist Hospital", "مستشفى الملك فيصل التخصصي", "Riyadh", 24.6692, 46.6760, 350, HospitalType.SPECIALTY),
    ("Dr. Sulaiman Al Habib Hospital", "مستشفى د. سليمان الحبيب", "Riyadh", 24.7136, 46.6753, 300, HospitalType.GENERAL),
    ("King Abdulaziz Medical City", "مدينة الملك عبدالعزيز الطبية", "Riyadh", 24.9583, 46.6989, 450, HospitalType.UNIVERSITY),
    ("King Fahad Hospital Jeddah", "مستشفى الملك فهد بجدة", "Jeddah", 21.5433, 39.1728, 400, HospitalType.GENERAL),
    ("King Abdulaziz Hospital Jeddah", "مستشفى الملك عبدالعزيز بجدة", "Jeddah", 21.5169, 39.2192, 350, HospitalType.TRAUMA),
    ("Dr. Erfan & Bagedo Hospital", "مستشفى الدكتور عرفان", "Jeddah", 21.4858, 39.1925, 250, HospitalType.GENERAL),
    ("King Fahad Specialist Hospital Dammam", "مستشفى الملك فهد التخصصي بالدمام", "Dammam", 26.3927, 50.1130, 400, HospitalType.TRAUMA),
    ("King Fahad Hospital Hofuf", "مستشفى الملك فهد بالهفوف", "Eastern Province", 25.3647, 49.5876, 300, HospitalType.GENERAL),
    ("Ohud Hospital", "مستشفى أحد", "Medina", 24.4709, 39.6122, 350, HospitalType.GENERAL),
    ("King Fahad Hospital Medina", "مستشفى الملك فهد بالمدينة", "Medina", 24.5247, 39.5692, 300, HospitalType.GENERAL),
    ("Al Noor Specialist Hospital Mecca", "مستشفى النور التخصصي بمكة", "Mecca", 21.4225, 39.8262, 500, HospitalType.TRAUMA),
    ("King Abdullah Medical City Mecca", "مدينة الملك عبدالله الطبية بمكة", "Mecca", 21.3891, 39.8579, 450, HospitalType.UNIVERSITY),
    ("King Khaled Hospital Hail", "مستشفى الملك خالد بحائل", "Hail", 27.5114, 41.6901, 200, HospitalType.GENERAL),
    ("Aseer Central Hospital", "مستشفى عسير المركزي", "Abha", 18.2164, 42.5053, 300, HospitalType.GENERAL),
    ("King Fahad Specialist Hospital Tabuk", "مستشفى الملك فهد التخصصي بتبوك", "Tabuk", 28.3998, 36.5715, 250, HospitalType.GENERAL),
    ("King Fahad Hospital Buraidah", "مستشفى الملك فهد ببريدة", "Qassim", 26.3260, 43.9750, 280, HospitalType.GENERAL),
    ("King Fahad Central Hospital Najran", "مستشفى الملك فهد المركزي بنجران", "Najran", 17.4924, 44.1277, 200, HospitalType.GENERAL),
    ("Prince Mohammed Bin Abdulaziz Hospital", "مستشفى الأمير محمد بن عبدالعزيز", "Riyadh", 24.7743, 46.7386, 320, HospitalType.GENERAL),
]

TRAFFIC_ZONES = [
    ("Riyadh Ring Road", "Riyadh", 24.7136, 46.6753, 3.0, TrafficLevel.RED, 0.4),
    ("Olaya District", "Riyadh", 24.6900, 46.6850, 2.0, TrafficLevel.YELLOW, 0.7),
    ("King Fahd Road", "Riyadh", 24.7200, 46.6400, 2.5, TrafficLevel.YELLOW, 0.7),
    ("Jeddah Corniche", "Jeddah", 21.5433, 39.1728, 2.0, TrafficLevel.RED, 0.4),
    ("Palestine Street Jeddah", "Jeddah", 21.5169, 39.2192, 1.5, TrafficLevel.YELLOW, 0.7),
    ("Dammam King Fahd Road", "Dammam", 26.4207, 50.0888, 2.0, TrafficLevel.GREEN, 1.0),
    ("Mecca Central", "Mecca", 21.4225, 39.8262, 3.0, TrafficLevel.RED, 0.4),
    ("Medina Quba Road", "Medina", 24.4709, 39.6122, 1.5, TrafficLevel.GREEN, 1.0),
]

AMBULANCE_POSITIONS = [
    ("RYD-001", "Riyadh", 24.7136, 46.6753),
    ("RYD-002", "Riyadh", 24.7580, 46.7020),
    ("RYD-003", "Riyadh", 24.6500, 46.7100),
    ("JED-001", "Jeddah", 21.5433, 39.1728),
    ("JED-002", "Jeddah", 21.4858, 39.1925),
    ("DMM-001", "Dammam", 26.3927, 50.1130),
    ("DMM-002", "Dammam", 26.4207, 50.0888),
    ("MKK-001", "Mecca", 21.3891, 39.8579),
    ("MED-001", "Medina", 24.5247, 39.5692),
    ("ABH-001", "Abha", 18.2164, 42.5053),
]


def init_db():
    Base.metadata.create_all(bind=engine)


def seed_if_empty():
    init_db()
    db = SessionLocal()
    try:
        if db.query(User).first():
            return

        demo_users = [
            ("admin@system.com", "admin123", "System Admin", UserRole.DISPATCHER),
            ("driver@system.com", "driver123", "Ahmed Al Driver", UserRole.DRIVER),
            ("citizen@system.com", "citizen123", "Sara Al Citizen", UserRole.CITIZEN),
            ("hospital@system.com", "hospital123", "Hospital Staff", UserRole.HOSPITAL),
        ]

        users = []
        for email, password, name, role in demo_users:
            u = User(
                email=email,
                hashed_password=get_password_hash(password),
                full_name=name,
                phone="+966500000000",
                role=role,
            )
            db.add(u)
            users.append((u, role))
        db.commit()

        for u, role in users:
            db.refresh(u)
            if role == UserRole.CITIZEN:
                db.add(Citizen(user_id=u.id, default_lat=24.7136, default_lng=46.6753))
            elif role == UserRole.DISPATCHER:
                db.add(Dispatcher(user_id=u.id))
            elif role == UserRole.DRIVER:
                db.add(Driver(user_id=u.id, license_number="SA-DEMO-DRIVER"))
        db.commit()

        driver_user = db.query(User).filter(User.email == "driver@system.com").first()
        driver = db.query(Driver).filter(Driver.user_id == driver_user.id).first()

        for plate, city, lat, lng in AMBULANCE_POSITIONS:
            amb = Ambulance(
                plate_number=plate,
                lat=lat,
                lng=lng,
                city=city,
                status=AmbulanceStatus.AVAILABLE,
            )
            db.add(amb)
        db.commit()

        first_amb = db.query(Ambulance).filter(Ambulance.plate_number == "RYD-001").first()
        if first_amb and driver:
            first_amb.driver_id = driver.id

        hospital_user = db.query(User).filter(User.email == "hospital@system.com").first()
        for i, (name, name_ar, city, lat, lng, cap, htype) in enumerate(HOSPITALS_DATA):
            h = Hospital(
                name=name,
                name_ar=name_ar,
                city=city,
                lat=lat,
                lng=lng,
                capacity=cap,
                current_load=int(cap * 0.3),
                emergency_available=True,
                hospital_type=htype,
                user_id=hospital_user.id if i == 0 and hospital_user else None,
            )
            db.add(h)

        for name, city, clat, clng, radius, level, factor in TRAFFIC_ZONES:
            db.add(
                TrafficZone(
                    name=name,
                    city=city,
                    center_lat=clat,
                    center_lng=clng,
                    radius_km=radius,
                    level=level,
                    speed_factor=factor,
                )
            )

        db.commit()
        print("Database seeded successfully with demo data.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_if_empty()
