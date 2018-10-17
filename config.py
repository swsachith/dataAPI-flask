class Config(object):
    MYSQL_DB = "flask_test"
    MYSQL_USER = "root"
    MYSQL_PWD = "root"
    MYSQL_HOST = "localhost"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://" + MYSQL_USER + ":" + MYSQL_PWD + "@" + MYSQL_HOST + "/" + MYSQL_DB
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "IMLSDEMO"