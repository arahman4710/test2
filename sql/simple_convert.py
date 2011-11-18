import re
import sys 
# simple (and simple minded) python script to convert mysql tables
# to base classes for sqlalchemy
# this is NOT a real parser and does not fill in the objects generated in
# any way (the __init__ method is empty)
# logic to fill in details is missing
#
# it should be possible to generate objects based on mysql tables more or
# less directly by changing String() (etc) to being String(len)
# as the length is kept in the Field objects along with the type
# 
def recmp(x) :
    return re.compile(x,  re.IGNORECASE | re.MULTILINE)
rem_pats = map(recmp,      ["^SET.*$",
                            "^CREATE SCHEMA.*$", 
                            "^USE.*$",
                            "/\*.*\*/", 
                            "NOT NULL",
                            "USE.*$"
                            "^\s+INDEX.*$",
                            "DROP TABLE.*$", 
                            "ON DELETE NO ACTION",
                            "ON UPDATE NO ACTION",
                            "DEFAULT NULL", 
                            "ENGINE.*$", 
                            "ENGINE = Innodb",
                            "`acuity`.", 
                            "`", 
                            "--.*$"]) 

tablename = re.compile("CREATE\s+TABLE\s* (IF NOT EXISTS)?\s*(?P<tname>[a-zA-Z0-9_]+)") 
fieldname = re.compile("^\s+(?P<fn>[a-zA-Z0-9_]+)\s+(?P<type>[a-zA-Z]+)\s*(?P<len>\([0-9]+\))?.*(?P<seq>AUTO_INCREMENT)?") 
pkey = re.compile("^\s+PRIMARY KEY\s+\((?P<pkey>[a-zA-Z0-9_]+)\)" )
fkey = re.compile("^\s+FOREIGN KEY\s+\((?P<fkey>[a-zA-Z0-9_]+)\s*\)" )
ref  = re.compile("^\s+REFERENCES\s+(?P<tab>[a-zA-Z0-9_]+)\s+\((?P<field>[a-zA-Z0-9_]+)\s*\)")


def to_underscores(name) :
    """
    Convert name in "camelCase" to one using underscores "camel_case"
    This avoids having to quote all the field and table names. 
    """ 
    ln = list(name)
    outl = [] 
    for (i,c) in enumerate(ln) :
        if i > 0 and c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" : 
            outl.append("_")
        outl.append(c.lower())
    return "".join(outl)

class Field(object) :
    """
    Each field is initialized with name and type and if it has an auto-increment
    sequence when first encountered. 
    Then later on (as the constraints are not necessarily discovered with
    the field) they're modified to add primary key information as well as  
    foreign key information.
    """ 
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

    def to_string(self, use_lengths=False) :
        """
        Print the field as a column in sqlalchemy
        Strings are kept as String() with no length as postgresql support for
        unlength'ed strings is pretty good.  However, if use_lengths=True the
        length info is included. 
        """ 
        seqstr = "" 
        if self.needs_sequence :
            seqstr = ",Sequence(%s_sequence)" % name  
        pstr = "" 
        if self.is_primary :
            pstr = ",primary_key=True" 
        
        fref = "" 
        if self.reference_table :
            fref = ",ForeignKey('%s.%s')" % (to_underscores(self.reference_table),
                                             to_underscores(self.reference_field)) 
        length = "" 
        if use_lengths :
            length = "%s" % self.len 
        return "    %s = Column(%s(%s)%s%s%s) " % (self.name , self.tipe, length, seqstr, pstr, fref) 

class Table(object) :
    """
    A table has a name and dictionary of keys.   When a field is encountered in
    the sql definition it is added to the table and primary key, foreign key info
    added as it is found.
    """ 
    def __init__(self, n) :
        self.name =   n  
        self.fields = {}  

    def add_field(self, name, tipe, len=None, auto_inc=None) : 
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
        print self.fields 
        self.fields[name].is_primary = True 
        
    def add_foreign_key(self, field, tab_ref, field_ref) : 
        if field in self.fields : 
            self.fields[field].set_foreign(tab_ref, field_ref) 

    def to_string(self, use_lengths=False) :
        """ 
        generate a string that looks like an sqlalchemy object definition
        """ 
        outl = [] 
        name = to_underscores(self.name) 
        outl.append("class %s (Base) :\n" % name )
        outl.append("    __tablename__ = '%s'\n" % name ) 
        for i in self.fields.values() :
            outl.append(i.to_string(use_lengths=False))
        outl.append("") 
        outl.append("    def __init__(self) : ")
        outl.append("        pass")
        outl.append("") 
        return "\n".join(outl)

def main() : 
    fn = "a.sql"
    if len(sys.argv) > 1 : 
        fn = sys.argv[1] 

    outfn = "%s-alchemy.py"  % fn 
    sql = open(fn).read().replace("\r", "") 


    for i in rem_pats :   # eliminate cruft 
        sql = i.sub("", sql) 

    print sql 

    lines =  sql.split("\n") 
    tables = [] 
    table = None 
    # ugly matching for regexes we're looking for 
    for l in lines : 
        print l 
        mo = tablename.match(l)  
        if mo : 
            table = Table(mo.group("tname"))
            tables.append(table) 
        else : 
            mo = pkey.match(l) 
            if table and mo :
                table.set_primary(mo.group("pkey"))
            else :
                mo = fkey.match(l)
                if mo : 
                    foreign_key = mo.group("fkey") 
                else : 
                    mo = ref.match(l) 
                    if mo and table : 
                        table.add_foreign_key(foreign_key, mo.group("tab"), mo.group("field"))
                    else :
                        mo = fieldname.match(l) 
                        if table and  mo : 
                            table.add_field(mo.group("fn"), mo.group("type"), len= mo.group("len"), auto_inc=mo.group("seq"))
                        
                        elif ";" in l :    
                            table = None

        
# print tables 

    outf = open(outfn, "w") 
    for i in tables :
        outf.write(i.to_string(use_lengths=True)) 
        outf.write("\n") 
    
main() 
