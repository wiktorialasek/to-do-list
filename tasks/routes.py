from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from forms import TaskForm
from models import Task
from app import db

tasks = Blueprint('tasks', __name__)

@tasks.route('/tasks', methods=['GET'])
@login_required
def task_list():
    user_tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('task_list.html', tasks=user_tasks)

@tasks.route('/tasks/new', methods=['GET', 'POST'])
@login_required
def new_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            deadline=form.deadline.data,
            user_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('tasks.task_list'))
    return render_template('task_form.html', form=form)

@tasks.route('/tasks/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to edit this task.')
        return redirect(url_for('tasks.task_list'))
    form = TaskForm()
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.deadline = form.deadline.data
        db.session.commit()
        return redirect(url_for('tasks.task_list'))
    elif request.method == 'GET':
        form.title.data = task.title
        form.description.data = task.description
        form.deadline.data = task.deadline
    return render_template('task_form.html', form=form)

@tasks.route('/tasks/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to delete this task.')
        return redirect(url_for('tasks.task_list'))
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('tasks.task_list'))
