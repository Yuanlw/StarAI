from sqlalchemy import create_engine, event

# 创建数据库引擎和 ORM 操作类
engine = create_engine(
    # 'mysql+pymysql://root:Uej#8910@127.0.0.1:3306/starAI',
    'mysql+pymysql://root:root1234@127.0.0.1:3306/starAI',
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=1800,
    isolation_level='REPEATABLE READ',
    connect_args={
        'read_timeout': 30,
        'write_timeout': 30,
        'charset': 'utf8',
        'sql_mode': 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION'
    },
    echo=True
)

@event.listens_for(engine, 'checkout')
def ping_connection(dbapi_connection, connection_record,
                    connection_proxy):
    try:
        dbapi_connection.ping()
    except:
        dbapi_connection.close()
        dbapi_connection = engine.pool.connect()
