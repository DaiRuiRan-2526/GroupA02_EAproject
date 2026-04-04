from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.decorators import admin_required
from app.extensions import db
from app.models.user import User, Role
from app.models.tutorial import Category as TutorialCategory
from app.models.resource import ResourceCategory
from app.forms import UserForm, RoleForm, CategoryForm, ResourceCategoryForm

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
@login_required
@admin_required
def dashboard():
    user_count = User.query.count()
    tutorial_count = 0  # 可以动态导入 Tutorial 模型
    resource_count = 0
    return render_template('admin/dashboard.html', 
                           user_count=user_count,
                           tutorial_count=tutorial_count,
                           resource_count=resource_count)


@bp.route('/users')
@login_required
@admin_required
def list_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@bp.route('/user/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        if form.password.data:
            user.set_password(form.password.data)
        else:

            flash('Password is required for new user.', 'danger')
            return render_template('admin/user_form.html', form=form)
        user.role = form.role.data  

        db.session.add(user)
        db.session.commit()
        flash('User created.', 'success')
        return redirect(url_for('admin.list_users'))
    return render_template('admin/user_form.html', form=form)

@bp.route('/user/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:
            user.set_password(form.password.data)

        flash('User updated.', 'success')
        db.session.commit()
        return redirect(url_for('admin.list_users'))
    return render_template('admin/user_form.html', form=form, user=user)

@bp.route('/user/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('You cannot delete yourself.', 'danger')
        return redirect(url_for('admin.list_users'))
    db.session.delete(user)
    db.session.commit()
    flash('User deleted.', 'success')
    return redirect(url_for('admin.list_users'))


@bp.route('/roles')
@login_required
@admin_required
def list_roles():
    roles = Role.query.all()
    return render_template('admin/roles.html', roles=roles)

@bp.route('/role/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_role():
    form = RoleForm()
    if form.validate_on_submit():
        role = Role(name=form.name.data, description=form.description.data)
        db.session.add(role)
        db.session.commit()
        flash('Role created.', 'success')
        return redirect(url_for('admin.list_roles'))
    return render_template('admin/role_form.html', form=form)

@bp.route('/role/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_role(id):
    role = Role.query.get_or_404(id)
    form = RoleForm(obj=role)
    if form.validate_on_submit():
        role.name = form.name.data
        role.description = form.description.data
        db.session.commit()
        flash('Role updated.', 'success')
        return redirect(url_for('admin.list_roles'))
    return render_template('admin/role_form.html', form=form, role=role)

@bp.route('/role/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_role(id):
    role = Role.query.get_or_404(id)
    if role.users.count() > 0:
        flash('Cannot delete role that has users.', 'danger')
        return redirect(url_for('admin.list_roles'))
    db.session.delete(role)
    db.session.commit()
    flash('Role deleted.', 'success')
    return redirect(url_for('admin.list_roles'))


@bp.route('/tutorial-categories')
@login_required
@admin_required
def list_tutorial_categories():
    categories = TutorialCategory.query.order_by(TutorialCategory.sort_order).all()
    return render_template('admin/tutorial_categories.html', categories=categories)

@bp.route('/tutorial-category/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_tutorial_category():
    form = CategoryForm()
    if form.validate_on_submit():
        cat = TutorialCategory(
            name=form.name.data,
            slug=form.slug.data,
            description=form.description.data,
            sort_order=form.sort_order.data
        )
        db.session.add(cat)
        db.session.commit()
        flash('Category created.', 'success')
        return redirect(url_for('admin.list_tutorial_categories'))
    return render_template('admin/category_form.html', form=form)

@bp.route('/tutorial-category/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_tutorial_category(id):
    cat = TutorialCategory.query.get_or_404(id)
    form = CategoryForm(obj=cat)
    if form.validate_on_submit():
        cat.name = form.name.data
        cat.slug = form.slug.data
        cat.description = form.description.data
        cat.sort_order = form.sort_order.data
        db.session.commit()
        flash('Category updated.', 'success')
        return redirect(url_for('admin.list_tutorial_categories'))
    return render_template('admin/category_form.html', form=form, category=cat)

@bp.route('/tutorial-category/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_tutorial_category(id):
    cat = TutorialCategory.query.get_or_404(id)
    if cat.tutorials.count() > 0:
        flash('Cannot delete category that has tutorials.', 'danger')
        return redirect(url_for('admin.list_tutorial_categories'))
    db.session.delete(cat)
    db.session.commit()
    flash('Category deleted.', 'success')
    return redirect(url_for('admin.list_tutorial_categories'))


@bp.route('/resource-categories')
@login_required
@admin_required
def list_resource_categories():
    categories = ResourceCategory.query.all()
    return render_template('admin/resource_categories.html', categories=categories)

@bp.route('/resource-category/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_resource_category():
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
        return redirect(url_for('admin.list_resource_categories'))
    return render_template('admin/resource_category_form.html', form=form)

@bp.route('/resource-category/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_resource_category(id):
    cat = ResourceCategory.query.get_or_404(id)
    form = ResourceCategoryForm(obj=cat)
    if form.validate_on_submit():
        cat.name = form.name.data
        cat.slug = form.slug.data
        cat.icon = form.icon.data
        cat.description = form.description.data
        db.session.commit()
        flash('Category updated.', 'success')
        return redirect(url_for('admin.list_resource_categories'))
    return render_template('admin/resource_category_form.html', form=form, category=cat)

@bp.route('/resource-category/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_resource_category(id):
    cat = ResourceCategory.query.get_or_404(id)
    if cat.resources.count() > 0:
        flash('Cannot delete category that has resources.', 'danger')
        return redirect(url_for('admin.list_resource_categories'))
    db.session.delete(cat)
    db.session.commit()
    flash('Category deleted.', 'success')
    return redirect(url_for('admin.list_resource_categories'))
