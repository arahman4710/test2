import re
import time

def recmp(x) :
    return re.compile(x,  re.IGNORECASE | re.MULTILINE)

rem_pats = map(recmp,      ["^SET.*$",
                            "^CREATE SCHEMA.*$", 
                            "^USE.*$",
                            "NOT NULL",
                            "^\s+INDEX.*$",
                            "ON DELETE NO ACTION",
                            "ON UPDATE NO ACTION",
                            "ENGINE = Innodb",
                            "--.*$",
                            "`acuity`.", 
                            "`",]) 

tablename = re.compile("CREATE\s+TABLE IF NOT EXISTS (?P<tname>[a-zA-Z0-9_]+)") 
fieldname = re.compile("^\s+(?P<fn>[a-zA-Z0-9_]+)\s+(?P<type>[A-Z]+)\s*(?P<len>\([0-9]+\))?.*(?P<seq>AUTO_INCREMENT)?") 
pkey = re.compile("^\s+PRIMARY KEY\s+\((?P<pkey>[a-zA-Z0-9_]+)\)" )
fkey = re.compile("^\s+FOREIGN KEY\s+\((?P<fkey>[a-zA-Z0-9_]+)\s*\)" )
ref  = re.compile("^\s+REFERENCES\s+(?P<tab>[a-zA-Z0-9_]+)\s+\((?P<field>[a-zA-Z0-9_]+)\s*\)")


def to_underscores(name) :
    ln = list(name)
    outl = [] 
    for (i,c) in enumerate(ln) :
        if i > 0 and c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" : 
            outl.append("_")
        outl.append(c.lower())
    return "".join(outl)

class Field(object) :
    def __init__(self, name, tipe, len=None, auto_inc=None) :
        self.name = name
        self.is_primary = False
        self.len = len 
        self.is_foreign = False 
        self.reference_table = None 
        self.reference_field = None 
        self.tipe = tipe 
        self.needs_sequence = auto_inc

    def set_foreign(self, tab_ref, field_ref) :
        self.reference_table = tab_ref
        self.reference_field = field_ref 

    def to_string(self) :
        seqstr = "" 
        if self.needs_sequence :
            seqstr = ",Sequence(%s_sequence" % name  
        pstr = "" 
        if self.is_primary :
            pstr = ",primary_key=True" 
        fref = "" 
        if self.reference_table :
            fref = ",ForeignKey('%s.%s')" % (to_underscores(self.reference_table),
                                             to_underscores(self.reference_field)) 
        return "    %s = Column(%s()%s%s%s) " % (self.name , self.tipe, seqstr, pstr, fref) 

class Table(object) :
    def __init__(self, n) :
        self.name = to_underscores(n)  
        self.fields = {}  

    def add_field(self, name, tipe, len=None, auto_inc=None) : 
        name = to_underscores(name) 
        print "add_field ", name 
        if tipe == "INT" : 
            tipe = "Integer" 
        elif tipe == "VARCHAR" :
            tipe = "String" 
        elif tipe == "DOUBLE":
            tipe = "Float" 
        elif tipe == "DATETIME":
            tipe = "DateTime" 
        elif tipe == "CHAR" :
            tipe = "Char" 
        self.fields[name] = Field(name, tipe, len, auto_inc) 

    def set_primary(self, name) : 
        name = to_underscores(name) 
        print self.fields 
        self.fields[name].is_primary = True 
        
    def add_foreign_key(self, field, tab_ref, field_ref) : 
        field = to_underscores(field)
        if field in self.fields : 
            tab_ref = to_underscores(tab_ref)
            field_ref = to_underscores(field_ref)
            self.fields[field].set_foreign(tab_ref, field_ref) 

    def to_string(self) : 
        outl = [] 
        outl.append("class %s (Base) :\n" % self.name )
        outl.append("    __tablename__ = '%s'\n" % self.name ) 
        
        for i in self.fields.values() :
            outl.append(i.to_string())
        
        outl.append("    def __init__(self) : ")
        outl.append("        pass") 
        return "\n".join(outl)

sql = open("a.sql").read().replace("\r", "") 
outf = open("a.sqlalchemy.py", "w") 

for i in rem_pats :   # eliminate cruft 
    sql = i.sub("", sql) 

lines =  sql.split("\n") 
tables = [] 
table = None 

for l in lines:
    mo = tablename.match(l)
    if mo: 
        table = Table(mo.group("tname"))
        tables.append(table)
    else: 
        mo = pkey.match(l) 
        if table and mo :
            table.set_primary(mo.group("pkey"))
        else:
            mo = fkey.match(l)
            if mo: 
                foreign_key = mo.group("fkey")
            else: 
                mo = ref.match(l)
                if mo and table: 
                    table.add_foreign_key(foreign_key, mo.group("tab"), mo.group("field"))
                else:
                    mo = fieldname.match(l)
                    if table and  mo: 
                        table.add_field(mo.group("fn"), mo.group("type"), len= mo.group("len"), auto_inc=mo.group("seq"))
                    elif ";" in l:    
                        table = None

for i in tables :
    print i.to_string()
    print "\n" 