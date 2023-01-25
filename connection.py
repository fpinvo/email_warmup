import mysql.connector as mdb
import os
import dotenv
from itertools import chain

class SQL_Base(object):
    cursor_ = None
    def __init__(self, host, user, password, database):
        try:
            self.connection = mdb.connect(host=host, user=user, password=password, database=database)
            db_Info = self.connection.get_server_info()
            print("Connected to MySQL database... MySQL Server version on ", db_Info)
            
            self.cursor_ = self.connection.cursor()
            # global connection timeout arguments
            global_connect_timeout = 'SET GLOBAL connect_timeout=180'
            global_wait_timeout = 'SET GLOBAL connect_timeout=180'
            global_interactive_timeout = 'SET GLOBAL connect_timeout=180'

            self.cursor_.execute(global_connect_timeout)
            self.cursor_.execute(global_wait_timeout)
            self.cursor_.execute(global_interactive_timeout)
            self.cursor_.execute("USE %s;" %  os.getenv("DATABASE_NAME"))
        except mdb.Error as e:
            print("Init error %d: %s" % (e.args[0], e.args[1]))
    
    def __execute(self, query, parameters=[]):
        try:
            if self.connection.is_connected():
                self.cursor_.execute(query, parameters)
                return self.cursor_
        except mdb.Error as e:
            print("Execute error %d: %s" % (e.args[0], e.args[1]))
            
    def __select(self, query, parameters):
        return self.__execute(query, parameters)
    
    def commit(self, query, parameters=[]):
        self.__execute(query, parameters)
        return self.connection.commit()
    
    def execute(self, query, parameters=[]):
        return self.__execute(query, parameters)
 
    def select_all(self, query, parameters=[]):
        cursor = self.__select(query, parameters)
        return cursor.fetchall()
   
    def select_one(self, query, parameters=[]):
        cursor = self.__select(query, parameters)
        return cursor.fetchone()
   
    def dispose(self):
        if self.connection:
            self.connection.close()
            
            
class Warmup_data(SQL_Base):
    def __init__(self):
        dotenv_file = os.path.join(".env")
        if os.path.isfile(dotenv_file):
            dotenv.load_dotenv(dotenv_file)
        SQL_Base.__init__(self, os.getenv("DATABASE_HOST"), os.getenv("DATABASE_USER"), os.getenv("DATABASE_PASSWORD"), os.getenv("DATABASE_NAME"))
    
    def insert(self,tb_name,*args):
        list_cName= self.get_table_names(tb_name)
        column_names = tuple(chain(*list_cName))
        query = "INSERT INTO "+tb_name+" "+str(column_names[1:]).replace("'", "")+" VALUES (%s,%s,%s,%s,%s)"
        return self.commit(query,[*args])
          
    def get_table_names(self,tb_name):
        query = """
         SELECT `COLUMN_NAME` 
        FROM `INFORMATION_SCHEMA`.`COLUMNS` 
        WHERE `TABLE_SCHEMA`='emailwarmup' 
            AND `TABLE_NAME`='"""+tb_name+"""';"""
        return self.select_all(query)
       
    def get(self, db_name,condition,email):
        query = "SELECT * FROM "+db_name+" WHERE "+condition+"=%s"
        result = self.select_one(query, [email])
        return result
      
    def get_all(self,tb_name):
        query = "SELECT * FROM "+tb_name
        result = self.select_all(query)
        users = []
        for row in result:
            users.append(row)
        return users
 
    def update(self, username, email):
        query = "UPDATE users SET email=%s WHERE username=%s"
        return self.execute(query, [email, username])
          
    def delete(self, username):
        query = "DELETE FROM users WHERE username=%s"
        return self.execute(query, [username])