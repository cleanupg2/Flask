import sqlite3

conn = sqlite3.connect("items.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS linen
(tag_id,aquisition_date, category, sub_category, supplier, clean, damage, status, staff_name)''')
c.execute('''CREATE TABLE IF NOT EXISTS log
(tag_id,event_type,date,staff_name)''')
conn.commit()
conn.close()

#Classe nao utilizada, estava tentando fazer algo parecido que fiz com usuarios mas acabou nao sendo necessario
#Nao apaguei para deixar registrado.

class Tag():
    def __init__(self,tag_id,aquisition_date, type, supplier, clean, status,staff_name):
        self.tag_id = tag_id
        self.aquisition_date = aquisition_date
        self.type = type
        self.supplier= supplier
        self.clean = clean
        self.status = status
        self.staff_name = staff_name

    def get_tag(self):
        return self.tag_id
    
    def to_dict(self):
        return {
            'tag_id': self.tag_id,
            'aquisition_date': self.aquisition_date,
            'type': self.type,
            'supplier': self.supplier,
            'clean': self.clean,
            'status': self.status,
            'staff_name': self.staff_name
        }
