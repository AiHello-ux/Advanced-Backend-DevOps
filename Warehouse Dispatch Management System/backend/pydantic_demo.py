from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey, create_engine
from sqlalchemy.orm import Session, declarative_base
from pydantic import BaseModel
engine = create_engine("sqlite:///warehouse.db")
Base = declarative_base()

class WithoutPydanticModel(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True)
    package_name = Column(String)
    destination = Column(String)
    weight = Column(Float)


Base.metadata.create_all(engine)


package = WithoutPydanticModel(
    package_name="Laptop",
    destination="Bangalore",
    weight="ten"
)

print(package.package_name)
print(package.destination)
print(package.weight)


class PydanticModel(BaseModel):
    package_name: str
    destination: str
    weight: float


package = PydanticModel(
    package_name="Laptop",
    destination="Bangalore",
    weight="ten"
)

print(package.package_name)
print(package.destination)
print(package.weight)