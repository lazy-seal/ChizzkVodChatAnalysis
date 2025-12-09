import psycopg2
import json


class dbObject:
    def __init__(self):
        with open("private.json", "r", encoding="utf-8") as f: #@TODO make resource.json or other file to store private data
            f_json = json.load(f)
            dbpassword = f_json['dbpassword']
        self.conn = psycopg2.connect(host="localhost", dbname="ChzzkChats", user="postgres", password=dbpassword, port=5432)
        self.cur = self.conn.cursor()

    # def connectToChzzkChats(self):
    #     self.conn = psycopg2.connect(host="localhost", dbname="ChzzkChats", user="postgres",
    #                         password="6801", port=5432)
    #     self.cur = self.conn.cursor()
    #     # @TODO implement code when db wasn't connected

    def getCursor(self):
        return self.cur
    
    def endSession(self):
        if self.cur:
            self.cur.close()
        self.conn.close()
    
    def executeSQLScript(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            script = f.read()
            self.cur.execute(script)

if __name__ == "__main__":
    chatdb = dbObject()
    # chatdb.connectToChzzkChats()
    chatdb.getCursor()
    
    # code here to implement
    """
    First, check if the streamer already exists on the users
    if not, put in the user.
    
    Use the streamer's id to create video_streamer_id
    """
    
    chatdb.endSession()
    
    # @TODO Database Related
        # @TODO write a pipeline code from api fetch -> database:
            # @TODO read that csv file and put them into the db (look at csv lib doc)
    
