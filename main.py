from fastapi import Depends, HTTPException, Security, status, Request
import time
from fastapi import security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, SecurityScopes
# from jose import JWTError, jwt
from typing import Union
from fastapi import FastAPI
import os
import logging
import push2notion
from notion_client import Client

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# app_secret = os.environ['APP_SECRET']
mm_secret = os.environ['MM_CMD_TOKEN']
app = FastAPI()

# security = HTTPBearer()

# default_msg = "\n"


class HTTPToken:

  def __init__(self, auto_error: bool = True):
    self.auto_error = auto_error

  async def __call__(self, request: Request, security_scopes: SecurityScopes):
    authorization = request.headers.get("Authorization")
    if authorization is not None:
      scheme, _, param = authorization.partition(" ")
    else:
      return None
    if not authorization or scheme.lower() != "token":
      if self.auto_error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authenticated")
      else:
        return None
    return HTTPAuthorizationCredentials(scheme=scheme, credentials=param)


app_security = HTTPToken()

# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#   start_time = time.time()
#   # Log Basic Request Details (Method, URL)
#   print(f"Request: {request.method} {request.url}")
#   # Log Request Headers
#   print(f"Headers: {request.headers.items()}")
#   try:
#     # Log Request Body
#     # body = await request.body()
#     body = ""
#     # Note: body is bytes, so decode or use json.loads() as needed
#     # body_str = body.decode('utf-8')  # Example decoding to string
#     # print(f"Body: {body_str}")
#   except Exception as e:
#     print(f"Error reading body: {e}")
#   # Proceed with the request
#   response = await call_next(request)
#   # Calculate request processing time
#   process_time = time.time() - start_time
#   print(f"Request processed in {process_time} secs")
#   return response


@app.post("/items/{item_id}")
def read_item(
    item_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(app_security),
    q: Union[str, None] = None):
  if credentials.credentials != mm_secret:
    logging.info("info logged in read item")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail="Invalid token")
  return {"item_id": item_id, "q": q}


@app.get("/")
def hello_world():
  # print("test print log")
  return {"message": "Hello World"}


@app.post("/")
async def receive_task(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(app_security)):
  if credentials.credentials != mm_secret:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail="Invalid token")
  task_details = await request.form()
  parsed_details = {
      'channel_id': task_details.get('channel_id'),
      'channel_name': task_details.get('channel_name'),
      'command': task_details.get('command'),
      'response_url': task_details.get('response_url'),
      'team_domain': task_details.get('team_domain'),
      'team_id': task_details.get('team_id'),
      'text': task_details.get('text'),
      'token': task_details.get('token'),
      'trigger_id': task_details.get('trigger_id'),
      'user_id': task_details.get('user_id'),
      'user_name': task_details.get('user_name')
  }
  # the important content is in text
  task_content = parsed_details['text']
  print(task_content)
  print("Task Received ")
  notion_token = os.environ['NOTION_API']
  database_id = "a05b2e9a2a38458db15a682ce03e9a4c"
  client = Client(auth=notion_token, log_level=logging.DEBUG)
  page = push2notion.insert_page(client, database_id, str(task_content))
  # return page
  return {"message": "Task received", "parsed_details": parsed_details}
