import pymysql
import pandas as pd
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

host = config.get('mysql', 'host')
user = config.get('mysql', 'user')
password = config.get('mysql', 'password')
database = config.get('mysql', 'database')
port = int(config.get('mysql', 'port')) # 确保端口是整数

cnx = pymysql.connect(host=host,
                      user=user,
                      password=password,
                      db=database,
                      port=port) # 添加端口参数
                      

cursor = cnx.cursor()

df = pd.read_excel('mapping.xls')
mapping = df.set_index('字段').T.to_dict('list')

query = """
    SELECT c.TABLE_NAME, c.COLUMN_NAME, c.COLUMN_TYPE, c.COLUMN_COMMENT 
    FROM information_schema.columns c
    JOIN information_schema.tables t 
    ON c.TABLE_NAME = t.TABLE_NAME AND c.TABLE_SCHEMA = t.TABLE_SCHEMA
    WHERE c.TABLE_SCHEMA = %s AND IFNULL(c.COLUMN_COMMENT,'')='' AND t.TABLE_TYPE = 'BASE TABLE'
    AND c.COLUMN_KEY<>'PRI'
"""
cursor.execute(query, (database,))
results = list(cursor.fetchall())

query2 = """
    SELECT c.TABLE_NAME, c.COLUMN_NAME, c.COLUMN_TYPE, c.COLUMN_COMMENT 
    FROM information_schema.columns c
    JOIN information_schema.tables t 
    ON c.TABLE_NAME = t.TABLE_NAME AND c.TABLE_SCHEMA = t.TABLE_SCHEMA
    WHERE c.TABLE_SCHEMA = %s AND IFNULL(c.COLUMN_COMMENT,'')<>'' AND t.TABLE_TYPE = 'BASE TABLE'
    AND c.COLUMN_KEY<>'PRI'
"""
cursor.execute(query2, (database,))
results2 = list(cursor.fetchall())

# 创建一个从列名到注释的映射
column_comment_mapping = {column_name: column_comment for table_name, column_name, column_type, column_comment in results2 if column_comment}

# 合并xls文件中的映射和数据库中的映射
mapping = {**column_comment_mapping,**mapping}

sql_file = open('log.sql', 'w',encoding='utf-8')

for (table_name, column_name,column_type, column_comment) in results:
  if column_name in mapping:
    update_query = ("ALTER TABLE `%s`.`%s` CHANGE COLUMN `%s` `%s` %s COMMENT '%s';" %
                    (database,table_name,column_name,column_name,column_type, mapping[column_name]))
    print(update_query)
    cursor.execute(update_query)
    cnx.commit()
    sql_file.write(update_query)

sql_file.close()

cursor.close()
cnx.close()

