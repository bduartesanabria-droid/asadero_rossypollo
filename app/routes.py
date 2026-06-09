from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func

from app.models import db, Post, Category, Match, Prediction, User, Result, Prize

main_bp = Blueprint('main', __name__)

@main_bp.route('/matches')
@login_required
def list_matches():
    """List all upcoming matches for users"""
    matches = Match.query.order_by(Match.match_date.asc()).all()
    # Get user's existing predictions
    user_predictions = {p.match_id: p for p in current_user.predictions}
    return render_template('matches.html', matches=matches, predictions=user_predictions)

@main_bp.route('/match/<int:match_id>', methods=['GET', 'POST'])
@login_required
def match_detail(match_id):
    """View match details and allow prediction before lock"""
    match = Match.query.get_or_404(match_id)
    existing_prediction = Prediction.query.filter_by(user_id=current_user.id, match_id=match.id).first()
    if request.method == 'POST':
        if match.is_locked:
            flash('El partido está bloqueado y no se pueden enviar pronósticos', 'error')
            return redirect(url_for('main.match_detail', match_id=match.id))
        if existing_prediction:
            flash('Ya has hecho un pronóstico para este partido', 'error')
            return redirect(url_for('main.match_detail', match_id=match.id))

        home_score = int(request.form.get('home_score'))
        away_score = int(request.form.get('away_score'))
        existing_match_score = Prediction.query.filter_by(
            match_id=match.id,
            predicted_home_score=home_score,
            predicted_away_score=away_score
        ).first()
        if existing_match_score:
            flash('Este marcador ya fue seleccionado por otro participante. Debes elegir un resultado diferente.', 'error')
            return redirect(url_for('main.match_detail', match_id=match.id))

        try:
            pred = Prediction(
                user_id=current_user.id,
                match_id=match.id,
                predicted_home_score=home_score,
                predicted_away_score=away_score
            )
            db.session.add(pred)
            db.session.commit()
            flash('Pronóstico guardado', 'success')
            return redirect(url_for('main.list_matches'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar pronóstico: {str(e)}', 'error')
    return render_template('match_detail.html', match=match, prediction=existing_prediction)

@main_bp.route('/leaderboard')
def leaderboard():
    """Display leaderboard based on total points"""
    from sqlalchemy import func
    users_points = db.session.query(User.username, func.coalesce(func.sum(Prediction.points_earned), 0).label('total_points'))\
        .outerjoin(Prediction, Prediction.user_id == User.id)\
        .group_by(User.id)\
        .order_by(func.sum(Prediction.points_earned).desc())\
        .all()
    return render_template('leaderboard.html', users_points=users_points)

@main_bp.route('/admin/calculate_points')
@login_required
def calculate_points_admin():
    """Admin endpoint to calculate points for completed matches"""
    if not current_user.is_admin:
        return jsonify({'error': 'Acceso denegado'}), 403
    predictions = Prediction.query.filter(Prediction.points_earned.is_(None)).all()
    for pred in predictions:
        if pred.match.home_score is not None and pred.match.away_score is not None:
            pred.calculate_points()
    db.session.commit()
    flash('Puntos recalculados para predicciones pendientes', 'success')
    return redirect(url_for('main.admin_matches'))

@main_bp.route('/admin/seed_matches')
@login_required
def seed_matches_admin():
    """Seed initial matches data (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Acceso denegado'}), 403
    from datetime import datetime, timedelta
    seed_data = [
        {'home_team': 'Brasil', 'away_team': 'Argentina', 'match_date': datetime.utcnow() + timedelta(days=1), 'group': 'A'},
        {'home_team': 'España', 'away_team': 'Portugal', 'match_date': datetime.utcnow() + timedelta(days=2), 'group': 'B'},
        {'home_team': 'Alemania', 'away_team': 'Francia', 'match_date': datetime.utcnow() + timedelta(days=3), 'group': 'C'},
    ]
    for data in seed_data:
        exists = Match.query.filter_by(home_team=data['home_team'], away_team=data['away_team'], match_date=data['match_date']).first()
        if not exists:
            m = Match(**data)
            db.session.add(m)
    db.session.commit()
    flash('Partidos iniciales sembrados', 'success')
    return redirect(url_for('main.admin_matches'))

# Admin match management routes
@main_bp.route('/admin/matches')
@login_required
def admin_matches():
    """Lista de partidos para administradores"""
    if not current_user.is_admin:
        return jsonify({'error': 'Acceso denegado'}), 403
    matches = Match.query.order_by(Match.match_date.desc()).all()
    return render_template('admin/matches.html', matches=matches)

@main_bp.route('/admin/match/new', methods=['GET', 'POST'])
@login_required
def create_match():
    """Crear un nuevo partido (solo admin)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Acceso denegado'}), 403
    if request.method == 'POST':
        try:
            from datetime import datetime
            match_date = datetime.fromisoformat(request.form.get('match_date'))
            match = Match(
                home_team=request.form.get('home_team'),
                away_team=request.form.get('away_team'),
                match_date=match_date,
                group=request.form.get('group') or None
            )
            db.session.add(match)
            db.session.commit()
            flash('Partido creado exitosamente', 'success')
            return redirect(url_for('main.admin_matches'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear partido: {str(e)}', 'error')
    return render_template('admin/create_match.html')

@main_bp.route('/admin/match/<int:match_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_match(match_id):
    """Editar un partido o actualizar resultado (solo admin)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Acceso denegado'}), 403
    match = Match.query.get_or_404(match_id)
    locked = match.is_locked

    if request.method == 'POST':
        try:
            if not locked:
                match.home_team = request.form.get('home_team')
                match.away_team = request.form.get('away_team')
                match.match_date = datetime.fromisoformat(request.form.get('match_date'))
            match.home_score = int(request.form.get('home_score')) if request.form.get('home_score') else None
            match.away_score = int(request.form.get('away_score')) if request.form.get('away_score') else None
            match.group = request.form.get('group') or None
            db.session.commit()
            flash('Partido actualizado exitosamente', 'success')
            return redirect(url_for('main.admin_matches'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar partido: {str(e)}', 'error')
    return render_template('admin/edit_match.html', match=match, locked=locked)

@main_bp.route('/admin/update_rankings')
@login_required
def update_rankings_admin():
    """Actualizar el ranking usando los puntos acumulados de cada usuario."""
    if not current_user.is_admin:
        return jsonify({'error': 'Acceso denegado'}), 403

    from app.models import Ranking
    user_points = db.session.query(
        User.id.label('user_id'),
        func.coalesce(func.sum(Prediction.points_earned), 0).label('total_points')
    ).outerjoin(Prediction, Prediction.user_id == User.id).group_by(User.id).all()

    for row in user_points:
        ranking = Ranking.query.filter_by(user_id=row.user_id).first()
        if ranking:
            ranking.points = row.total_points
        else:
            ranking = Ranking(user_id=row.user_id, points=row.total_points)
            db.session.add(ranking)

    db.session.commit()
    flash('Ranking actualizado correctamente', 'success')
    return redirect(url_for('main.admin_matches'))


@main_bp.route('/')
def index():
    """Página principal con hero, próximos partidos y ranking"""
    upcoming_matches = Match.query.filter(Match.match_date >= datetime.utcnow())
    upcoming_matches = upcoming_matches.order_by(Match.match_date.asc()).limit(6).all()

    leaderboard = db.session.query(
        User.username,
        func.coalesce(func.sum(Prediction.points_earned), 0).label('total_points')
    ).outerjoin(Prediction, Prediction.user_id == User.id)
    leaderboard = leaderboard.group_by(User.id)
    leaderboard = leaderboard.order_by(func.sum(Prediction.points_earned).desc()).limit(5).all()

    prizes = [
        {'phase': 'Fase de Grupos', 'title': 'Presas Broaster', 'detail': 'Disfruta un combo especial de presas Rossy Pollo.'},
        {'phase': 'Octavos', 'title': '5% Descuento', 'detail': 'Gana un cupón para tu próxima orden.'},
        {'phase': 'Cuartos', 'title': '25% Descuento', 'detail': 'Aprovecha un ahorro especial en combos.'},
        {'phase': 'Semifinal', 'title': 'Combo Familiar', 'detail': 'Premio para compartir con tu familia.'},
        {'phase': 'Final', 'title': '50% Descuento', 'detail': 'El máximo premio para cerrar la fase.'},
    ]

    prizes = Prize.query.order_by(Prize.phase.asc()).all()
    if not prizes:
        prizes = [
            Prize(name='Presas Broaster', description='Disfruta un combo especial de presas Rossy Pollo.', phase='Fase de Grupos'),
            Prize(name='5% Descuento', description='Gana un cupón para tu próxima orden.', phase='Octavos'),
            Prize(name='25% Descuento', description='Aprovecha un ahorro especial en combos.', phase='Cuartos'),
            Prize(name='Combo Familiar', description='Premio para compartir con tu familia.', phase='Semifinal'),
            Prize(name='50% Descuento', description='El máximo premio para cerrar la fase.', phase='Final')
        ]

    return render_template('index.html', upcoming_matches=upcoming_matches, leaderboard=leaderboard, prizes=prizes)

@main_bp.route('/admin/prizes')
@login_required
def admin_prizes():
    """Lista de premios para administradores"""
    if not current_user.is_admin:
        return jsonify({'error': 'Acceso denegado'}), 403
    prizes = Prize.query.order_by(Prize.phase.asc()).all()
    return render_template('admin/prizes.html', prizes=prizes)

@main_bp.route('/admin/prize/new', methods=['GET', 'POST'])
@login_required
def create_prize():
    """Crear un nuevo premio"""
    if not current_user.is_admin:
        return jsonify({'error': 'Acceso denegado'}), 403

    if request.method == 'POST':
        try:
            prize = Prize(
                name=request.form.get('name'),
                description=request.form.get('description'),
                image_url=request.form.get('image_url'),
                phase=request.form.get('phase')
            )
            db.session.add(prize)
            db.session.commit()
            flash('Premio creado exitosamente', 'success')
            return redirect(url_for('main.admin_prizes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear premio: {str(e)}', 'error')

    return render_template('admin/create_prize.html')

@main_bp.route('/admin/prize/<int:prize_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_prize(prize_id):
    """Editar un premio"""
    if not current_user.is_admin:
        return jsonify({'error': 'Acceso denegado'}), 403
    prize = Prize.query.get_or_404(prize_id)

    if request.method == 'POST':
        try:
            prize.name = request.form.get('name')
            prize.description = request.form.get('description')
            prize.image_url = request.form.get('image_url')
            prize.phase = request.form.get('phase')
            db.session.commit()
            flash('Premio actualizado exitosamente', 'success')
            return redirect(url_for('main.admin_prizes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar premio: {str(e)}', 'error')

    return render_template('admin/edit_prize.html', prize=prize)

@main_bp.route('/admin/prize/<int:prize_id>/delete', methods=['POST'])
@login_required
def delete_prize(prize_id):
    """Eliminar un premio"""
    if not current_user.is_admin:
        return jsonify({'error': 'Acceso denegado'}), 403
    prize = Prize.query.get_or_404(prize_id)

    try:
        db.session.delete(prize)
        db.session.commit()
        flash('Premio eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar premio: {str(e)}', 'error')

    return redirect(url_for('main.admin_prizes'))

@main_bp.route('/post/<slug>')
def view_post(slug):
    """Ver un post completo"""
    post = Post.query.filter_by(slug=slug).first_or_404()

    # Incrementar contador de vistas
    if post.is_published:
        post.views += 1
        db.session.commit()

    return render_template('post.html', post=post)

@main_bp.route('/category/<slug>')
def view_category(slug):
    """Ver posts de una categoría"""
    category = Category.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)

    posts = Post.query.filter_by(
        category_id=category.id,
        is_published=True
    ).order_by(Post.created_at.desc()).paginate(page=page, per_page=10)

    return render_template('category.html', category=category, posts=posts)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Panel de usuario con estadísticas de pronósticos y próximos partidos"""
    predictions = Prediction.query.filter_by(user_id=current_user.id).join(Match).order_by(Match.match_date.asc()).all()
    total_points = sum((p.points_earned or 0) for p in predictions)
    exact_hits = sum(1 for p in predictions if p.points_earned == 3)
    winner_hits = sum(1 for p in predictions if p.points_earned == 1)
    total_forecasts = len(predictions)
    accuracy = int(((exact_hits + winner_hits) / total_forecasts) * 100) if total_forecasts else 0

    upcoming_matches = Match.query.filter(Match.match_date >= datetime.utcnow())
    upcoming_matches = upcoming_matches.order_by(Match.match_date.asc()).limit(4).all()

    return render_template(
        'dashboard.html',
        predictions=predictions,
        total_points=total_points,
        exact_hits=exact_hits,
        winner_hits=winner_hits,
        total_forecasts=total_forecasts,
        accuracy=accuracy,
        upcoming_matches=upcoming_matches
    )

@main_bp.route('/results')
@login_required
def results():
    """Ver los resultados personales del usuario"""
    user_results = Result.query.filter_by(user_id=current_user.id).order_by(Result.created_at.desc()).all()
    return render_template('results.html', results=user_results)

@main_bp.route('/admin/results')
@login_required
def admin_results():
    """Ver todos los resultados y ganadores (solo admin)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Acceso denegado'}), 403

    winners = Result.query.filter_by(is_winner=True).order_by(Result.created_at.desc()).all()
    all_results = Result.query.order_by(Result.created_at.desc()).all()
    return render_template('admin/results.html', winners=winners, results=all_results)

@main_bp.route('/admin/post/new', methods=['GET', 'POST'])
@login_required
def create_post():
    """Crear un nuevo post (solo admins o autores)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Acceso denegado'}), 403

    if request.method == 'POST':
        try:
            post = Post(
                title=request.form.get('title'),
                slug=request.form.get('slug'),
                content=request.form.get('content'),
                excerpt=request.form.get('excerpt'),
                user_id=current_user.id,
                category_id=request.form.get('category_id'),
                is_published=request.form.get('is_published') == 'on'
            )
            db.session.add(post)
            db.session.commit()

            return jsonify({'message': 'Post creado exitosamente', 'id': post.id}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    categories = Category.query.all()
    return render_template('admin/create_post.html', categories=categories)

@main_bp.route('/admin/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """Editar un post"""
    post = Post.query.get_or_404(post_id)

    # Verificar que sea el autor o admin
    if post.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Acceso denegado'}), 403

    if request.method == 'POST':
        try:
            post.title = request.form.get('title')
            post.slug = request.form.get('slug')
            post.content = request.form.get('content')
            post.excerpt = request.form.get('excerpt')
            post.category_id = request.form.get('category_id')
            post.is_published = request.form.get('is_published') == 'on'

            db.session.commit()
            return jsonify({'message': 'Post actualizado exitosamente'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    categories = Category.query.all()
    return render_template('admin/edit_post.html', post=post, categories=categories)

@main_bp.route('/admin/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """Eliminar un post"""
    post = Post.query.get_or_404(post_id)

    # Verificar que sea el autor o admin
    if post.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Acceso denegado'}), 403

    try:
        db.session.delete(post)
        db.session.commit()
        return jsonify({'message': 'Post eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@main_bp.route('/api/search')
def search():
    """API de búsqueda"""
    query = request.args.get('q', '')

    if len(query) < 2:
        return jsonify({'results': []})

    search_results = Post.query.filter(
        Post.is_published == True,
        Post.title.ilike(f'%{query}%')
    ).limit(10).all()

    return jsonify({
        'results': [
            {'id': post.id, 'title': post.title, 'slug': post.slug}
            for post in search_results
        ]
    })
