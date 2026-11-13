from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey, create_engine
from sqlalchemy.orm import Session, declarative_base
from argon2 import PasswordHasher
import jwt
from datetime import datetime, timedelta, timezone
from argon2.exceptions import VerifyMismatchError


engine = create_engine("sqlite:///warehouse.db")
Base = declarative_base()
ph=PasswordHasher()

class DispatchBatch(Base):
    __tablename__ = "dispatch_batches"
    id = Column(Integer, primary_key=True)
    destination = Column(String)
    vehicle = Column(String)
    dispatch_status = Column(String)


class Package(Base):
    __tablename__ = "packages"
    id = Column(Integer, primary_key=True)
    package_name = Column(String)
    destination = Column(String)
    weight = Column(Float)
    arrival_date = Column(Date)
    status = Column(String)
    batch_id = Column(Integer, ForeignKey("dispatch_batches.id"), nullable=True)


class User(Base):
    __tablename__ ="users"
    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)

Base.metadata.create_all(engine)


def register_package(package_name, destination, weight, arrival_date, status):
    session = Session(engine)

    pkg = Package(
        package_name=package_name,
        destination=destination,
        weight=weight,
        arrival_date=arrival_date,
        status=status
    )
    session.add(pkg)
    session.commit()

    result = {
        "id": pkg.id,
        "package_name": pkg.package_name,
        "destination": pkg.destination,
        "weight": pkg.weight,
        "arrival_date": pkg.arrival_date,
        "status": pkg.status,
        "batch_id": pkg.batch_id
    }

    session.close()
    return result


def get_one_package(id):
    session = Session(engine)

    pkg = session.query(Package).filter(Package.id == id).first()

    if pkg is None:
        session.close()
        return None

    result = {
        "id": pkg.id,
        "package_name": pkg.package_name,
        "destination": pkg.destination,
        "weight": pkg.weight,
        "arrival_date": str(pkg.arrival_date),
        "status": pkg.status,
        "batch_id": pkg.batch_id
    }

    session.close()
    return result


def update_package(id, package_name=None, destination=None, weight=None, arrival_date=None, status=None):
    session = Session(engine)

    pkg = session.query(Package).filter(Package.id == id).first()

    if pkg is None:
        session.close()
        return None

    if package_name is not None:
        pkg.package_name = package_name

    if destination is not None:
        pkg.destination = destination

    if weight is not None:
        pkg.weight = float(weight)

    if arrival_date is not None:
        pkg.arrival_date = arrival_date

    if status is not None:
        pkg.status = status

    session.commit()

    result = {
        "id": pkg.id,
        "package_name": pkg.package_name,
        "destination": pkg.destination,
        "weight": pkg.weight,
        "arrival_date": str(pkg.arrival_date),
        "status": pkg.status,
        "batch_id": pkg.batch_id
    }

    session.close()
    return result


def delete_package(id):
    session = Session(engine)

    pkg = session.query(Package).filter(Package.id == id).first()

    if pkg is None:
        session.close()
        return None

    if pkg.status == "dispatched":
        session.close()
        return None

    session.delete(pkg)
    session.commit()

    session.close()
    return True

def search_packages(destination=None, status=None, arrival_date=None):
    session = Session(engine)

    query = session.query(Package)

    if destination is not None:
        query = query.filter(Package.destination == destination)

    if status is not None:
        query = query.filter(Package.status == status)

    if arrival_date is not None:
        query = query.filter(Package.arrival_date == arrival_date)

    packages = query.all()

    results = []
    for pkg in packages:
        results.append({
            "id": pkg.id,
            "package_name": pkg.package_name,
            "destination": pkg.destination,
            "weight": pkg.weight,
            "arrival_date": str(pkg.arrival_date),
            "status": pkg.status,
            "batch_id": pkg.batch_id
        })

    session.close()
    return results

def view_dispatch_batches(destination=None, vehicle=None, dispatch_status=None):
    session = Session(engine)

    query = session.query(DispatchBatch)

    if destination is not None:
        query = query.filter(DispatchBatch.destination == destination)

    if vehicle is not None:
        query = query.filter(DispatchBatch.vehicle == vehicle)

    if dispatch_status is not None:
        query = query.filter(DispatchBatch.dispatch_status == dispatch_status)

    batches = query.all()

    results = []
    for batch in batches:
        results.append({
            "id": batch.id,
            "destination": batch.destination,
            "vehicle": batch.vehicle,
            "dispatch_status": batch.dispatch_status
        })

    session.close()
    return results


# ----------------------------------------------------------------------------------------#
USERNAME = "admin"
PASSWORD = "admin123"
access_token_expire_minutes = 1
refresh_token_expire = 7 * 24 * 60
secret_key = "12345"
algorithm = "HS256"


def login(username,password):
    if username == USERNAME and password == PASSWORD:
        access_token = create_token(username=username,token_type="access")
        refresh_token = create_token(username=username,token_type="refresh")
        return {"access_token":access_token,"refresh_token":refresh_token}
    return None

# login and username
def verify_login(username, passward):
    session=Session(engine)
    user=Session.query(User).filter_by(username=username).first()
    if user is None:
        session.close()
        return False
    try:
        ph.verify(user.passward,passward)
    except VerifyMismatchError:
        return False
    session.close()
    access_token=create_token(username=username,token_type="access")
    refresh_token=create_token(username=username,token_type="refresh")
    return {"access_token":access_token,"refresh_token":refresh_token}
        
        
        
#jwt has 3 parts one is header and then payload and then signature
#exp is the expiry o the token 
def create_token(username, token_type):
    payload = {
        "username": username,
        'token_type': token_type,
        "exp": datetime.now(timezone.utc) + timedelta(
            minutes=refresh_token_expire if token_type == "access" else refresh_token_expire)  
    }
    token = jwt.encode(payload=payload, key=secret_key, algorithm=algorithm)
    return token

#------------------------------------------#

def register_user(username:str,passward:str):
    session=Session(engine)
    username_exist=session.query(User).filter_by(username=username).first()
    if username_exist is not None:

        session.close()
        return False
    session.add(User(username=username, password=ph.hash(passward)))
    session.commit()
    session.close()
    return  True


