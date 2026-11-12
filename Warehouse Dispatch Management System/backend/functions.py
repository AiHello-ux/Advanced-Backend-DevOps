from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey, create_engine
from sqlalchemy.orm import Session, declarative_base

engine = create_engine("sqlite:///warehouse.db")
Base = declarative_base()


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


Base.metadata.create_all(engine)


def register_package(package_name, destination, weight, arrival_date, status):
    session = Session(engine)

    pkg = Package(
        package_name=package_name,
        destination=destination,
        weight=float(weight),
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
        "arrival_date": str(pkg.arrival_date),
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

    result = []

    for pkg in packages:
        result.append({
            "id": pkg.id,
            "package_name": pkg.package_name,
            "destination": pkg.destination,
            "weight": pkg.weight,
            "arrival_date": str(pkg.arrival_date),
            "status": pkg.status,
            "batch_id": pkg.batch_id
        })

    session.close()
    return result


def search_batches(destination=None, vehicle=None, dispatch_status=None):
    session = Session(engine)

    query = session.query(DispatchBatch)

    if destination is not None:
        query = query.filter(DispatchBatch.destination == destination)

    if vehicle is not None:
        query = query.filter(DispatchBatch.vehicle == vehicle)

    if dispatch_status is not None:
        query = query.filter(DispatchBatch.dispatch_status == dispatch_status)

    batches = query.all()

    result = []

    for batch in batches:
        packages = session.query(Package).filter(Package.batch_id == batch.id).all()

        package_ids = []
        for pkg in packages:
            package_ids.append(pkg.id)

        result.append({
            "id": batch.id,
            "destination": batch.destination,
            "vehicle": batch.vehicle,
            "dispatch_status": batch.dispatch_status,
            "package_ids": package_ids
        })

    session.close()
    return result


