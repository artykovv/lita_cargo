from sqlalchemy import Column, Integer, Float, ForeignKey, String, Date, Enum, JSON, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
from datetime import datetime


Base = declarative_base()

class ProductStatus(enum.Enum):
    IN_TRANSIT = 'В пути'
    IN_WAREHOUSE = 'Можно забирать'
    PICKED_UP = 'Забрали'

class Role (Base):
   __tablename__ = "role"
   id = Column(Integer, primary_key=True, index=True, autoincrement=True)
   name = Column(String)
   permissions = Column(JSON)

class User(Base):
   __tablename__ = "user"
   id = Column(Integer, primary_key=True, index=True, autoincrement=True)
   username = Column(String, unique=True, nullable=False)
   email = Column(String, nullable=True)
   password = Column(String, nullable=False)
   is_active = Column(Boolean, default=True)
   registered_at = Column(Date, default=datetime.utcnow)
   role_id = Column(Integer, ForeignKey('role.id'), default=1)
   role = relationship("Role", backref="users", primaryjoin="User.role_id == Role.id")

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    number = Column(String, nullable=True)
    city = Column(String, nullable=True)
    products = relationship("Product", order_by="Product.id", back_populates="client")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_code = Column(String, nullable=False)
    weight = Column(Integer)
    amount = Column(Integer)
    date = Column(Date)
    status = Column(Enum(ProductStatus), nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=True)
    client = relationship("Client", back_populates="products")
