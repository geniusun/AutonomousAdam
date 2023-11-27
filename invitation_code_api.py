from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pluginlab_admin import App
from typing import List
import uuid

app = FastAPI()

# 数据库模拟
users = {}  # 用户数据 {user_id: {"invitations": [invitation_code, ...]}}
invitations = set()  # 有效的邀请码

class Registration(BaseModel):
    invitation_code: str

class User(BaseModel):
    user_id: str
    invitations: List[str]

def generate_invitation_codes(n=3):
    """生成n个唯一的邀请码"""
    return [str(uuid.uuid4()) for _ in range(n)]

@app.post("/register")
def register_user(registration: Registration):
    if registration.invitation_code not in invitations:
        raise HTTPException(status_code=400, detail="Invalid invitation code")
    
    # 创建用户
    user_id = str(uuid.uuid4())
    new_invitations = generate_invitation_codes()
    users[user_id] = {"invitations": new_invitations}
    
    # 更新邀请码数据库
    invitations.remove(registration.invitation_code)
    invitations.update(new_invitations)
    
    return {"user_id": user_id, "invitations": new_invitations}

@app.get("/invitations/{user_id}", response_model=User)
def get_user_invitations(user_id: str):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user_id, "invitations": users[user_id]["invitations"]}

# 初始化一些邀请码
invitations.update(generate_invitation_codes(5))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
