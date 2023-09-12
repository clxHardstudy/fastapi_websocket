from fastapi_pagination import paginate, Params
from sqlalchemy.orm import Session
from app import schemas, crud
from fastapi import APIRouter, WebSocket, Depends
from app.common.validation import TokenSchemas, OAuth2PasswordRequestForm, check_user, check_user_ws, \
    fromat_token_to_user
from app import get_db, models

from configs.setting import config

router_user = APIRouter(
    prefix="/user",
    tags=["user-管理员"],
)


# PING_INTERVAL = int(config.get('token', 'ping_interval'))
# LOGIN_EXPIRED = int(config.get('token', 'login_expired'))


@router_user.post("", summary="创建管理员")
def add_user(item: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, item=item)


@router_user.post("/swagger/login", response_model=TokenSchemas, summary="swagger登录")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    item = schemas.UserSwaggerLogin(**{'username': form_data.username, 'password': form_data.password})
    return crud.login_user_swagger(db=db, item=item)


@router_user.post("/login", summary="管理员登录")
def login_user(item: schemas.UserLogin, db: Session = Depends(get_db)):
    return crud.login_user(db=db, item=item)


@router_user.put("", summary="管理员更新")
def update_user(update_item: schemas.UserUpdate, db: Session = Depends(get_db),
                user: models.User = Depends(check_user)):
    return crud.update_user(db=db, item_id=user.id, update_item=update_item)


@router_user.get("", summary="获取管理员列表")
def get_users(params: Params = Depends(), db: Session = Depends(get_db)):
    print("1111")
    return paginate(crud.get_users(db), params)


@router_user.get("/{item_id}", summary="获取管理员信息")
def get_user_once(item_id: int, db: Session = Depends(get_db)):
    return crud.get_user_once(db=db, item_id=item_id)


@router_user.delete("/{item_id}", summary="删除管理员")
def get_user_once(item_id: int, db: Session = Depends(get_db)):
    return crud.delete_user(db, item_id)

