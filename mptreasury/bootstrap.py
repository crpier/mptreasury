import warnings
from functools import partial
from sqlite3 import Connection

from mptreasury import config, db
from mptreasury.utils import injection


# TODO: set db in bootstrap
def bootstrap():
    conf = config.Config()

    def create_conn(conf: config.Config):
        conn = db.connect(conf.DB_FILE)
        db.create_tables(conn)
        return conn

    injection.add_lazy_injectable("sql_conn", partial(create_conn, conf))

    def create_discogs_client(conf: config.Config):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=SyntaxWarning)
            import discogs_client
        return discogs_client.Client("mptreasury/0.1", user_token=conf.DISCOGS_PAT)

    injection.add_lazy_injectable(
        "discogs_client", partial(create_discogs_client, conf)
    )

    def create_s3_client(conf: config.Config):
        import boto3

        if conf.AWS_ACCESS_KEY and conf.AWS_SECRET_KEY:
            s3 = boto3.resource(
                "s3",
                aws_access_key_id=conf.AWS_ACCESS_KEY,
                aws_secret_access_key=conf.AWS_SECRET_KEY,
            )
            if not s3.meta:
                raise ConnectionError("Cannot instantiate S3 client")
            return s3.meta.client

    injection.add_lazy_injectable("s3_client", partial(create_s3_client, conf))

    conf.CACHE_FOLDER.mkdir(parents=True, exist_ok=True)
    return conf
