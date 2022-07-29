import cx_Oracle
import csv

connection = cx_Oracle.connect("SOFIWI", "sofiwi123", "localhost:1521")

"""
nombre función: createStore
parámetros: conexion a base de datos

esta funcion crea una tabla vacia con las columnas de la tabla tienda, para luego ser rellenada
"""
def createStore(conn):
    cur = conn.cursor()

    #si la tabla tienda ya existe, la borra
    cur.execute("BEGIN EXECUTE IMMEDIATE 'DROP TABLE STORE'; EXCEPTION WHEN OTHERS THEN NULL; END;")

    cur.execute(
    """
        CREATE TABLE STORE(
            Rank INTEGER,
            Name VARCHAR(200),
            Platform VARCHAR(200),
            Year INTEGER,
            Genre VARCHAR(200),
            Publisher VARCHAR(200),
            NA_Sales FLOAT,
            EU_Sales FLOAT,
            JP_Sales FLOAT,
            Other_Sales FLOAT,
            Global_Sales FLOAT
        )
    """
)

"""
nombre función: fillStore
parámetros: conexion a base de datos

esta funcion rellena la tabla tienda con el archivo csv
"""
def fillStore(conn):
    cur = conn.cursor()
  
    with open("juegos.csv", newline="",encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter = ',')
        next(csv_reader)
        for lines in csv_reader:
            lines[0] = int(lines[0]) if lines[0] != 'N/A' else 0
            lines[3] = int(lines[3])if lines[3] != 'N/A' else 0
            lines[6] = float(lines[6])if lines[6] != 'N/A' else 0.0
            lines[7] = float(lines[7])if lines[7] != 'N/A' else 0.0
            lines[8] = float(lines[8])if lines[8] != 'N/A' else 0.0
            lines[9] = float(lines[9])if lines[9] != 'N/A' else 0.0
            lines[10] = float(lines[10])if lines[10] != 'N/A' else 0.0

            cur.execute("INSERT INTO STORE VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11)", 
            (lines[0], lines[1], lines[2], lines[3], lines[4], lines[5], lines[6], lines[7], lines[8], lines[9], lines[10])) 

            conn.commit()

"""
nombre función: adPRKey
parámetros: conexion a base de datos

esta funcion añade una primary key a la tabla biblioteca
"""
def addPRKey(conn):
    cur = conn.cursor()
    cur.execute("""
        ALTER TABLE LIBRARY 
        ADD CONSTRAINT pk_game PRIMARY KEY (game);
    """)

"""
nombre función: createLibrary
parámetros: conexion a base de datos

esta funcion crea una tabla vacia con las columnas de la tabla biblioteca, para luego ser rellenada con las compras del usuario
"""
def createLibrary(conn):
    cur = conn.cursor()
    
    #si la tabla ya existe la borra
    cur.execute("BEGIN EXECUTE IMMEDIATE 'DROP TABLE LIBRARY'; EXCEPTION WHEN OTHERS THEN NULL; END;")
    #crea tabla biblioteca vacia
    cur.execute(
        """
            CREATE TABLE LIBRARY(
                Id INTEGER,
                Rank INTEGER,
                Name VARCHAR(200),
                Platform VARCHAR(200),
                Year INTEGER,
                Genre VARCHAR(200),
                Publisher VARCHAR(200),
                Rating INTEGER
            )
        """

    )
    conn.commit()

"""
nombre función: deleteLibrary
parámetros: conexion a base de datos

esta funcion borra la tabla biblioteca
"""
def deleteLibrary(conn):
    cur = conn.cursor()
    cur.execute("DROP TABLE LIBRARY")
    conn.commit()

"""
nombre función: showLibrary
parámetros: conexion a base de datos

esta funcion imprime en pantalla la biblioteca del usuario
"""
def showLibrary(conn):
    cur = conn.cursor()
    cur.execute("SELECT NAME FROM LIBRARY")
    games = cur.fetchall()
    viewTableLibrary(games)

"""
nombre función: buyGame
parámetros: conexion a base de datos

esta funcion busca el juego que el usuario quiere comprar y lo inserta en la tabla biblioteca, luego de preguntarle un rating al usuario
"""
def buyGame(conn):
    game = input("Ingrese el nombre del juego que desea comprar: ")
    platform = input("¿Para qué consola quiere su juego?: ")
    cur = conn.cursor()

    cur.execute("SELECT * FROM STORE WHERE Name='"+game+"' AND Platform ='"+platform+"'")
    result = cur.fetchone()

    cur.execute("SELECT * FROM LIBRARY WHERE Name='"+game+"' AND Platform ='"+platform+"'")
    purchased = cur.fetchone()

    if purchased:
        print("No se pudo realizar la compra, ya has comprado el juego")
        
    else:
        rating = int(input(f"Ingrese un rating del 1 al 5 que le quiere dar al juego {game}: "))
        cur.execute("INSERT INTO LIBRARY VALUES (:1, :2, :3, :4, :5, :6, :7, :8)", 
        (num_id, result[0], result[1], result[2], result[3], result[4], result[5], rating))
        conn.commit()
        print(f"{game} comprado existosamente!")

"""
nombre función: top5GamesSold
parámetros: conexion a base de datos

esta funcion imprime por pantalla los 5 juegos más vendidos
"""
def top5GamesSold(conn):
    cur = conn.cursor()
    cur.execute("SELECT NAME FROM STORE ORDER BY Global_Sales DESC")
    results = cur.fetchall()[:5]
    viewList(results)

"""
nombre función: top5GamesByGenre
parámetros: conexion a base de datos

esta funcion imprime por pantalla los 5 juegos más vendidos por género. El género se le pregunta al usuario 
"""
def top5GamesByGenre(conn):
    cur = conn.cursor()
    genre = input("¿De qué genero quiere obtener los juegos más vendido?: ")
    cur.execute("SELECT NAME FROM STORE WHERE Genre = '"+genre+"'")
    results = cur.fetchall()[:5]
    viewList(results)

"""
nombre función: deleteGame
parámetros: conexion a base de datos

esta funcion borra un juego de la tabla biblioteca
"""
def deleteGame(conn):
    cur = conn.cursor()
    game = input("¿Qué juego le gustaría eliminar?: ")
    cur.execute("SELECT * FROM LIBRARY WHERE  Name='"+game+"'")
    purchased = cur.fetchall()

    if purchased:
        cur.execute("DELETE FROM LIBRARY WHERE Name='"+game+"'")
        conn.commit()
        print(f"{game} borrado exitosamente")
    else:
        print("No has comprado ese juego!")

"""
nombre función: updateRating
parámetros: conexion a base de datos

esta funcion alctualiza el rating de un juego de la tabla biblioteca
"""
def updateRating(conn):
    cur = conn.cursor()
    game = input("¿De qué juego quiere actualizar la calificación?: ")
    cur.execute("SELECT * FROM LIBRARY WHERE Name='"+game+"'")
    purchased = cur.fetchall()

    if purchased:
        rating = input("¿Qué calificación le quiere poner?: ")
        cur.execute("UPDATE LIBRARY SET Rating='"+rating+"' WHERE Name='"+game+"'")
        conn.commit()
    else:
        print("No has comprado ese juego!")

"""
nombre función: searchGameName
parámetros: conexion a base de datos

esta funcion permite buscar un juego por nombre en la tienda
"""
def searchGameName(conn):
    cur = conn.cursor()
    print("\t1. Buscar juego por tienda\n\t2. Buscar juego por biblioteca")
    choice = int(input("Ingrese su elección: "))
    game = input("¿Qué juego desea buscar?: ")
    num = int(input("¿Cuántos resultados desea mostrar?: "))

    if choice == 1:
        cur.execute("SELECT * FROM STORE WHERE Name='"+game+"'")
        results = cur.fetchall()
        if results:
            viewTableStore(results[:num])
        else: 
            print("No se encontraron resultados")
    elif choice == 2:
        cur.execute("SELECT * FROM LIBRARY WHERE Name='"+game+"'")
        results = cur.fetchall()
        if results:
            viewTableLibrary(results[:num])
        else:
            print("No se encontraron resultados")

"""
nombre función: searchGamePlatform
parámetros: conexion a base de datos

esta funcion permite buscar juegos por plataformas en la tienda
"""
def searchGamePlatform(conn):
    cur = conn.cursor()
    print("\t1. Buscar juego por tienda\n\t2. Buscar juego por biblioteca")
    choice = int(input("Ingrese su elección: "))
    platform = input("¿Qué plataforma desea buscar?: ")
    num = int(input("¿Cuántos resultados desea mostrar?: "))

    if choice == 1:
        cur.execute("SELECT * FROM STORE WHERE Platform ='"+platform+"'")
        results = cur.fetchall()
        if results:
            viewTableStore(results[:num])
            
        else:
            print("No se encontraron resultados")
    elif choice == 2:
        cur.execute("SELECT * FROM LIBRARY WHERE Platform ='"+platform+"'")
        results = cur.fetchall()
        if results:
            viewTableLibrary(results[:num])
        else:
            print("No se encontraron resultados")

"""
nombre función: viewTableStore
parámetros: conexion a base de datos

esta funcion imprime por pantalla ciertas filas de la tabla tienda
"""
def viewTableStore(list):
    maxLen = 0
    for item in list:
        for tupla in item:
            if len(str(tupla)) > maxLen:
                maxLen = len(item)

    spaces = " " * maxLen

    print(f"Name {spaces} Platform {spaces} Year   Genre {spaces} Publisher {spaces}")

    for item in list:
        difName = " " *(max(0, len("Name"+spaces) - len(str(item[1]))))
        difPlatfrom = " "*(max(0, len("Platfrom"+spaces) - len(str(item[2]))))
        difYear = " "*(max(0, len("Year"+spaces) - len(str(item[3]))))
        difGenre = " "*(max(0, len("Genre"+spaces) - len(str(item[4]))))
        print(f"{item[1]}{difName}   {item[2]}{difPlatfrom}   {item[3]}{difYear}   {item[4]}{difGenre}   {item[5]}")

"""
nombre función: viewTableLibrary
parámetros: conexion a base de datos

esta funcion imprime por pantalla ciertas filas de la tabla biblioteca
"""
def viewTableLibrary(list):
    maxLen = 0
    for item in list:
        for tupla in item:
            if len(str(tupla)) > maxLen:
                maxLen = len(item)

    spaces = " " * maxLen

    print(f"Name {spaces} Platform {spaces} Year   Genre {spaces} Publisher {spaces}")

    for item in list:
        difName = " " *(max(0, len("Name"+spaces) - len(str(item[2]))))
        difPlatfrom = " "*(max(0, len("Platfrom"+spaces) - len(str(item[3]))))
        difYear = " "*(max(0, len("Year"+spaces) - len(str(item[4]))))
        difGenre = " "*(max(0, len("Genre"+spaces) - len(str(item[5]))))
        print(f"{item[2]}{difName}   {item[3]}{difPlatfrom}   {item[4]}{difYear}   {item[5]}{difGenre}   {item[6]}")

"""
nombre función: viewList
parámetros: conexion a base de datos

esta funcion imprime por pantalla una lista de manera enumerada
"""
def viewList(list):
    for i in range(1, len(list)):
        print(f"\t{i}. {list[i][0]}")



menu = True

print("Bienvenidx, nuevo usuario!")
print("Creando tabla tienda...")

createStore(connection)
fillStore(connection)
createLibrary(connection)

while(menu):
    print("¿Qué desea hacer?")
    print("\t1. Mostrar biblioteca \n\t2. Comprar un juego\n\t3. Mostrar top 5 juegos más vendidos\n\t4. Mostrar top 5 juegos según género\n\t5. Eliminar un juego\n\t6. Actualizar calificación de un juego\n\t7. Buscar juego según nombre\n\t8. Buscar juego según Plataforma\n\t9. Eliminar todos los juegos de su biblioteca\n\t10. Salir")
    choice = int(input("Ingrese su elección: "))

    if choice == 1:
        print("Estos son los juegos que has comprado:")
        showLibrary(connection)
    
    elif choice == 2:
        num_id = 0
        buyGame(connection)
        num_id += 1
    
    elif choice == 3:
        top5GamesSold(connection)
    
    elif choice == 4:
        top5GamesByGenre(connection)

    elif choice == 5:
        deleteGame(connection)

    elif choice == 6:
        updateRating(connection)
    
    elif choice == 7:
        searchGameName(connection)
    
    elif choice == 8:
        searchGamePlatform(connection)
    
    elif choice == 9:
        deleteLibrary(connection)

    elif choice == 10:
        menu = False

connection.close()