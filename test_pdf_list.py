from controller import moderator_controller
import os

# Crear carpeta tesis si no existe y poner un archivo dummy si está vacía
if not os.path.exists('tesis'):
    os.makedirs('tesis')

if not os.listdir('tesis'):
    with open('tesis/test.pdf', 'w') as f:
        f.write('dummy pdf content')

print("Probando get_all_pdfs_info()...")
try:
    result = moderator_controller.get_all_pdfs_info()
    print("Resultado:", result)
except Exception as e:
    print("Error:", e)
