import json
from fastapi import FastAPI
from fastapi import WebSocket
import uvicorn
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 设置允许的源，可以是具体的域名，也可以是通配符"*"表示允许所有来源
    allow_methods=["*"],  # 设置允许的HTTP方法
    allow_headers=["*"],  # 设置允许的HTTP头部
    allow_credentials=True,  # 允许发送凭据（例如：cookies）
)


def deal_data(data):
    print("调用算法...")
    return {"hello":"world"}

@app.get("/")
async def printHello():
    return "hello"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=11800, ssl_keyfile="./certificate/key.pem", ssl_certfile="./certificate/cert.pem")
