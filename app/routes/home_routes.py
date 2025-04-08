from flask import Blueprint, render_template, request, redirect, url_for

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    # Simulación de datos de particiones
    partitions = [
        {'id': 1, 'name': 'Partición 1', 'size': 32, 'type': 'FAT32'},
        {'id': 2, 'name': 'Partición 2', 'size': 64, 'type': 'NTFS'}
    ]
    return render_template('index.html', partitions=partitions)

@home_bp.route('/activate/<int:partition_id>')
def activate_partition(partition_id):
    # Lógica para activar la partición
    print(f"Activando partición {partition_id}")
    return redirect(url_for('home.index'))

@home_bp.route('/deactivate/<int:partition_id>')
def deactivate_partition(partition_id):
    # Lógica para desactivar la partición
    print(f"Desactivando partición {partition_id}")
    return redirect(url_for('home.index'))

@home_bp.route('/edit/<int:partition_id>')
def edit_partition(partition_id):
    # Lógica para editar la partición
    print(f"Editando partición {partition_id}")
    return redirect(url_for('home.index'))

@home_bp.route('/delete/<int:partition_id>')
def delete_partition(partition_id):
    # Lógica para eliminar la partición
    print(f"Eliminando partición {partition_id}")
    return redirect(url_for('home.index'))

#Create refresh
@home_bp.route('/refresh_dashboard')
def refresh_dashboard():
    # Lógica para refrescar el dashboard
    print("Refrescando el dashboard")
    return redirect(url_for('home.index'))