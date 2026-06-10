import os
import sys
from datetime import datetime as dt, timedelta

# Asegurar que estamos en el contexto de Flask
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, User, Match, Prize, Prediction

def seed_database():
    app = create_app('development')
    with app.app_context():
        print("Iniciando carga de información hardcodeada (seed)...")

        # 1. Crear usuarios de prueba si no existen
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            test_user = User(username='testuser', email='test@test.com')
            test_user.set_password('password')
            db.session.add(test_user)
            print("  - Creado usuario de prueba (testuser / password)")
        
        # 2. Insertar Premios
        prizes = [
            {'name': 'Presas Broaster', 'description': 'Disfruta un combo especial de presas Rossy Pollo.', 'phase': 'Fase de Grupos'},
            {'name': '5% Descuento', 'description': 'Gana un cupón para tu próxima orden.', 'phase': 'Octavos'},
            {'name': '25% Descuento', 'description': 'Aprovecha un ahorro especial en combos.', 'phase': 'Cuartos'},
            {'name': 'Combo Familiar', 'description': 'Premio para compartir con tu familia.', 'phase': 'Semifinal'},
            {'name': '50% Descuento', 'description': 'El máximo premio para cerrar la fase.', 'phase': 'Final'}
        ]
        
        prize_count = 0
        for p in prizes:
            if not Prize.query.filter_by(name=p['name']).first():
                db.session.add(Prize(**p))
                prize_count += 1
        if prize_count > 0:
            print(f"  - Creados {prize_count} premios")

        # 3. Insertar Partidos
        seed_data = [
            # ---- Group A ----
            {'home_team': 'México', 'away_team': 'Sudáfrica', 'match_date': dt(2026, 6, 11, 15, 0), 'group': 'A'},
            {'home_team': 'Corea del Sur', 'away_team': 'República Checa', 'match_date': dt(2026, 6, 11, 22, 0), 'group': 'A'},
            # ---- Group B ----
            {'home_team': 'Canadá', 'away_team': 'Bosnia y Herzegovina', 'match_date': dt(2026, 6, 12, 15, 0), 'group': 'B'},
            {'home_team': 'Qatar', 'away_team': 'Suiza', 'match_date': dt(2026, 6, 13, 15, 0), 'group': 'B'},
            # Un partido viejo que ya está bloqueado (hace 2 días)
            {'home_team': 'Brasil', 'away_team': 'Marruecos', 'match_date': dt.now() - timedelta(days=2), 'group': 'C', 'home_score': 2, 'away_score': 1},
            # Un partido pronto a empezar
            {'home_team': 'EE.UU.', 'away_team': 'Australia', 'match_date': dt.now() + timedelta(hours=2), 'group': 'D'},
        ]
        
        match_count = 0
        for data in seed_data:
            exists = Match.query.filter_by(home_team=data['home_team'], away_team=data['away_team']).first()
            if not exists:
                m = Match(**data)
                db.session.add(m)
                match_count += 1
        
        db.session.commit()
        if match_count > 0:
            print(f"  - Creados {match_count} partidos hardcodeados")

        # 4. Crear algunas predicciones de prueba (usando test_user)
        match_bra = Match.query.filter_by(home_team='Brasil').first()
        if match_bra:
            # Crear prediccion si no existe
            pred_exists = Prediction.query.filter_by(user_id=test_user.id, match_id=match_bra.id).first()
            if not pred_exists:
                pred = Prediction(user_id=test_user.id, match_id=match_bra.id, predicted_home_score=2, predicted_away_score=0)
                db.session.add(pred)
                db.session.commit()
                # Y calcular puntos para ver el resultado!
                pred.calculate_points()
                db.session.commit()
                print("  - Creada predicción de prueba para el partido de Brasil")

        print("¡Base de datos hardcodeada con éxito para pruebas!")

if __name__ == '__main__':
    seed_database()
