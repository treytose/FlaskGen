#!/usr/local/bin/python3.9
'''
Allows high level access to a MySQL database using mysqlclient
'''

import MySQLdb, traceback

def check_connection(func):
    def inner(self, *args, **kwargs):        
        try:            
            return func(self, *args, **kwargs)        
        except Exception as e:
            self.connect()
            print(traceback.format_exc())
            self.log(traceback.format_exc())
            return func(self, *args, **kwargs)
    return inner

class P3DB:
    def __init__(self, hostname, username, password, database):        
        self.hostname = hostname
        self.username = username
        self.password = password
        self.database = database
        self.connection = None
        self.connect()
        self.lastInsId = -1

    def __del__(self):
        if self.connection:
            self.connection.close()

    def log(self, *args):        
        print(*args)

    def connect(self):
        self.connection = MySQLdb.connect(self.hostname, self.username, self.password, self.database)     
        self.connection.autocommit = True   
        self.connection.cursor().execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

    @check_connection
    def fetchone(self, sql, *args):        
        with self.connection.cursor() as cursor:
            cursor.execute(sql, args) if args else cursor.execute(sql)
            row = cursor.fetchone()  
            if not row:
                return {}
            column_names = [d[0] for d in cursor.description]
            return dict(zip(column_names, row))
        
    @check_connection
    def fetchall(self, sql, *args):     
        with self.connection.cursor() as cursor:     
            cursor.execute(sql, args) if args else cursor.execute(sql)
            rows = cursor.fetchall()        
            column_names = [d[0] for d in cursor.description]
            return [dict(zip(column_names, r)) for r in rows]

    @check_connection
    def fetchlistvals(self, sql, *args):
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(sql, args) if args else cursor.execute(sql)
                rows = cursor.fetchall()        
                return [r[0] for r in rows]
            except Exception as e:
                return []

    @check_connection
    def fetchval(self, sql, *args):        
        with self.connection.cursor() as cursor:
            cursor.execute(sql, args) if args else cursor.execute(sql)
            row = cursor.fetchone()
            return row[0] if len(row) > 0 else None

    def update(self, *args, **kwargs):
        return self.updatedict(*args, **kwargs)

    @check_connection
    def updatedict(self, table, key_column, key_value, obj):
        sql = f'UPDATE {table} SET {",".join([ a+"=%s" for a in obj.keys() ])} WHERE {key_column} = {key_value}'
        print(sql, obj.values())
        with self.connection.cursor() as cursor:
            cursor.execute(sql, tuple(obj.values()))
            self.connection.commit()
            return self.connection.errno()

    @check_connection
    def insert(self, table, obj, update_on_duplicate=False):
        sql = f'INSERT INTO {table} ({",".join(obj.keys())}) VALUES ({",".join(["%s" for v in range(len(obj))])})'
        arguments = tuple(obj.values())

        if update_on_duplicate:
            setstr = ",".join([ "{k}=%s".format(k=k) for k in obj.keys()])						
            sql += "ON DUPLICATE KEY UPDATE {setstr}".format(setstr=setstr)
            arguments += tuple(obj.values())

        with self.connection.cursor() as cursor:
            cursor.execute(sql, arguments)
            self.connection.commit()
            self.lastInsId = cursor.lastrowid
            return self.connection.errno()

    ''' Efficiently inserts a list of records
        @arg table - The table to insert into
        @arg records - A list of dictionaries, containing the keys as the columns and the values as the values to insert
    '''
    @check_connection
    def insert_many(self, table, records):
        sql = f'INSERT INTO {table} ({",".join(records[0].keys())}) VALUES ({",".join(["%s" for v in range(len(records[0]))])})'
        values = [tuple(obj.values()) for obj in records]
        with self.connection.cursor() as cursor:
            cursor.executemany(sql, values)
            self.connection.commit()
            return self.connection.errno()
            

    @check_connection
    def execute(self, sql, *args):
        with self.connection.cursor() as cursor:
            cursor.execute(sql, args)
            self.connection.commit()
            self.lastInsId = cursor.lastrowid
            return self.connection.errno()

if __name__ == '__main__':    
    pass
