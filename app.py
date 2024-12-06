import streamlit as st
import pandas as pd
import hashlib
import random
from datetime import datetime

# Datos de ejemplo
users = pd.DataFrame(columns=['username', 'email', 'password', 'tokens', 'referral_code', 'referral_from'])
matches = pd.DataFrame(columns=['team1', 'team2', 'date', 'result', 'bets'])
admin_code = "LIGA2024"
admin_data = {'admin': 'admin', 'password': 'adminpassword'}  # Contraseña para admin

# Funciones para manejo de usuarios
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(stored_password, entered_password):
    return stored_password == hash_password(entered_password)

# Función de registro de usuarios
def register_user(username, email, password, referral_code=None):
    if referral_code:
        referrer = users[users['referral_code'] == referral_code]
        if not referrer.empty:
            referral_from = referrer.iloc[0]['username']
        else:
            referral_from = None
    else:
        referral_from = None

    new_user = {
        'username': username,
        'email': email,
        'password': hash_password(password),
        'tokens': 1000,
        'referral_code': f'{username}_{random.randint(1000, 9999)}',
        'referral_from': referral_from
    }
    users.loc[len(users)] = new_user

# Función de login
def login_user(email, password):
    user = users[users['email'] == email]
    if not user.empty and check_password(user.iloc[0]['password'], password):
        return user.iloc[0]
    return None

# Función para agregar partido
def add_match(team1, team2, date):
    match = {'team1': team1, 'team2': team2, 'date': date, 'result': None, 'bets': []}
    matches.loc[len(matches)] = match

# Función para registrar resultado y distribuir tokens
def record_result(match_id, result):
    match = matches.iloc[match_id]
    match['result'] = result
    for bet in match['bets']:
        user = users[users['username'] == bet['username']]
        user_tokens = bet['tokens']
        if result == bet['prediction']:
            user['tokens'] += 0.8 * user_tokens
        else:
            user['tokens'] += 0.2 * user_tokens
    # Admin recibe el 20% de todas las apuestas
    admin_user = users[users['username'] == 'admin']
    admin_user['tokens'] += 0.2 * sum([bet['tokens'] for bet in match['bets']])

# Página principal
def main_page():
    st.title('Bienvenido a LaLigaBets')
    st.write("¡Participa en las apuestas de los partidos de La Liga Española!")
    st.sidebar.title("Menú")
    st.sidebar.button("Ir a Galería de la Fama")
    st.sidebar.button("Ver partidos próximos")

# Galería de la Fama
def fame_gallery():
    st.title("Galería de la Fama")
    top_users = users.sort_values(by='tokens', ascending=False).head(10)
    for i, row in top_users.iterrows():
        st.write(f"{row['username']} - {row['tokens']} tokens")

# Perfil de usuario
def profile(user):
    st.title(f"Perfil de {user['username']}")
    st.write(f"Email: {user['email']}")
    st.write(f"Tokens: {user['tokens']}")
    st.write(f"Referidos: {user['referral_from']}")

# Página de administración
def admin_page():
    st.title('Administración')
    if st.button("Agregar partido"):
        team1 = st.text_input("Equipo 1")
        team2 = st.text_input("Equipo 2")
        date = st.date_input("Fecha")
        if st.button("Registrar partido"):
            add_match(team1, team2, date)
            st.success("Partido agregado exitosamente.")

# Página de partidos próximos
def upcoming_matches():
    st.title('Partidos próximos')
    for i, match in matches.iterrows():
        st.write(f"{match['team1']} vs {match['team2']} - {match['date']}")
        if match['result'] is None:
            prediction = st.text_input(f"Apuesta para {match['team1']} vs {match['team2']}", key=i)
            tokens = st.number_input("Tokens a apostar", min_value=0, max_value=user['tokens'])
            if st.button("Apostar"):
                user['tokens'] -= tokens
                match['bets'].append({'username': user['username'], 'tokens': tokens, 'prediction': prediction})
                st.success("Apuesta realizada")

# Estructura principal de la app
def run_app():
    st.sidebar.title("Menú")
    pages = ["Inicio", "Registro", "Login", "Perfil", "Próximos partidos", "Galería de la fama"]
    choice = st.sidebar.selectbox("Selecciona una página", pages)

    if choice == "Inicio":
        main_page()
    elif choice == "Registro":
        username = st.text_input("Nombre de usuario")
        email = st.text_input("Correo electrónico")
        password = st.text_input("Contraseña", type="password")
        confirm_password = st.text_input("Confirmar contraseña", type="password")
        referral_code = st.text_input("Código de referido (opcional)")
        if password == confirm_password:
            if st.button("Registrarse"):
                register_user(username, email, password, referral_code)
                st.success("Usuario registrado exitosamente.")
        else:
            st.error("Las contraseñas no coinciden.")
    elif choice == "Login":
        email = st.text_input("Correo electrónico")
        password = st.text_input("Contraseña", type="password")
        user = login_user(email, password)
        if user is not None:
            profile(user)
        else:
            st.error("Credenciales incorrectas.")
    elif choice == "Próximos partidos":
        upcoming_matches()
    elif choice == "Galería de la fama":
        fame_gallery()

    if st.sidebar.button('Ir a Administración') and user['username'] == 'admin':
        admin_page()

if __name__ == "__main__":
    run_app()
