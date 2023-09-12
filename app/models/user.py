from sqlalchemy import Column, Integer, String, JSON

from app.models.database import BaseModel


class User(BaseModel):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True, comment='id')
    username = Column(String(255), comment='用户名', unique=True)
    password_hash = Column(String(255), comment='哈希密码')
    auth_token = Column(String(255), comment='登录token')
    create_time = Column(Integer, comment='创建时间')
    update_time = Column(Integer, comment='更新时间')
    last_login = Column(Integer, comment='最近时间')
