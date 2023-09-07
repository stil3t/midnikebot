from pydantic import BaseSettings


class Settings(BaseSettings):
    token: str
    account_id: str

    class Config:
        env_file = './robot/.env'


settings = Settings()
