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
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    user_type = Column(String, default="user")

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
 
def warehouse_statistics():
    session = Session(engine)
    packages = session.query(Package).all()

    total_packages = len(packages)
    pending_dispatch = 0
    dispatched = 0
    destination_summary = {}
    for package in packages:
        status = package.status
        if status == "pending":
            pending_dispatch += 1
        elif status == "dispatched":
            dispatched += 1

        dest = package.destination
        if dest in destination_summary:
            destination_summary[dest] += 1
        else:
            destination_summary[dest] = 1
    session.close()
    return {
        "total_packages_received": total_packages,
        "total_packages_pending": pending_dispatch,
        "total_packages_dispatched": dispatched,
        "destination_wise_count": destination_summary
    }

def create_dispatch_batch(destination, vehicle, dispatch_status="pending", package_ids=None):
    session = Session(engine)
    batch = DispatchBatch(
        destination=destination,
        vehicle=vehicle,
        dispatch_status=dispatch_status
    )
    session.add(batch)
    session.commit()
    assigned_packages = []
    if package_ids:
        if isinstance(package_ids, int):
            package_ids = [package_ids]
        for pkg_id in package_ids:
            pkg = session.query(Package).filter(Package.id == pkg_id).first()
            if pkg:
                pkg.batch_id = batch.id
                if dispatch_status == "dispatched":
                    pkg.status = "dispatched"
                assigned_packages.append(pkg.id)
        session.commit()
    result = {
        "id": batch.id,
        "destination": batch.destination,
        "vehicle": batch.vehicle,
        "dispatch_status": batch.dispatch_status,
        "assigned_package_ids": assigned_packages
    }
    session.close()
    return result


access_token_expire_minutes = 1
refresh_token_expire = 7 * 24 * 60
secret_key = "12345"
algorithm = "HS256"


def create_token(username, token_type, user_type="user"):
    payload = {
        "username": username,
        "token_type": token_type,
        "user_type": user_type,
        "exp": datetime.now(timezone.utc) + timedelta(
            minutes=access_token_expire_minutes if token_type == "access" else refresh_token_expire
        )
    }
    token = jwt.encode(payload=payload, key=secret_key, algorithm=algorithm)
    return token

def verify_login(username, password):
    session = Session(engine)
    user = session.query(User).filter_by(username=username).first()
    if user is None:
        session.close()
        return False
    try:
        ph.verify(user.password, password)
    except VerifyMismatchError:
        session.close()
        return False
    user_type = user.user_type
    session.close()
    access_token = create_token(username=username, token_type="access", user_type=user_type)
    refresh_token = create_token(username=username, token_type="refresh", user_type=user_type)
    return {"access_token": access_token, "refresh_token": refresh_token}
        
def verify_token(token, token_type):
    if not token:
        return False
    try:
        payload = jwt.decode(jwt=token, key=secret_key, algorithms=[algorithm])
    except jwt.InvalidTokenError:
        return False
    if payload.get("token_type") == token_type:
        return payload
    return False

def register_user(username: str, password: str):
    session = Session(engine)
    username_exist = session.query(User).filter_by(username=username).first()
    if username_exist is not None:
        session.close()
        return False
    session.add(User(
        username=username,
        password=ph.hash(password),
        user_type="user"
    ))
    session.commit()
    session.close()

    return True
