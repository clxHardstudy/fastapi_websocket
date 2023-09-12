import copy
import json
import time
import asyncio
import anyio
import websockets.exceptions
from fastapi import Depends
from app import models, schemas, get_db
from sqlalchemy.orm import Session
from app.common.validation import get_password_hash, create_access_token, verify_password, TokenSchemas, \
    check_access_token, check_user
from configs.setting import config
from fastapi import WebSocket
from app import logger

ACCESS_TOKEN_EXPIRE_MINUTES = config.get('token', 'expire_minutes')
LOGIN_EXPIRED = int(config.get('token', 'login_expired'))
PING_INTERVAL = int(config.get('token', 'ping_interval'))
USER_MAX_COUNT = int(config.get('token', 'user_max_count'))
MAX_TIME_PING = int(config.get('token', 'max_time_ping'))


def create_user(db: Session, item: schemas.UserCreate):
    res: models.User = db.query(models.User).filter(models.User.username == item.username).first()
    if res:
        raise Exception(f"用户 {item.username} 已存在")
    password = item.password
    db_item = models.User(**{
        'username': item.username,
        'password_hash': get_password_hash(password),
        "create_time": int(time.time()),
        "update_time": int(time.time()),
        "last_login": int(time.time()),
    })
    db_item.auth_token = create_access_token(db_item.id, 'user')
    db.add(db_item)
    db.commit()
    db.flush()
    return db_item.to_dict()


def login_user_swagger(db: Session, item: schemas.UserSwaggerLogin):
    user: models.User = db.query(models.User).filter(models.User.username == item.username).first()
    # 用户不存在
    if not user:
        raise Exception(404, f"用户 {item.username} 不存在")
    # 密码错误
    if not verify_password(item.password, user.password_hash):
        raise Exception(401, "用户密码错误")
    auth_token = create_access_token(user.id, 'user')
    user.auth_token = auth_token
    # 如果该用户还未登陆过，表中字段不存在json字符串
    user.last_login = int(time.time())
    db.commit()
    db.flush()
    return {"access_token": user.auth_token, "token_type": "bearer", "user_id": user.id,
            "user_name": user.username}


def login_user(db: Session, item: schemas.UserLogin):
    user: models.User = db.query(models.User).filter(models.User.username == item.username).first()
    # 用户不存在
    if not user:
        raise Exception(404, f"用户 {item.username} 不存在")
    # 密码错误
    if not verify_password(item.password, user.password_hash):
        raise Exception(401, "用户密码错误")
    user.last_login = int(time.time())
    db.commit()
    db.flush()
    print({"access_token": user.auth_token, "user_id": user.id, "user_name": user.username})
    return {"access_token": user.auth_token, "user_id": user.id, "user_name": user.username}


def update_user(db: Session, item_id: int, update_item: schemas.UserUpdate):
    user: models.User = db.query(models.User).filter(models.User.id == item_id).first()
    if not user:
        raise Exception("用户不存在")
    now = int(time.time())
    user.update_time = now
    user.password_hash = get_password_hash(update_item.password)
    db.commit()
    db.flush()
    return user.to_dict()


def get_user_once(db: Session, item_id: int):
    res: models.User = db.query(models.User).filter(models.User.id == item_id).first()
    return res


def get_user_once_by_name(db: Session, name: str):
    res: models.User = db.query(models.User).filter(models.User.name == name).first()
    return res


def get_users(db: Session):
    query = db.query(models.User).all()
    return query


def delete_user(db: Session, item_id: int):
    item = get_user_once(item_id=item_id, db=db)
    if not item:
        raise Exception(404, f"删除失败, 用户 {item_id} 不存在")
    db.delete(item)
    db.commit()
    db.flush()
    return True





