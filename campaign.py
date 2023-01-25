
import asyncio

from connection import Warmup_data
from core import Core
import sendEmail

class Campaign:
    source_email = None
    target_email = None
    subject = None
    Body = None
    
    def __init__(self):
        self.data = Warmup_data()
    
    def get_target_db(self,email):
        result = self.data.select_all(
            """SELECT * FROM target
           where email = '""" + str(email) + """' """)
        return result
    
    def get_source_db(self):
        result = self.data.select_all(
            """SELECT * FROM source
            ORDER BY RAND()
            LIMIT 1 """)
        return result
    
    def check_source_campaign(self):
        target_email_ = self.get_target_db(self.target_email)
        target_email_id = target_email_[0][0]
        self.source_email = self.get_source_db()
        source_id = self.source_email[0][0]
        result = self.data.select_all(
            """ SELECT * FROM campaign where source_email_id = """ + str(source_id) + """ and target_email_id = """+str(target_email_id))
        return result

    def sendEmail(self):
        sendEmail.our_email = self.target_email
        # sendEmail.main("source",self.source_email[0][2])
        return sendEmail.get_user_service(self.source_email[0][2]) 
        
    
    def func1(self):
        source_camp = self.check_source_campaign()
        service = self.sendEmail()
        if source_camp:
            result = self.data.select_all("Select * from gmailThreadId where id ="+str(source_camp[0][5]))
            message = sendEmail.get_msg_id_header(service,str(result[0][1]))
            print("message",str(result[0][1]))
            print(message)
            print(self.source_email[0][2], self.subject,self.Body, str(result[0][2]), str(message['Message-Id']))
            sendEmail.send_message_thread(service, self.source_email[0][2], self.subject,self.Body, str(result[0][2]), str(message['Message-Id']))
        else:
            sendEmail.send_message(service, 'farhan.pirzada@invozone.com',self.subject,self.Body)
            print("Message sent")
            
            

    def func2(self,task_no):
        print(f'{task_no}... Blog!')

    async def async_func(self,task_no):
        self.func1()
        await asyncio.sleep(1)
        self.func2(task_no)

    async def main(self):
        taskA = loop.create_task (self.async_func('taskA'))
        await asyncio.wait([taskA])

if __name__ == "__main__":
    camp = Campaign()
    camp.target_email = "farhan.pirzada@invozone.com"
    camp.subject = "Campaign"
    camp.Body = "Campaign Body"
    ##  update the source in database
    # run = Core()
    # run.json_to_db('target')
    ##  target email address
    try:
        # camp.check_source_campaign()
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(camp.main())
        # import pdb; pdb.set_trace()
        camp.func1()
    except Exception as e:
        print(e)
    
