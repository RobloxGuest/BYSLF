# Credit: Pidge and Griff 
# You've gotta put your database credentials in.
# Place it in your DarkflameServer directory.
# Run it with sudo python3 unstuck.py [ACCOUNT-NAME] [CHARACTER-NAME]
# You might have to install the mysql-connector first, which you can do with sudo pip install mysql-connector
# !/usr/bin/python

import mysql.connector
import sys
import xml.dom.minidom as md

MAP_ID = "1200" #World to put player in to get them un-stuck
LZX = "-14"  #X-Value
LZY = "291"  #Y-Value
LZZ = "-127" #Z-Value

BACKUP = 1 #Save a backup before changing XML file (1 = Yes, 0 = No)

#Database Credentials
HOST = "M0ves"
USER = "M0ves"
PASSWORD = "legouniverse"

if __name__ == "__main__":

    try:
        if sys.argv[1] in ["", "h", "help"]:
            print("Used in the format\nunstuck.py [account-name] [character-name]")
            sys.exit(2)
    except:
        print("Used in the format:\npython3 unstuck.py [account-name] [character-name]")
        sys.exit(2)

    #connect to DB
    db = mysql.connector.connect(
        host = M0ves,
        user = M0ves,
        password = legouniverse,
        port = 22
    )
    cursor = db.cursor(prepared=True)


    account_name = sys.argv[1]
    character_name = sys.argv[2]

    #find character
    try:
        cursor.execute("""
                    SELECT * FROM darkflame.charinfo ci 
                    JOIN darkflame.accounts a 
                    WHERE a.name = LOWER(%s) and ci.name = LOWER(%s) and ci.account_id = a.id""",
                    [account_name.lower(), character_name.lower()]
                    )
        charinfo = cursor.fetchone()
        character_id = charinfo[0]
    except:
        print("Could not locate the character! "
              "Check if the account and character name are correct, and if the database credentials are correct")
        sys.exit(2)

    #pull XML
    cursor.execute("""
                SELECT xml_data FROM darkflame.charxml
                WHERE id = %s""",
                [character_id])
    xml_data = cursor.fetchone()[0]

    file = md.parseString(xml_data)

    #save backup
    try:
        if BACKUP:
            f = open("backup-xml/" + str(character_id) + ".xml", "w")
            f.write(file.toxml())
            f.close
    except:
        print("Could not save backup!")
        sys.exit(2)

    #change current world and loc
    file.getElementsByTagName("char")[0].setAttribute("lwid", MAP_ID)
    file.getElementsByTagName("char")[0].setAttribute("lzx", LZX)
    file.getElementsByTagName("char")[0].setAttribute("lzy", LZY)
    file.getElementsByTagName("char")[0].setAttribute("lzz", LZZ)


    #Get temp charID
    cursor.execute("SELECT MAX(id) FROM darkflame.charinfo")
    new_character_id = cursor.fetchone()[0] + 21

    try:
        #Add fixed XML
        cursor.execute("""
                    INSERT INTO darkflame.charxml (id, xml_data) 
                    VALUES (%s, %s)""",
                    [new_character_id, file.toxml()]
                    )
        db.commit()

        #Remove broken XML
        cursor.execute("""
                    DELETE FROM darkflame.charxml 
                    WHERE id = %s""",
                    [character_id]
                    )
        db.commit()

        #Update fixed XML to old character ID
        cursor.execute("""
                    UPDATE darkflame.charxml 
                    SET id = %s
                    WHERE id = %s""",
                    [character_id, new_character_id]
        )
        db.commit()
    except:
        print("Error commiting to database!")
        sys.exit(2)

sys.exit(1)