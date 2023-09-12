import asyncio

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.models.database import Base, engine
from app.routers.user import router_user
from app import logger
from algorithm import deal_data
import json
from configs.setting import config
from app import crud
from utils import RedisServer

# 定义状态常量
WS_CONNECTED = 1
WS_DISCONNECTED = 2

HEARTBEAT_MESSAGE = "0"
MAX_RETRIES = 3

Base.metadata.create_all(bind=engine)

app = FastAPI(title="问境")

# CORS 跨源资源共享
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 设置允许的源，可以是具体的域名，也可以是通配符"*"表示允许所有来源
    allow_methods=["*"],  # 设置允许的HTTP方法
    allow_headers=["*"],  # 设置允许的HTTP头部
    allow_credentials=True,  # 允许发送凭据（例如：cookies）
)


@app.get("/", tags=["主页"])
def get_home():
    return "hello,welcome!"


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    logger.info("websocket建立连接...")
    await websocket.accept()
    retry = 0

    while True:
        try:
            recv = json.loads(await asyncio.wait_for(websocket.receive_text(), 60))

            if recv == HEARTBEAT_MESSAGE:
                await websocket.send_text(json.dumps("1"))
                retry = 0
            else:
                res = deal_data(recv)
                await websocket.send_text(json.dumps(res))

        except WebSocketDisconnect:
            logger.info("websocket连接断开，系统异常！请退出重新登陆！")
            break
        except asyncio.TimeoutError:
            logger.info("心跳停止...")
            handle_heartbeat_failure(websocket, retry)
            retry += 1
            if retry > MAX_RETRIES:
                break
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            break


def handle_heartbeat_failure(websocket: WebSocket, retry: int):
    logger.info("检查websocket连接状态")

    if websocket.application_state.value == WS_CONNECTED:
        logger.info("websocket处于连接中...")
        if retry == MAX_RETRIES:
            websocket.close()
            logger.error("心跳超时，服务异常，请退出重新登陆！")
        else:
            logger.info(f"心跳停止：准备第{retry}次监听...")
    elif websocket.application_state.value == WS_DISCONNECTED:
        logger.info("websocket连接断开，系统异常！请退出重新登陆！")
    else:
        logger.info("websocket正在连接...")


app.include_router(router_user)

# keyfile = "./certificate/key.pem"
# certfile = "./certificate/cert.pem"

if __name__ == '__main__':
    uvicorn.run("server:app", host="0.0.0.0", port=11800, reload=True)
