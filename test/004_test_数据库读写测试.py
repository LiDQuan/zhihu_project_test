import pymysql
import configg


def main():
    db = configg.conn

    cursor = db.cursor()

    items = {
        "id2" : 11100,
        "id3" : 445654,
        "id4" : 0000
    }

    sql = "select count(*) from test_table where id2 = '%d' " % (items["id2"])
    sql2 = "insert into test_table(id2, id3, id4) VALUE ('%d', '%d', '%d')" % (items["id2"], items["id3"], items["id4"])

    cursor.execute(sql)

    return_counts = cursor.fetchall()

    if return_counts[0][0] > 0:
        print("数据已存在，不插入数据库")
    elif return_counts[0][0] == 0:
        print("新数据，执行插入")
        cursor.execute(sql2)
        db.commit()

    cursor.close()
    db.close()




if __name__ == "__main__":
    main()