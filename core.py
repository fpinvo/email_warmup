
from connection import Warmup_data
from datetime import datetime
import json

class Core:
    def __init__(self):
        self.data = Warmup_data()

    def __str__(self) -> str:
        pass
    
    # do validation and checks before insert
    def validate_string(self,val):
        if val != None:
                if type(val) is int:
                    #for x in val:
                    #   print(x)
                    return str(val).encode('utf-8')
                else:
                    return val
    def json_to_db(self,tb_name):
        json_data=open('data/'+tb_name+'.json')
        json_obj = json.load(json_data)
        # parse json data to SQL insert
        for i, item in enumerate(json_obj):
            type = self.validate_string(item.get("type", None))
            username = self.validate_string(item.get("username", None))
            password = self.validate_string(item.get("password", None))
            create_at = self.validate_string(item.get("create_at", None))
            try:
                if tb_name == 'source':
                    self.source_db_insert(tb_name,type,username,password,create_at)
                elif tb_name == 'target':
                    self.source_db_insert(tb_name,type,username,password,create_at)
            except Exception as e:
                print(e)
    def source_db_insert(self,tb_name,type,username,password,create_at):
        self.data.insert(tb_name,type,username,password,create_at,None)

    def target_db_insert(self,tb_name,type,username,password,create_at):
        self.data.insert(tb_name,type,username,password,create_at,None)


# if __name__ == '__main__':
#     run = Core()
#     run.json_to_db('source')