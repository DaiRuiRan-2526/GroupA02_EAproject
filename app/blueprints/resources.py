from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.decorators import admin_required
from app.extensions import db
from app.models.resource import Resource, ResourceCategory, Download
from app.forms import ResourceForm, ResourceCategoryForm

bp = Blueprint('resources', __name__, url_prefix='/resources')

@bp.route('/')
def list():
    category_slug = request.args.get('category')
    if category_slug:
        category = ResourceCategory.query.filter_by(slug=category_slug).first_or_404()
        resources = Resource.query.filter_by(category_id=category.id).all()
    else:
        resources = Resource.query.all()
    categories = ResourceCategory.query.all()
    return render_template('resources_list.html.j2', resources=resources, categories=categories)

@bp.route('/<int:id>')
def view(id):
    resource = Resource.query.get_or_404(id)
    return render_template('resources_view.html.j2', resource=resource)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = ResourceForm()
    if form.validate_on_submit():
        resource = Resource(
            title=form.title.data,
            description=form.description.data,
            type=form.type.data,
            file_path=form.file_path.data,
            external_link=form.external_link.data,
            file_size=form.file_size.data,
            is_featured=form.is_featured.data,
            category_id=form.category_id.data,
            user_id=current_user.id
        )
        db.session.add(resource)
        db.session.commit()
        flash('Resource created.', 'success')
        return redirect(url_for('resources.view', id=resource.id))
    return render_template('resources_form.html.j2', form=form)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    resource = Resource.query.get_or_404(id)
    form = ResourceForm(obj=resource)
    if form.validate_on_submit():
        resource.title = form.title.data
        resource.description = form.description.data
        resource.type = form.type.data
        resource.file_path = form.file_path.data
        resource.external_link = form.external_link.data
        resource.file_size = form.file_size.data
        resource.is_featured = form.is_featured.data
        resource.category_id = form.category_id.data
        db.session.commit()
        flash('Resource updated.', 'success')
        return redirect(url_for('resources.view', id=resource.id))
    return render_template('resources_form.html.j2', form=form, resource=resource)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    resource = Resource.query.get_or_404(id)
    db.session.delete(resource)
    db.session.commit()
    flash('Resource deleted.', 'success')
    return redirect(url_for('resources.list'))


@bp.route('/categories')
@login_required
@admin_required
def list_categories():
    categories = ResourceCategory.query.all()
    return render_template('resources_categories.html.j2', categories=categories)

@bp.route('/category/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_category():
    form = ResourceCategoryForm()
    if form.validate_on_submit():
        cat = ResourceCategory(
            name=form.name.data,
            slug=form.slug.data,
            icon=form.icon.data,
            description=form.description.data
        )
        db.session.add(cat)
        db.session.commit()
        flash('Category created.', 'success')
        return redirect(url_for('resources.list_categories'))
    return render_template('resources_category_form.html.j2', form=form)

@bp.route('/category/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(id):
    cat = ResourceCategory.query.get_or_404(id)
    form = ResourceCategoryForm(obj=cat)
    if form.validate_on_submit():
        cat.name = form.name.data
        cat.slug = form.slug.data
        cat.icon = form.icon.data
        cat.description = form.description.data
        db.session.commit()
        flash('Category updated.', 'success')
        return redirect(url_for('resources.list_categories'))
    return render_template('resources_category_form.html.j2', form=form, category=cat)

@bp.route('/category/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(id):
    cat = ResourceCategory.query.get_or_404(id)
    db.session.delete(cat)
    db.session.commit()
    flash('Category deleted.', 'success')
    return redirect(url_for('resources.list_categories'))


@bp.route('/<int:id>/download')
@login_required
def download(id):
    resource = Resource.query.get_or_404(id)

    download = Download(
        user_id=current_user.id,
        resource_id=resource.id,
        ip_address=request.remote_addr
    )
    resource.download_count += 1
    db.session.add(download)
    db.session.commit()
    if resource.file_path:

        return redirect(resource.file_path)
    elif resource.external_link:
        return redirect(resource.external_link)
    else:
        flash('No download link available.', 'warning')
        return redirect(url_for('resources.view', id=resource.id))

@bp.route('/my-downloads')
@login_required
def my_downloads():
    downloads = Download.query.filter_by(user_id=current_user.id).order_by(Download.downloaded_at.desc()).all()
    return render_template('resources/my_downloads.html', downloads=downloads)