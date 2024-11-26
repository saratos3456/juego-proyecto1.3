import hashlib
import os
import json
import random 
from dataclasses import dataclass

DATABASE = "usuarios_triqui.txt"
DATABASE_JSON = "usuarios_triqui.json"  # Archivo JSON para almacenar usuarios
usuario_actual = None
TAMAÑO_TABLERO = 3

@dataclass
class Usuario:
    username: str
    password_cifrada: str

# Función para cifrar la contraseña usando SHA-256
def cifrar_clave(clave):
    return hashlib.sha256(clave.encode()).hexdigest()

# Función para registrar un nuevo usuario
def registrar_usuario(username, password):
    password_cifrada = cifrar_clave(password)
    
    if usuario_existe(username):
        print("El usuario ya existe. Elige otro nombre de usuario.")
        return False

    usuario = Usuario(username, password_cifrada)

    with open(DATABASE, "a") as f:
        f.write(f"{usuario.username},{usuario.password_cifrada}\n")
    
    # Agregar el usuario al archivo JSON
    usuarios = cargar_usuarios_json()
    usuarios[usuario.username] = usuario.password_cifrada
    guardar_usuarios_json(usuarios)

    print(f"Usuario {usuario.username} registrado con éxito.")
    return True

# Función para verificar si un usuario ya existe
def usuario_existe(username):
    if os.path.exists(DATABASE):
        with open(DATABASE, "r") as f:
            for line in f:
                user, _ = line.strip().split(",")
                if user == username:
                    return True
                    
    usuarios = cargar_usuarios_json()
    return username in usuarios

# Función para cargar usuarios desde el archivo JSON
def cargar_usuarios_json():
    if os.path.exists(DATABASE_JSON):
        with open(DATABASE_JSON, "r") as f:
            return json.load(f)
    return {}

# Función para guardar usuarios en el archivo JSON
def guardar_usuarios_json(usuarios):
    with open(DATABASE_JSON, "w") as f:
        json.dump(usuarios, f)

# Función para iniciar sesión
def iniciar_sesion(username, password):
    global usuario_actual
    password_cifrada = cifrar_clave(password)
    
    with open(DATABASE, "r") as f:
        for line in f:
            user, pass_cifrada = line.strip().split(",")
            if user == username and pass_cifrada == password_cifrada:
                usuario_actual = username
                print(f"Inicio de sesión exitoso. ¡Bienvenido {username}!")
                return True

    print("Usuario o contraseña incorrectos.")
    return False

# Función para cerrar sesión
def cerrar_sesion():
    global usuario_actual
    if usuario_actual:
        print(f"Sesión de {usuario_actual} cerrada.")
        usuario_actual = None
    else:
        print("No hay sesión activa.")

# Función para editar la contraseña
def editar_clave(username, nueva_clave):
    password_cifrada = cifrar_clave(nueva_clave)
    
    if not usuario_existe(username):
        print("El usuario no existe.")
        return False

    with open(DATABASE, "r") as f:
        usuarios = f.readlines()

    with open(DATABASE, "w") as f:
        for line in usuarios:
            user, _ = line.strip().split(",")
            if user == username:
                f.write(f"{username},{password_cifrada}\n")
            else:
                f.write(line)

    usuarios_json = cargar_usuarios_json()
    usuarios_json[username] = password_cifrada
    guardar_usuarios_json(usuarios_json)

    print(f"Contraseña de {username} actualizada con éxito.")
    return True

# Función para eliminar una cuenta
def eliminar_cuenta(username):
    global usuario_actual
    if not usuario_existe(username):
        print("El usuario no existe.")
        return False

    with open(DATABASE, "r") as f:
        usuarios = f.readlines()

    with open(DATABASE, "w") as f:
        for line in usuarios:
            user, _ = line.strip().split(",")
            if user != username:
                f.write(line)

    usuarios_json = cargar_usuarios_json()
    if username in usuarios_json:
        del usuarios_json[username]
        guardar_usuarios_json(usuarios_json)

    if usuario_actual == username:
        usuario_actual = None
        print(f"La cuenta {username} ha sido eliminada. Se ha cerrado la sesión.")

    print(f"Cuenta {username} eliminada con éxito.")
    return True

# Función para mostrar el tablero del Triqui
def mostrar_tablero(tablero):
    for fila in tablero:
        print(" | ".join(fila))
        print("-" * (TAMAÑO_TABLERO * 2))

# Función para revisar si hay un ganador
def revisar_ganador(tablero, jugador):
    for fila in tablero:
        if all([cell == jugador for cell in fila]):
            return True

    for columna in range(TAMAÑO_TABLERO):
        if all([tablero[fila][columna] == jugador for fila in range(TAMAÑO_TABLERO)]):
            return True

    if all([tablero[i][i] == jugador for i in range(TAMAÑO_TABLERO)]) or \
       all([tablero[i][TAMAÑO_TABLERO - i - 1] == jugador for i in range(TAMAÑO_TABLERO)]):
        return True

    return False

# Función para verificar si hay un empate
def verificar_empate(tablero):
    return all([cell != " " for fila in tablero for cell in fila])

# Función para el movimiento de la máquina
def movimiento_maquina(tablero):
    movimientos_disponibles = [(fila, col) for fila in range(TAMAÑO_TABLERO) for col in range(TAMAÑO_TABLERO) if tablero[fila][col] == " "]

    if movimientos_disponibles:
        # Seleccionar un movimiento aleatorio de los disponibles
        fila, columna = random.choice(movimientos_disponibles)
        tablero[fila][columna] = "O"  # La máquina coloca su marca en la posición seleccionada
        print("La máquina ha hecho su movimiento.")
    else:
        print("No hay movimientos disponibles para la máquina.")

# Función para jugar el modo Jugador vs Máquina
def jugar_triqui():
    if not usuario_actual:
        print("Debes iniciar sesión para jugar.")
        return

    tablero = [[" " for _ in range(TAMAÑO_TABLERO)] for _ in range(TAMAÑO_TABLERO)]
    turno = 0
    jugadores = ["X", "O"]

    while True:
        mostrar_tablero(tablero)
        jugador = jugadores[turno % 2]

        if jugador == "X":  # Turno del usuario
            print(f"Turno del jugador {jugador} (Jugador actual: {usuario_actual})")

            try:
                fila = int(input(f"Selecciona la fila (0 a {TAMAÑO_TABLERO - 1}): "))
                columna = int(input(f"Selecciona la columna (0 a {TAMAÑO_TABLERO - 1}): "))
                if fila not in range(TAMAÑO_TABLERO) or columna not in range(TAMAÑO_TABLERO):
                    print(f"Fila o columna inválida. Deben estar entre 0 y {TAMAÑO_TABLERO - 1}.")
                    continue
            except ValueError:
                print("Entrada no válida. Intenta de nuevo.")
                continue

            if tablero[fila][columna] == " ":
                tablero[fila][columna] = jugador
            else:
                print("Posición no válida. El espacio ya está ocupado. Intenta de nuevo.")
                continue
        else:  # Turno de la máquina
            movimiento_maquina(tablero)

        if revisar_ganador(tablero, jugador):
            mostrar_tablero(tablero)
            print(f"¡Jugador {jugador} gana!")
            break

        if verificar_empate(tablero):
            mostrar_tablero(tablero)
            print("¡Es un empate!")
            break

        turno += 1

    input("Presiona Enter para volver al menú principal.")

# Función para jugar el modo Jugador vs Jugador
def jugar_triqui_jugador_vs_jugador():
    tablero = [[" " for _ in range(TAMAÑO_TABLERO)] for _ in range(TAMAÑO_TABLERO)]
    turno = 0
    jugadores = ["X", "O"]

    while True:
        mostrar_tablero(tablero)
        jugador = jugadores[turno % 2]
        print(f"Turno del jugador {jugador}")

        try:
            fila = int(input(f"Selecciona la fila (0 a {TAMAÑO_TABLERO - 1}): "))
            columna = int(input(f"Selecciona la columna (0 a {TAMAÑO_TABLERO - 1}): "))
            if fila not in range(TAMAÑO_TABLERO) or columna not in range(TAMAÑO_TABLERO):
                print(f"Fila o columna inválida. Deben estar entre 0 y {TAMAÑO_TABLERO - 1}.")
                continue
        except ValueError:
            print("Entrada no válida. Intenta de nuevo.")
            continue

        if tablero[fila][columna] == " ":
            tablero[fila][columna] = jugador
        else:
            print("Posición no válida. El espacio ya está ocupado. Intenta de nuevo.")
            continue

        if revisar_ganador(tablero, jugador):
            mostrar_tablero(tablero)
            print(f"¡Jugador {jugador} gana!")
            break

        if verificar_empate(tablero):
            mostrar_tablero(tablero)
            print("¡Es un empate!")
            break

        turno += 1

    input("Presiona Enter para volver al menú principal.")

# Función para seleccionar el modo de juego
def seleccionar_modo_juego():
    print("\n--- Seleccionar Modo de Juego ---")
    print("1. Jugador vs Máquina")
    print("2. Jugador vs Jugador")
    
    opcion = input("Selecciona una opción: ")

    if opcion == "1":
        jugar_triqui()
    elif opcion == "2":
        jugar_triqui_jugador_vs_jugador()
    else:
        print("Opción no válida. Intenta de nuevo.")

# Función principal del menú
def menu_principal():
    while True:
        print("\n--- Menú Principal ---")
        print("1. Registrar usuario")
        print("2. Iniciar sesión")
        print("3. Editar clave")
        print("4. Eliminar cuenta")
        print("5. Seleccionar modo de juego")
        print("6. Cerrar sesión")
        print("7. Salir")

        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            username = input("Nombre de usuario: ")
            password = input("Contraseña: ")
            registrar_usuario(username, password)
        elif opcion == "2":
            username = input("Nombre de usuario: ")
            password = input("Contraseña: ")
            iniciar_sesion(username, password)
        elif opcion == "3":
            if usuario_actual:
                nueva_clave = input("Nueva contraseña: ")
                editar_clave(usuario_actual, nueva_clave)
            else:
                print("Debes iniciar sesión para cambiar la contraseña.")
        elif opcion == "4":
            username = input("Nombre de usuario a eliminar: ")
            eliminar_cuenta(username)
        elif opcion == "5":
            seleccionar_modo_juego()
        elif opcion == "6":
            cerrar_sesion()
        elif opcion == "7":
            print("Saliendo del juego. ¡Hasta luego!")
            break
        else:
            print("Opción no válida. Intenta de nuevo.")

# Iniciar el menú principal
menu_principal()
