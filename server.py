import asyncio

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.models.database import Base, engine
from app.routers.user import router_user
from app import crud
from app import logger
from configs.setting import config
import json

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


def deal_data(data):
    print("调用算法...")
    return "11111"


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
            await websocket.send_text("1")
            recv = json.loads(await asyncio.wait_for(websocket.receive_text(), 5))
            # print(recv,type(recv))
            if recv == "0":
                await websocket.send_text("1")
                retry = 0
            else:
                res = deal_data(recv)
                await websocket.send_text(res)
        except Exception as e:
            logger.info("心跳停止...")
            logger.info("检查websocket连接状态")
            if websocket.application_state.value == 1:
                logger.info("websocket处于连接中...")
                if retry == 3:
                    await websocket.close()
                    print("心跳超时，服务异常，请退出重新登陆！")
                    break
                retry += 1
                print("心跳停止：准备第{}次监听...".format(retry))
            elif websocket.application_state.value == 2:
                logger.info("websocket连接断开，系统异常！请退出重新登陆！")
                break
            else:
                logger.info("websocket正在连接...")
        finally:
            pass


app.include_router(router_user)

# keyfile = "./certificate/key.pem"
# certfile = "./certificate/cert.pem"

if __name__ == '__main__':
    uvicorn.run("server:app", host="0.0.0.0", port=11800, reload=True)
