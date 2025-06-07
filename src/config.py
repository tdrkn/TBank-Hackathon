from pydantic_settings import BaseSettings
from pydantic import SecretStr


class Settings(BaseSettings):
    telegram_token: SecretStr
    openai_api_key: SecretStr
    gemini_api_key: SecretStr
    tinvest_token: SecretStr
    tinvest_env: str = "prod"
    postgres_user: str = "postgres"
    postgres_password: SecretStr = SecretStr("postgres")
    postgres_db: str = "newsbot"
    postgres_host: str = "db"
    postgres_port: int = 5432
    rss_feeds: str = (
        "rbc=https://static.feed.rbc.ru/rbc/internal/rss.rbc.ru/rbc.ru/mainnews.rss,"  # noqa: E501
        "kommersant=https://www.kommersant.ru/RSS/section-economics.xml,"
        "cbr=http://www.cbr.ru/rss/RssNews,"
        "bankiru=https://www.banki.ru/news/lenta/?r1=rss&r2=news,"
        "finam_companies=https://www.finam.ru/analysis/conews/rsspoint/,"
        "finam_bonds=https://bonds.finam.ru/news/today/rss.asp,"
        "tass=https://tass.com/rss/v2.xml,"
        "profinance_stock=https://www.profinance.ru/fond.xml,"
        "profinance_economy=https://www.profinance.ru/econom.xml"
    )

    @property
    def rss_feeds_map(self) -> dict[str, str]:
        feeds = {}
        for item in self.rss_feeds.split(","):
            if "=" in item:
                name, url = item.split("=", 1)
                feeds[name.strip()] = url.strip()
        return feeds

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password.get_secret_value()}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
