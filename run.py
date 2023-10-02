
import uvicorn
import sqlalchemy
from typing import List, Optional, Annotated, Union

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
import databases
import sqlalchemy
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

DATABASE_URL = "sqlite:///./database.db"

metadata = sqlalchemy.MetaData()
database = databases.Database(DATABASE_URL)


battery = sqlalchemy.Table(
    "battery",
    metadata,
    sqlalchemy.Column("id",
                      sqlalchemy.Integer,
                      primary_key=True),
    sqlalchemy.Column("name",
                      sqlalchemy.String(500)),
    sqlalchemy.Column("latitude",
                      sqlalchemy.Float),
    sqlalchemy.Column("longitude",
                      sqlalchemy.Float),
    sqlalchemy.Column("setup_date",
                      sqlalchemy.String(100)),
    sqlalchemy.Column("level",
                      sqlalchemy.Integer),
    sqlalchemy.Column("capacity",
                      sqlalchemy.Integer),
    sqlalchemy.Column("group_id",
                      sqlalchemy.Integer,
                      sqlalchemy.ForeignKey("group.id"),
                      nullable=True),

)


group = sqlalchemy.Table(
    "group",
    metadata,
    sqlalchemy.Column("id",
                      sqlalchemy.Integer,
                      primary_key=True),
    sqlalchemy.Column("name",
                      sqlalchemy.String(500)),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


metadata.create_all(engine)

app = FastAPI()


def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user_auth = get_user(fake_users_db, token)
    return user_auth


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="1 - Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="2 - Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


@app.on_event("startup")
async def connect():
    await database.connect()


@app.on_event("shutdown")
async def connect():
    await database.disconnect()


class Group(BaseModel):
    id: int
    name: str


class GroupIn(BaseModel):
    name: str


class Battery(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    setup_date: str
    level: int
    capacity: int
    group_id: int


class BatteryIn(BaseModel):
    name: str
    latitude: float
    longitude: float
    setup_date: str
    level: int
    capacity: int
    group_id: int


class SecondBatteryIn(BaseModel):
    setup_date: str
    level: int


# GROUP


@app.post("/group/", response_model=Group)
async def create_group(current_user: Annotated[User, Depends(get_current_active_user)],
                       r: GroupIn = Depends()):
    query = group.insert().values(
        name=r.name
    )
    record_id = await database.execute(query)
    query = group.select().where(group.c.id == record_id)
    row = await database.fetch_one(query)
    return {**row}


@app.get("/group/{id}", response_model=Group)
async def get_one_group(id: int,
                        current_user: Annotated[User, Depends(get_current_active_user)]):
    query = group.select().where(group.c.id == id)
    row = await database.fetch_one(query)
    return {**row}


@app.get("/group/", response_model=List[Group])
async def get_all_groups(current_user: Annotated[User, Depends(get_current_active_user)]):
    query = group.select()
    all_get = await database.fetch_all(query)
    return all_get


@app.put("/group/{id}", response_model=Group)
async def update_group(id: int, current_user: Annotated[User, Depends(get_current_active_user)],
                       r: GroupIn = Depends()):
    query = group.update().where(group.c.id == id).values(
        name=r.name,
    )
    record_id = await database.execute(query)
    query = group.select().where(group.c.id == record_id)
    row = await database.fetch_one(query)
    return {**row}


@app.delete("/group/{id}", response_model=Optional[Group])
async def delete(id: int,
                 current_user: Annotated[User, Depends(get_current_active_user)]):
    query = group.delete().where(group.c.id == id)
    await database.execute(query)


# BATTERY


@app.post("/battery/", response_model=Battery)
async def create_battery(current_user: Annotated[User, Depends(get_current_active_user)],
                         r: BatteryIn = Depends()):
    query = battery.insert().values(
        name=r.name,
        latitude=r.latitude,
        longitude=r.longitude,
        setup_date=r.setup_date,
        level=r.level,
        capacity=r.capacity,
        group_id=r.group_id
    )
    record_id = await database.execute(query)
    query = battery.select().where(battery.c.id == record_id)
    row = await database.fetch_one(query)
    return {**row}


@app.get("/battery/{id}", response_model=Battery)
async def get_one_battery(id: int,
                          current_user: Annotated[User, Depends(get_current_active_user)]):
    query = battery.select().where(battery.c.id == id)
    row = await database.fetch_one(query)
    return {**row}


@app.get("/battery/", response_model=List[Battery])
async def get_all_battery(current_user: Annotated[User, Depends(get_current_active_user)]):
    query = battery.select()
    all_get = await database.fetch_all(query)
    return all_get


@app.get("/battery/params/", response_model=List[Battery])
async def get_parameters_all_battery(current_user: Annotated[User, Depends(get_current_active_user)],
                                     r: SecondBatteryIn = Depends()):
    query = battery.select().where(battery.c.setup_date == r.setup_date)
    all_get = await database.fetch_all(query)
    return all_get


@app.put("/battery/{id}", response_model=Battery)
async def update_battery(id: int,
                         current_user: Annotated[User, Depends(get_current_active_user)],
                         r: BatteryIn = Depends()):
    query = battery.update().where(battery.c.id == id).values(
        name=r.name,
        latitude=r.latitude,
        longitude=r.longitude,
        setup_date=r.setup_date,
        level=r.level,
        capacity=r.capacity
    )
    record_id = await database.execute(query)
    query = battery.select().where(battery.c.id == record_id)
    row = await database.fetch_one(query)
    return {**row}


@app.delete("/battery/{id}", response_model=Optional[Battery])
async def delete_battery(id: int,
                         current_user: Annotated[User, Depends(get_current_active_user)]):
    query = battery.delete().where(battery.c.id == id)
    await database.execute(query)


@app.get("/group/extreme/")
async def extrem_group(current_user: Annotated[User, Depends(get_current_active_user)]):
    query = battery.select()
    row = await database.fetch_all(query)

    capacity_per_group = {}

    for battery_row in row:
        if battery_row["group_id"] not in capacity_per_group:
            capacity_per_group[battery_row["group_id"]] = battery_row["capacity"]
        else:
            capacity_per_group[battery_row["group_id"]] += battery_row["capacity"]

    return {"min": min(capacity_per_group, key=capacity_per_group.get),
            "max": max(capacity_per_group, key=capacity_per_group.get)}


# ENDPOINT FOR RETREIVE BATTERIES PER GROUP
@app.get("/group/list/batteries/{id}", response_model=List[Battery])
async def extrem_group(id: int,
                       current_user: Annotated[User, Depends(get_current_active_user)]):
    query = battery.select().where(battery.c.group_id == id)
    row = await database.fetch_all(query)
    return row


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)


