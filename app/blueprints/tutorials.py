from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, session
from flask_login import login_required, current_user
from app.decorators import admin_required
from app.extensions import db
from app.models.tutorial import Tutorial, Category, Tag
from app.forms import TutorialForm, CategoryForm, TagForm

bp = Blueprint('tutorials', __name__, url_prefix='/tutorials')


@bp.route('/')
def list():
    category_slug = request.args.get('category')
    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first_or_404()
        tutorials = Tutorial.query.filter_by(category_id=category.id, is_published=True).all()
    else:
        tutorials = Tutorial.query.filter_by(is_published=True).all()
    categories = Category.query.order_by(Category.sort_order).all()
    return render_template('tutorials_list.html.j2', tutorials=tutorials, categories=categories)


@bp.route('/<slug>')
def view(slug):
    tutorial = Tutorial.query.filter_by(slug=slug).first_or_404()
    if not tutorial.is_published and not (current_user.is_authenticated and current_user.is_admin()):
        abort(404)

    if not session.get(f'viewed_tutorial_{tutorial.id}'):
        tutorial.view_count += 1
        db.session.commit()
        session[f'viewed_tutorial_{tutorial.id}'] = True
    return render_template('tutorials_view.html.j2', tutorial=tutorial)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = TutorialForm()
    if form.validate_on_submit():
        tutorial = Tutorial(
            title=form.title.data,
            slug=form.slug.data,
            summary=form.summary.data,
            content=form.content.data,
            difficulty=form.difficulty.data,
            estimated_minutes=form.estimated_minutes.data,
            is_published=form.is_published.data,
            category_id=form.category_id.data,
            user_id=current_user.id
        )
        db.session.add(tutorial)
        db.session.commit()
        if form.tags.data:
            tag_names = [t.strip() for t in form.tags.data.split(',') if t.strip()]
            for name in tag_names:
                slug = name.lower().replace(' ', '-')
                tag = Tag.query.filter_by(slug=slug).first()
                if not tag:
                    tag = Tag(name=name, slug=slug)
                    db.session.add(tag)
                tutorial.tags.append(tag)
            db.session.commit()
        flash('Tutorial created successfully.', 'success')
        return redirect(url_for('tutorials.view', slug=tutorial.slug))
    return render_template('tutorials/create.html', form=form)

@bp.route('/<slug>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(slug):
    tutorial = Tutorial.query.filter_by(slug=slug).first_or_404()
    form = TutorialForm(obj=tutorial)
    if request.method == 'GET':
        form.tags.data = ','.join([tag.name for tag in tutorial.tags])
    if form.validate_on_submit():
        tutorial.title = form.title.data
        tutorial.slug = form.slug.data
        tutorial.summary = form.summary.data
        tutorial.content = form.content.data
        tutorial.difficulty = form.difficulty.data
        tutorial.estimated_minutes = form.estimated_minutes.data
        tutorial.is_published = form.is_published.data
        tutorial.category_id = form.category_id.data

        tutorial.tags.clear()
        if form.tags.data:
            tag_names = [t.strip() for t in form.tags.data.split(',') if t.strip()]
            for name in tag_names:
                slug = name.lower().replace(' ', '-')
                tag = Tag.query.filter_by(slug=slug).first()
                if not tag:
                    tag = Tag(name=name, slug=slug)
                    db.session.add(tag)
                tutorial.tags.append(tag)
        db.session.commit()
        flash('Tutorial updated.', 'success')
        return redirect(url_for('tutorials.view', slug=tutorial.slug))
    return render_template('tutorials/edit.html', form=form, tutorial=tutorial)

@bp.route('/<slug>/delete', methods=['POST'])
@login_required
@admin_required
def delete(slug):
    tutorial = Tutorial.query.filter_by(slug=slug).first_or_404()
    db.session.delete(tutorial)
    db.session.commit()
    flash('Tutorial deleted.', 'success')
    return redirect(url_for('tutorials.list'))

@bp.route('/categories')
@login_required
@admin_required
def list_categories():
    categories = Category.query.order_by(Category.sort_order).all()
    return render_template('tutorials/categories.html', categories=categories)

@bp.route('/category/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_category():
    form = CategoryForm()
    if form.validate_on_submit():
        cat = Category(
            name=form.name.data,
            slug=form.slug.data,
            description=form.description.data,
            sort_order=form.sort_order.data
        )
        db.session.add(cat)
        db.session.commit()
        flash('Category created.', 'success')
        return redirect(url_for('tutorials.list_categories'))
    return render_template('tutorials/category_form.html', form=form)

@bp.route('/category/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(id):
    cat = Category.query.get_or_404(id)
    form = CategoryForm(obj=cat)
    if form.validate_on_submit():
        cat.name = form.name.data
        cat.slug = form.slug.data
        cat.description = form.description.data
        cat.sort_order = form.sort_order.data
        db.session.commit()
        flash('Category updated.', 'success')
        return redirect(url_for('tutorials.list_categories'))
    return render_template('tutorials/category_form.html', form=form, category=cat)

@bp.route('/category/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(id):
    cat = Category.query.get_or_404(id)
    db.session.delete(cat)
    db.session.commit()
    flash('Category deleted.', 'success')
    return redirect(url_for('tutorials.list_categories'))

@bp.route('/tags')
@login_required
@admin_required
def list_tags():
    tags = Tag.query.all()
    return render_template('tutorials/tags.html', tags=tags)

@bp.route('/tag/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_tag():
    form = TagForm()
    if form.validate_on_submit():
        tag = Tag(name=form.name.data, slug=form.slug.data)
        db.session.add(tag)
        db.session.commit()
        flash('Tag created.', 'success')
        return redirect(url_for('tutorials.list_tags'))
    return render_template('tutorials/tag_form.html', form=form)

@bp.route('/tag/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_tag(id):
    tag = Tag.query.get_or_404(id)
    form = TagForm(obj=tag)
    if form.validate_on_submit():
        tag.name = form.name.data
        tag.slug = form.slug.data
        db.session.commit()
        flash('Tag updated.', 'success')
        return redirect(url_for('tutorials.list_tags'))
    return render_template('tutorials/tag_form.html', form=form, tag=tag)

@bp.route('/tag/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_tag(id):
    tag = Tag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    flash('Tag deleted.', 'success')
    return redirect(url_for('tutorials.list_tags'))