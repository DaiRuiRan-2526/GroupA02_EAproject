# app/blueprints/community.py
from flask import render_template, redirect, url_for, flash, request, abort, Blueprint
from flask_login import login_required, current_user
from app.extensions import db
from app.models.community import DiscussionPost, PostComment, PostLike
from app.forms import PostForm, CommentForm
from datetime import datetime

bp = Blueprint('community', __name__, url_prefix='/community')

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    posts = DiscussionPost.query.order_by(DiscussionPost.is_pinned.desc(), DiscussionPost.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('community.html.j2', posts=posts)


@bp.route('/post/<int:id>')
def view_post(id):
    post = DiscussionPost.query.get_or_404(id)
    form = CommentForm()
    
    post.view_count += 1
    db.session.commit()
    comments = post.comments.order_by(PostComment.created_at.asc()).all()
    return render_template('community_post.html.j2', post=post, comments=comments, form=form)


@bp.route('/post/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = DiscussionPost(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            user_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        flash('Post created', 'success')
        return redirect(url_for('community.view_post', id=post.id))
    return render_template('community_post_form.html.j2', form=form)


@bp.route('/post/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = DiscussionPost.query.get_or_404(id)
    if post.user_id != current_user.id and not current_user.is_admin():
        abort(403)
    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.category = form.category.data
        post.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Post updated', 'success')
        return redirect(url_for('community.view_post', id=post.id))
    return render_template('community_post_form.html.j2', form=form, post=post)


@bp.route('/post/<int:id>/delete', methods=['POST'])
@login_required
def delete_post(id):
    post = DiscussionPost.query.get_or_404(id)
    if post.user_id != current_user.id and not current_user.is_admin():
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted', 'success')
    return redirect(url_for('community.index'))


@bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def create_comment(post_id):
    post = DiscussionPost.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = PostComment(
            content=form.content.data,
            post_id=post.id,
            user_id=current_user.id
        )
        db.session.add(comment)
        post.reply_count = PostComment.query.filter_by(post_id=post.id).count()
        db.session.commit()
        flash('Comment posted', 'success')
    else:
        flash('Comment content cannot be empty.', 'danger')
    return redirect(url_for('community.view_post', id=post.id))

@bp.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_comment(comment_id):
    comment = PostComment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id and not current_user.is_admin():
        abort(403)
    form = CommentForm()
    if form.validate_on_submit():
        comment.content = form.content.data
        db.session.commit()
        flash('Comment updated', 'success')
        return redirect(url_for('community.view_post', id=comment.post_id))
    form.content.data = comment.content
    return render_template('community_comment_edit.html.j2', form=form, comment=comment)

@bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = PostComment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id and not current_user.is_admin():
        abort(403)
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    
    post = DiscussionPost.query.get(post_id)
    post.reply_count = PostComment.query.filter_by(post_id=post_id).count()
    db.session.commit()
    flash('Comment deleted', 'success')
    return redirect(url_for('community.view_post', id=post_id))


@bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = DiscussionPost.query.get_or_404(post_id)
    existing = PostLike.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if existing:
        
        db.session.delete(existing)
        post.like_count -= 1
        db.session.commit()
        flash('Likes cancelled', 'info')
    else:
        like = PostLike(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        post.like_count += 1
        db.session.commit()
        flash('Like successfully', 'success')
    return redirect(url_for('community.view_post', id=post.id))