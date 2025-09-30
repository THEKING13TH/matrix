"""
Sistema Profesional de Modelado 3D con Python
Autor: Sistema de Modelado Avanzado
Versión: 2.0

Este sistema permite crear planos arquitectónicos, modelos 3D complejos,
visualizaciones interactivas y exportar a múltiples formatos.

Dependencias necesarias:
pip install numpy matplotlib plotly trimesh open3d pyvista scipy
pip install cadquery-ocp python-opencascade-core
pip install ezdxf pyglet PyOpenGL
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import trimesh
import json
import os
from datetime import datetime
from typing import List, Tuple, Dict, Optional, Union
import warnings
warnings.filterwarnings('ignore')

class Vector3D:
    """Clase para manejar vectores 3D con operaciones matemáticas"""
    
    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        self.x, self.y, self.z = float(x), float(y), float(z)
    
    def __add__(self, other):
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def cross(self, other):
        """Producto cruzado"""
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def dot(self, other):
        """Producto punto"""
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def magnitude(self):
        """Magnitud del vector"""
        return np.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self):
        """Normalizar vector"""
        mag = self.magnitude()
        if mag == 0:
            return Vector3D(0, 0, 0)
        return Vector3D(self.x/mag, self.y/mag, self.z/mag)
    
    def to_array(self):
        """Convertir a numpy array"""
        return np.array([self.x, self.y, self.z])

class Transformations3D:
    """Clase para manejar transformaciones 3D (rotación, traslación, escala)"""
    
    @staticmethod
    def rotation_matrix_x(angle_rad: float) -> np.ndarray:
        """Matriz de rotación en X"""
        c, s = np.cos(angle_rad), np.sin(angle_rad)
        return np.array([
            [1, 0, 0, 0],
            [0, c, -s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1]
        ])
    
    @staticmethod
    def rotation_matrix_y(angle_rad: float) -> np.ndarray:
        """Matriz de rotación en Y"""
        c, s = np.cos(angle_rad), np.sin(angle_rad)
        return np.array([
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1]
        ])
    
    @staticmethod
    def rotation_matrix_z(angle_rad: float) -> np.ndarray:
        """Matriz de rotación en Z"""
        c, s = np.cos(angle_rad), np.sin(angle_rad)
        return np.array([
            [c, -s, 0, 0],
            [s, c, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
    
    @staticmethod
    def translation_matrix(dx: float, dy: float, dz: float) -> np.ndarray:
        """Matriz de traslación"""
        return np.array([
            [1, 0, 0, dx],
            [0, 1, 0, dy],
            [0, 0, 1, dz],
            [0, 0, 0, 1]
        ])
    
    @staticmethod
    def scale_matrix(sx: float, sy: float, sz: float) -> np.ndarray:
        """Matriz de escala"""
        return np.array([
            [sx, 0, 0, 0],
            [0, sy, 0, 0],
            [0, 0, sz, 0],
            [0, 0, 0, 1]
        ])

class Geometry3D:
    """Clase base para todas las geometrías 3D"""
    
    def __init__(self, name: str = "Geometry"):
        self.name = name
        self.vertices = []
        self.faces = []
        self.normals = []
        self.materials = {}
        self.transform_matrix = np.identity(4)
    
    def apply_transformation(self, matrix: np.ndarray):
        """Aplicar transformación a la geometría"""
        self.transform_matrix = matrix @ self.transform_matrix
    
    def get_bounding_box(self) -> Tuple[Vector3D, Vector3D]:
        """Obtener caja delimitadora"""
        if not self.vertices:
            return Vector3D(), Vector3D()
        
        min_point = Vector3D(float('inf'), float('inf'), float('inf'))
        max_point = Vector3D(float('-inf'), float('-inf'), float('-inf'))
        
        for vertex in self.vertices:
            min_point.x = min(min_point.x, vertex.x)
            min_point.y = min(min_point.y, vertex.y)
            min_point.z = min(min_point.z, vertex.z)
            max_point.x = max(max_point.x, vertex.x)
            max_point.y = max(max_point.y, vertex.y)
            max_point.z = max(max_point.z, vertex.z)
        
        return min_point, max_point

class ArchitecturalElements:
    """Clase para crear elementos arquitectónicos básicos"""
    
    @staticmethod
    def create_wall(length: float, height: float, thickness: float, 
                   position: Vector3D = Vector3D()) -> Geometry3D:
        """Crear una pared"""
        wall = Geometry3D("Wall")
        
        # Definir vértices de la pared
        vertices = [
            Vector3D(0, 0, 0),
            Vector3D(length, 0, 0),
            Vector3D(length, thickness, 0),
            Vector3D(0, thickness, 0),
            Vector3D(0, 0, height),
            Vector3D(length, 0, height),
            Vector3D(length, thickness, height),
            Vector3D(0, thickness, height)
        ]
        
        # Trasladar a la posición deseada
        wall.vertices = [v + position for v in vertices]
        
        # Definir caras (cada cara como lista de índices de vértices)
        wall.faces = [
            [0, 1, 2, 3],  # Base
            [4, 7, 6, 5],  # Techo
            [0, 4, 5, 1],  # Frente
            [2, 6, 7, 3],  # Atrás
            [0, 3, 7, 4],  # Izquierda
            [1, 5, 6, 2]   # Derecha
        ]
        
        wall.materials = {
            'color': '#8B4513',
            'texture': 'brick',
            'opacity': 1.0
        }
        
        return wall
    
    @staticmethod
    def create_door(width: float, height: float, thickness: float,
                   position: Vector3D = Vector3D()) -> Geometry3D:
        """Crear una puerta"""
        door = Geometry3D("Door")
        
        vertices = [
            Vector3D(0, 0, 0),
            Vector3D(width, 0, 0),
            Vector3D(width, thickness, 0),
            Vector3D(0, thickness, 0),
            Vector3D(0, 0, height),
            Vector3D(width, 0, height),
            Vector3D(width, thickness, height),
            Vector3D(0, thickness, height)
        ]
        
        door.vertices = [v + position for v in vertices]
        door.faces = [
            [0, 1, 2, 3], [4, 7, 6, 5], [0, 4, 5, 1],
            [2, 6, 7, 3], [0, 3, 7, 4], [1, 5, 6, 2]
        ]
        
        door.materials = {
            'color': '#8B4513',
            'texture': 'wood',
            'opacity': 0.9
        }
        
        return door
    
    @staticmethod
    def create_window(width: float, height: float, thickness: float,
                     position: Vector3D = Vector3D()) -> Geometry3D:
        """Crear una ventana"""
        window = Geometry3D("Window")
        
        # Marco de la ventana
        frame_thickness = 0.05
        
        vertices = []
        faces = []
        
        # Marco exterior
        outer_vertices = [
            Vector3D(0, 0, 0),
            Vector3D(width, 0, 0),
            Vector3D(width, thickness, 0),
            Vector3D(0, thickness, 0),
            Vector3D(0, 0, height),
            Vector3D(width, 0, height),
            Vector3D(width, thickness, height),
            Vector3D(0, thickness, height)
        ]
        
        # Marco interior (cristal)
        inner_vertices = [
            Vector3D(frame_thickness, frame_thickness, frame_thickness),
            Vector3D(width-frame_thickness, frame_thickness, frame_thickness),
            Vector3D(width-frame_thickness, thickness-frame_thickness, frame_thickness),
            Vector3D(frame_thickness, thickness-frame_thickness, frame_thickness),
            Vector3D(frame_thickness, frame_thickness, height-frame_thickness),
            Vector3D(width-frame_thickness, frame_thickness, height-frame_thickness),
            Vector3D(width-frame_thickness, thickness-frame_thickness, height-frame_thickness),
            Vector3D(frame_thickness, thickness-frame_thickness, height-frame_thickness)
        ]
        
        window.vertices = [v + position for v in outer_vertices + inner_vertices]
        
        # Caras del marco y cristal
        window.faces = [
            [0, 1, 2, 3], [4, 7, 6, 5],  # Marco exterior
            [8, 11, 10, 9], [12, 13, 14, 15]  # Cristal
        ]
        
        window.materials = {
            'color': '#87CEEB',
            'texture': 'glass',
            'opacity': 0.3
        }
        
        return window
    
    @staticmethod
    def create_roof(length: float, width: float, height: float,
                   position: Vector3D = Vector3D()) -> Geometry3D:
        """Crear un techo a dos aguas"""
        roof = Geometry3D("Roof")
        
        vertices = [
            Vector3D(0, 0, 0),  # Base esquina 1
            Vector3D(length, 0, 0),  # Base esquina 2
            Vector3D(length, width, 0),  # Base esquina 3
            Vector3D(0, width, 0),  # Base esquina 4
            Vector3D(length/2, 0, height),  # Pico frente
            Vector3D(length/2, width, height)  # Pico atrás
        ]
        
        roof.vertices = [v + position for v in vertices]
        
        roof.faces = [
            [0, 1, 2, 3],  # Base
            [0, 4, 5, 3],  # Lado izquierdo
            [1, 2, 5, 4],  # Lado derecho
            [0, 1, 4],     # Frente
            [2, 3, 5]      # Atrás
        ]
        
        roof.materials = {
            'color': '#8B0000',
            'texture': 'tile',
            'opacity': 1.0
        }
        
        return roof

class MechanicalElements:
    """Elementos para modelado mecánico e industrial"""
    
    @staticmethod
    def create_cylinder(radius: float, height: float, segments: int = 32,
                       position: Vector3D = Vector3D()) -> Geometry3D:
        """Crear un cilindro"""
        cylinder = Geometry3D("Cylinder")
        
        vertices = []
        faces = []
        
        # Vértices de la base inferior
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            vertices.append(Vector3D(x, y, 0))
        
        # Vértices de la base superior
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            vertices.append(Vector3D(x, y, height))
        
        # Centro de las bases
        vertices.append(Vector3D(0, 0, 0))  # Centro base inferior
        vertices.append(Vector3D(0, 0, height))  # Centro base superior
        
        cylinder.vertices = [v + position for v in vertices]
        
        # Caras laterales
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append([i, next_i, next_i + segments, i + segments])
        
        # Caras de las bases
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.append([2*segments, i, next_i])  # Base inferior
            faces.append([2*segments + 1, next_i + segments, i + segments])  # Base superior
        
        cylinder.faces = faces
        cylinder.materials = {
            'color': '#C0C0C0',
            'texture': 'metal',
            'opacity': 1.0
        }
        
        return cylinder
    
    @staticmethod
    def create_sphere(radius: float, u_segments: int = 16, v_segments: int = 16,
                     position: Vector3D = Vector3D()) -> Geometry3D:
        """Crear una esfera"""
        sphere = Geometry3D("Sphere")
        
        vertices = []
        faces = []
        
        # Generar vértices
        for i in range(u_segments + 1):
            u = i * np.pi / u_segments
            for j in range(v_segments):
                v = j * 2 * np.pi / v_segments
                
                x = radius * np.sin(u) * np.cos(v)
                y = radius * np.sin(u) * np.sin(v)
                z = radius * np.cos(u)
                
                vertices.append(Vector3D(x, y, z))
        
        sphere.vertices = [v + position for v in vertices]
        
        # Generar caras
        for i in range(u_segments):
            for j in range(v_segments):
                current = i * v_segments + j
                next_u = (i + 1) * v_segments + j
                next_v = i * v_segments + (j + 1) % v_segments
                next_both = (i + 1) * v_segments + (j + 1) % v_segments
                
                if i > 0:  # No crear caras en el polo norte
                    faces.append([current, next_v, next_both, next_u])
        
        sphere.faces = faces
        sphere.materials = {
            'color': '#FFD700',
            'texture': 'smooth',
            'opacity': 1.0
        }
        
        return sphere
    
    @staticmethod
    def create_gear(outer_radius: float, inner_radius: float, height: float,
                   teeth: int = 20, position: Vector3D = Vector3D()) -> Geometry3D:
        """Crear un engranaje"""
        gear = Geometry3D("Gear")
        
        vertices = []
        faces = []
        
        # Parámetros del diente
        tooth_height = (outer_radius - inner_radius) * 0.3
        
        # Generar puntos del perfil del engranaje
        profile_points = []
        
        for i in range(teeth * 2):  # 2 puntos por diente
            angle = 2 * np.pi * i / (teeth * 2)
            
            if i % 2 == 0:  # Base del diente
                r = inner_radius + tooth_height * 0.3
            else:  # Punta del diente
                r = outer_radius
            
            x = r * np.cos(angle)
            y = r * np.sin(angle)
            profile_points.append(Vector3D(x, y, 0))
        
        # Extruir el perfil
        for point in profile_points:
            vertices.append(point)  # Base inferior
            vertices.append(Vector3D(point.x, point.y, height))  # Base superior
        
        # Centro del engranaje
        vertices.append(Vector3D(0, 0, 0))
        vertices.append(Vector3D(0, 0, height))
        
        gear.vertices = [v + position for v in vertices]
        
        # Generar caras
        num_profile_points = len(profile_points)
        
        # Caras laterales
        for i in range(num_profile_points):
            next_i = (i + 1) % num_profile_points
            v1, v2 = i * 2, next_i * 2
            v3, v4 = i * 2 + 1, next_i * 2 + 1
            faces.append([v1, v2, v4, v3])
        
        # Caras superior e inferior
        center_bottom = len(vertices) - 2
        center_top = len(vertices) - 1
        
        for i in range(num_profile_points):
            next_i = (i + 1) % num_profile_points
            # Cara inferior
            faces.append([center_bottom, i * 2, next_i * 2])
            # Cara superior
            faces.append([center_top, next_i * 2 + 1, i * 2 + 1])
        
        gear.faces = faces
        gear.materials = {
            'color': '#4169E1',
            'texture': 'metal',
            'opacity': 1.0
        }
        
        return gear

class Professional3DModeler:
    """Clase principal del sistema de modelado 3D profesional"""
    
    def __init__(self):
        self.geometries: List[Geometry3D] = []
        self.lights = []
        self.cameras = []
        self.materials = {}
        self.scene_name = "Professional_3D_Model"
        self.metadata = {
            'created': datetime.now().isoformat(),
            'version': '2.0',
            'author': 'Professional 3D Modeler'
        }
    
    def add_geometry(self, geometry: Geometry3D):
        """Agregar geometría al modelo"""
        self.geometries.append(geometry)
    
    def remove_geometry(self, name: str):
        """Remover geometría por nombre"""
        self.geometries = [g for g in self.geometries if g.name != name]
    
    def add_light(self, light_type: str, position: Vector3D, 
                  intensity: float = 1.0, color: str = '#FFFFFF'):
        """Agregar fuente de luz"""
        light = {
            'type': light_type,
            'position': position,
            'intensity': intensity,
            'color': color
        }
        self.lights.append(light)
    
    def create_architectural_plan(self, plan_data: Dict) -> 'Professional3DModeler':
        """Crear un plano arquitectónico completo"""
        
        # Crear paredes
        for wall_data in plan_data.get('walls', []):
            wall = ArchitecturalElements.create_wall(
                wall_data['length'],
                wall_data['height'],
                wall_data['thickness'],
                Vector3D(wall_data['x'], wall_data['y'], wall_data['z'])
            )
            self.add_geometry(wall)
        
        # Crear puertas
        for door_data in plan_data.get('doors', []):
            door = ArchitecturalElements.create_door(
                door_data['width'],
                door_data['height'],
                door_data['thickness'],
                Vector3D(door_data['x'], door_data['y'], door_data['z'])
            )
            self.add_geometry(door)
        
        # Crear ventanas
        for window_data in plan_data.get('windows', []):
            window = ArchitecturalElements.create_window(
                window_data['width'],
                window_data['height'],
                window_data['thickness'],
                Vector3D(window_data['x'], window_data['y'], window_data['z'])
            )
            self.add_geometry(window)
        
        # Crear techo
        if 'roof' in plan_data:
            roof_data = plan_data['roof']
            roof = ArchitecturalElements.create_roof(
                roof_data['length'],
                roof_data['width'],
                roof_data['height'],
                Vector3D(roof_data['x'], roof_data['y'], roof_data['z'])
            )
            self.add_geometry(roof)
        
        return self
    
    def create_mechanical_assembly(self, assembly_data: Dict) -> 'Professional3DModeler':
        """Crear un ensamble mecánico"""
        
        # Crear cilindros
        for cylinder_data in assembly_data.get('cylinders', []):
            cylinder = MechanicalElements.create_cylinder(
                cylinder_data['radius'],
                cylinder_data['height'],
                cylinder_data.get('segments', 32),
                Vector3D(cylinder_data['x'], cylinder_data['y'], cylinder_data['z'])
            )
            self.add_geometry(cylinder)
        
        # Crear esferas
        for sphere_data in assembly_data.get('spheres', []):
            sphere = MechanicalElements.create_sphere(
                sphere_data['radius'],
                sphere_data.get('u_segments', 16),
                sphere_data.get('v_segments', 16),
                Vector3D(sphere_data['x'], sphere_data['y'], sphere_data['z'])
            )
            self.add_geometry(sphere)
        
        # Crear engranajes
        for gear_data in assembly_data.get('gears', []):
            gear = MechanicalElements.create_gear(
                gear_data['outer_radius'],
                gear_data['inner_radius'],
                gear_data['height'],
                gear_data.get('teeth', 20),
                Vector3D(gear_data['x'], gear_data['y'], gear_data['z'])
            )
            self.add_geometry(gear)
        
        return self
    
    def visualize_matplotlib(self, figsize: Tuple[int, int] = (12, 8),
                           show_wireframe: bool = False):
        """Visualizar usando Matplotlib"""
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'brown', 'pink']
        
        for i, geometry in enumerate(self.geometries):
            color = colors[i % len(colors)]
            
            # Extraer coordenadas
            x = [v.x for v in geometry.vertices]
            y = [v.y for v in geometry.vertices]
            z = [v.z for v in geometry.vertices]
            
            if show_wireframe:
                # Dibujar wireframe
                for face in geometry.faces:
                    if len(face) >= 3:
                        face_x = [geometry.vertices[idx].x for idx in face] + [geometry.vertices[face[0]].x]
                        face_y = [geometry.vertices[idx].y for idx in face] + [geometry.vertices[face[0]].y]
                        face_z = [geometry.vertices[idx].z for idx in face] + [geometry.vertices[face[0]].z]
                        ax.plot(face_x, face_y, face_z, color=color, alpha=0.6)
            else:
                # Scatter plot de vértices
                ax.scatter(x, y, z, c=color, s=20, alpha=0.8, label=geometry.name)
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.legend()
        ax.set_title(f'Modelo 3D: {self.scene_name}')
        
        plt.tight_layout()
        plt.show()
        
        return fig
    
    def visualize_plotly(self, show_axes: bool = True, 
                        interactive: bool = True) -> go.Figure:
        """Visualizar usando Plotly (interactivo)"""
        fig = go.Figure()
        
        colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'brown', 'pink']
        
        for i, geometry in enumerate(self.geometries):
            color = colors[i % len(colors)]
            
            # Extraer coordenadas
            x = [v.x for v in geometry.vertices]
            y = [v.y for v in geometry.vertices]
            z = [v.z for v in geometry.vertices]
            
            # Agregar vértices como scatter3d
            fig.add_trace(go.Scatter3d(
                x=x, y=y, z=z,
                mode='markers',
                marker=dict(size=5, color=color, opacity=0.8),
                name=geometry.name,
                hovertemplate=f'{geometry.name}<br>X: %{{x}}<br>Y: %{{y}}<br>Z: %{{z}}<extra></extra>'
            ))
            
            # Agregar caras como mesh3d si tiene suficientes datos
            if len(geometry.faces) > 0 and len(geometry.vertices) > 3:
                try:
                    # Convertir caras a formato de triángulos
                    triangles = []
                    for face in geometry.faces:
                        if len(face) >= 3:
                            # Triangular caras con más de 3 vértices
                            for j in range(1, len(face) - 1):
                                triangles.append([face[0], face[j], face[j+1]])
                    
                    if triangles:
                        i_indices = [t[0] for t in triangles]
                        j_indices = [t[1] for t in triangles]
                        k_indices = [t[2] for t in triangles]
                        
                        fig.add_trace(go.Mesh3d(
                            x=x, y=y, z=z,
                            i=i_indices, j=j_indices, k=k_indices,
                            color=color,
                            opacity=0.7,
                            name=f"{geometry.name}_mesh"
                        ))
                except Exception as e:
                    print(f"Error creando mesh para {geometry.name}: {e}")
        
        # Configurar layout
        fig.update_layout(
            title=f'Modelo 3D Profesional: {self.scene_name}',
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z',
                aspectmode='cube' if show_axes else 'data'
            ),
            width=1000,
            height=800
        )
        
        if interactive:
            fig.show()
        
        return fig
    
    def export_to_obj(self, filename: str):
        """Exportar modelo a formato OBJ"""
        with open(filename, 'w') as f:
            f.write(f"# Modelo 3D Profesional: {self.scene_name}\n")
            f.write(f"# Creado: {self.metadata['created']}\n\n")
            
            vertex_offset = 1  # OBJ usa índices basados en 1
            
            for geometry in self.geometries:
                f.write(f"# Geometría: {geometry.name}\n")
                f.write(f"o {geometry.name}\n")
                
                # Escribir vértices
                for vertex in geometry.vertices:
                    f.write(f"v {vertex.x} {vertex.y} {vertex.z}\n")
                
                # Escribir caras
                for face in geometry.faces:
                    if len(face) >= 3:
                        face_str = "f " + " ".join([str(idx + vertex_offset) for idx in face])
                        f.write(face_str + "\n")
                
                vertex_offset += len(geometry.vertices)
                f.write("\n")
        
        print(f"Modelo exportado a: {filename}")
    
    def export_to_json(self, filename: str):
        """Exportar modelo a formato JSON"""
        model_data = {
            'metadata': self.metadata,
            'scene_name': self.scene_name,
            'geometries': [],
            'lights': []
        }

        # Serializar luces (si hay Vector3D)
        for light in self.lights:
            light_serializable = light.copy()
            if isinstance(light_serializable.get('position'), Vector3D):
                light_serializable['position'] = [
                    light_serializable['position'].x,
                    light_serializable['position'].y,
                    light_serializable['position'].z
                ]
            model_data['lights'].append(light_serializable)

        for geometry in self.geometries:
            geo_data = {
                'name': geometry.name,
                'vertices': [[v.x, v.y, v.z] for v in geometry.vertices],
                'faces': geometry.faces,
                'materials': geometry.materials,
                'transform_matrix': geometry.transform_matrix.tolist()
            }
            model_data['geometries'].append(geo_data)

        with open(filename, 'w') as f:
            json.dump(model_data, f, indent=2)

        print(f"Modelo exportado a JSON: {filename}")
    
    def import_from_json(self, filename: str):
        """Importar modelo desde formato JSON"""
        with open(filename, 'r') as f:
            model_data = json.load(f)
        
        self.metadata = model_data.get('metadata', {})
        self.scene_name = model_data.get('scene_name', 'Imported_Model')
        self.lights = model_data.get('lights', [])
        
        for geo_data in model_data.get('geometries', []):
            geometry = Geometry3D(geo_data['name'])
            
            # Reconstruir vértices
            geometry.vertices = [Vector3D(v[0], v[1], v[2]) for v in geo_data['vertices']]
            geometry.faces = geo_data['faces']
            geometry.materials = geo_data.get('materials', {})
            geometry.transform_matrix = np.array(geo_data.get('transform_matrix', np.identity(4).tolist()))
            
            self.add_geometry(geometry)
        
        print(f"Modelo importado desde: {filename}")
    
    def generate_blueprint_2d(self, view: str = 'top', figsize: Tuple[int, int] = (12, 8)):
        """Generar plano 2D (vista superior, frontal o lateral)"""
        fig, ax = plt.subplots(figsize=figsize)
        
        colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'brown', 'pink']
        
        for i, geometry in enumerate(self.geometries):
            color = colors[i % len(colors)]
            
            if view == 'top':
                # Vista superior (proyección X-Y)
                x_coords = [v.x for v in geometry.vertices]
                y_coords = [v.y for v in geometry.vertices]
                ax.scatter(x_coords, y_coords, c=color, s=30, alpha=0.7, label=geometry.name)
                
                # Dibujar contornos de las caras
                for face in geometry.faces:
                    if len(face) >= 3:
                        face_x = [geometry.vertices[idx].x for idx in face] + [geometry.vertices[face[0]].x]
                        face_y = [geometry.vertices[idx].y for idx in face] + [geometry.vertices[face[0]].y]
                        ax.plot(face_x, face_y, color=color, alpha=0.5, linewidth=1)
                
                ax.set_xlabel('X')
                ax.set_ylabel('Y')
                ax.set_title('Vista Superior - Plano 2D')
            
            elif view == 'front':
                # Vista frontal (proyección X-Z)
                x_coords = [v.x for v in geometry.vertices]
                z_coords = [v.z for v in geometry.vertices]
                ax.scatter(x_coords, z_coords, c=color, s=30, alpha=0.7, label=geometry.name)
                
                for face in geometry.faces:
                    if len(face) >= 3:
                        face_x = [geometry.vertices[idx].x for idx in face] + [geometry.vertices[face[0]].x]
                        face_z = [geometry.vertices[idx].z for idx in face] + [geometry.vertices[face[0]].z]
                        ax.plot(face_x, face_z, color=color, alpha=0.5, linewidth=1)
                
                ax.set_xlabel('X')
                ax.set_ylabel('Z')
                ax.set_title('Vista Frontal - Plano 2D')
            
            elif view == 'side':
                # Vista lateral (proyección Y-Z)
                y_coords = [v.y for v in geometry.vertices]
                z_coords = [v.z for v in geometry.vertices]
                ax.scatter(y_coords, z_coords, c=color, s=30, alpha=0.7, label=geometry.name)
                
                for face in geometry.faces:
                    if len(face) >= 3:
                        face_y = [geometry.vertices[idx].y for idx in face] + [geometry.vertices[face[0]].y]
                        face_z = [geometry.vertices[idx].z for idx in face] + [geometry.vertices[face[0]].z]
                        ax.plot(face_y, face_z, color=color, alpha=0.5, linewidth=1)
                
                ax.set_xlabel('Y')
                ax.set_ylabel('Z')
                ax.set_title('Vista Lateral - Plano 2D')
        
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_aspect('equal')
        plt.tight_layout()
        plt.show()
        
        return fig
    
    def calculate_volume(self) -> Dict[str, float]:
        """Calcular volumen de cada geometría"""
        volumes = {}
        
        for geometry in self.geometries:
            volume = 0.0
            
            # Método simplificado para calcular volumen usando triangulación
            if len(geometry.vertices) >= 4 and len(geometry.faces) > 0:
                try:
                    # Crear malla con trimesh para cálculo preciso
                    vertices_array = np.array([[v.x, v.y, v.z] for v in geometry.vertices])
                    
                    # Triangular todas las caras
                    triangles = []
                    for face in geometry.faces:
                        if len(face) >= 3:
                            for j in range(1, len(face) - 1):
                                triangles.append([face[0], face[j], face[j+1]])
                    
                    if triangles:
                        mesh = trimesh.Trimesh(vertices=vertices_array, faces=triangles)
                        if mesh.is_volume:
                            volume = mesh.volume
                        else:
                            volume = 0.0
                
                except Exception as e:
                    print(f"Error calculando volumen para {geometry.name}: {e}")
                    volume = 0.0
            
            volumes[geometry.name] = volume
        
        return volumes
    
    def calculate_surface_area(self) -> Dict[str, float]:
        """Calcular área superficial de cada geometría"""
        areas = {}
        
        for geometry in self.geometries:
            total_area = 0.0
            
            for face in geometry.faces:
                if len(face) >= 3:
                    # Calcular área de cada cara
                    face_vertices = [geometry.vertices[idx] for idx in face]
                    
                    # Triangular la cara y sumar áreas
                    for j in range(1, len(face_vertices) - 1):
                        v1 = face_vertices[0]
                        v2 = face_vertices[j]
                        v3 = face_vertices[j + 1]
                        
                        # Producto cruzado para área del triángulo
                        edge1 = v2 - v1
                        edge2 = v3 - v1
                        cross = edge1.cross(edge2)
                        triangle_area = cross.magnitude() / 2.0
                        
                        total_area += triangle_area
            
            areas[geometry.name] = total_area
        
        return areas
    
    def apply_transformation_to_geometry(self, geometry_name: str, 
                                       transformation_matrix: np.ndarray):
        """Aplicar transformación específica a una geometría"""
        for geometry in self.geometries:
            if geometry.name == geometry_name:
                # Aplicar transformación a todos los vértices
                transformed_vertices = []
                for vertex in geometry.vertices:
                    # Convertir a coordenadas homogéneas
                    homogeneous = np.array([vertex.x, vertex.y, vertex.z, 1.0])
                    transformed = transformation_matrix @ homogeneous
                    transformed_vertices.append(Vector3D(transformed[0], transformed[1], transformed[2]))
                
                geometry.vertices = transformed_vertices
                geometry.apply_transformation(transformation_matrix)
                break
    
    def create_animation_frames(self, geometry_name: str, transformation_sequence: List[np.ndarray],
                              frame_count: int = 30) -> List['Professional3DModeler']:
        """Crear secuencia de frames para animación"""
        frames = []
        
        # Encontrar la geometría objetivo
        target_geometry = None
        for geometry in self.geometries:
            if geometry.name == geometry_name:
                target_geometry = geometry
                break
        
        if not target_geometry:
            print(f"Geometría '{geometry_name}' no encontrada")
            return frames
        
        # Guardar vértices originales
        original_vertices = [Vector3D(v.x, v.y, v.z) for v in target_geometry.vertices]
        
        # Generar frames interpolados
        for frame in range(frame_count):
            # Crear copia del modelo
            frame_model = Professional3DModeler()
            frame_model.scene_name = f"{self.scene_name}_frame_{frame}"
            
            # Copiar todas las geometrías
            for geometry in self.geometries:
                new_geometry = Geometry3D(geometry.name)
                new_geometry.vertices = [Vector3D(v.x, v.y, v.z) for v in geometry.vertices]
                new_geometry.faces = geometry.faces.copy()
                new_geometry.materials = geometry.materials.copy()
                new_geometry.transform_matrix = geometry.transform_matrix.copy()
                frame_model.add_geometry(new_geometry)
            
            # Aplicar interpolación de transformaciones
            t = frame / (frame_count - 1) if frame_count > 1 else 0
            
            # Interpolación simple entre transformaciones
            if len(transformation_sequence) >= 2:
                start_transform = transformation_sequence[0]
                end_transform = transformation_sequence[-1]
                
                # Interpolación lineal de matrices (simplificado)
                interpolated_transform = start_transform + t * (end_transform - start_transform)
                
                frame_model.apply_transformation_to_geometry(geometry_name, interpolated_transform)
            
            frames.append(frame_model)
        
        return frames
    
    def generate_cross_sections(self, plane_normal: Vector3D, plane_distances: List[float]) -> List[List[Vector3D]]:
        """Generar secciones transversales del modelo"""
        cross_sections = []
        
        plane_normal = plane_normal.normalize()
        
        for distance in plane_distances:
            section_points = []
            
            for geometry in self.geometries:
                for face in geometry.faces:
                    if len(face) >= 3:
                        # Verificar intersección de cada arista de la cara con el plano
                        for i in range(len(face)):
                            v1 = geometry.vertices[face[i]]
                            v2 = geometry.vertices[face[(i + 1) % len(face)]]
                            
                            # Calcular intersección línea-plano
                            edge_dir = v2 - v1
                            
                            # Evitar división por cero
                            denominator = edge_dir.dot(plane_normal)
                            if abs(denominator) > 1e-6:
                                # Punto de referencia en el plano
                                plane_point = Vector3D(0, 0, distance) if plane_normal.z != 0 else Vector3D(0, distance, 0) if plane_normal.y != 0 else Vector3D(distance, 0, 0)
                                
                                t = (plane_point - v1).dot(plane_normal) / denominator
                                
                                # Verificar si la intersección está en el segmento
                                if 0 <= t <= 1:
                                    intersection = v1 + edge_dir * t
                                    section_points.append(intersection)
            
            cross_sections.append(section_points)
        
        return cross_sections
    
    def optimize_mesh(self, geometry_name: str, target_vertices: int = 1000):
        """Optimizar malla reduciendo número de vértices"""
        for geometry in self.geometries:
            if geometry.name == geometry_name:
                if len(geometry.vertices) > target_vertices:
                    # Simplificación básica: mantener cada n-ésimo vértice
                    step = len(geometry.vertices) // target_vertices
                    optimized_vertices = geometry.vertices[::max(1, step)]
                    
                    # Reajustar índices de caras
                    vertex_mapping = {i * step: i for i in range(len(optimized_vertices))}
                    optimized_faces = []
                    
                    for face in geometry.faces:
                        new_face = []
                        for vertex_idx in face:
                            closest_idx = min(vertex_mapping.keys(), 
                                             key=lambda x: abs(x - vertex_idx))
                            if closest_idx in vertex_mapping:
                                new_face.append(vertex_mapping[closest_idx])
                        
                        if len(new_face) >= 3:
                            optimized_faces.append(new_face)
                    
                    geometry.vertices = optimized_vertices
                    geometry.faces = optimized_faces
                    
                    print(f"Malla optimizada: {geometry_name} - Vértices reducidos de {len(geometry.vertices)} a {len(optimized_vertices)}")
                break
    
    def generate_technical_drawing(self, scale: float = 1.0, 
                                 include_dimensions: bool = True,
                                 figsize: Tuple[int, int] = (16, 12)):
        """Generar dibujo técnico con múltiples vistas"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
        
        # Vista superior
        self._draw_2d_view(ax1, 'top', scale, include_dimensions)
        ax1.set_title('VISTA SUPERIOR', fontweight='bold')
        
        # Vista frontal
        self._draw_2d_view(ax2, 'front', scale, include_dimensions)
        ax2.set_title('VISTA FRONTAL', fontweight='bold')
        
        # Vista lateral
        self._draw_2d_view(ax3, 'side', scale, include_dimensions)
        ax3.set_title('VISTA LATERAL DERECHA', fontweight='bold')
        
        # Vista isométrica (simplificada)
        self._draw_isometric_view(ax4, scale)
        ax4.set_title('VISTA ISOMÉTRICA', fontweight='bold')
        
        # Información técnica
        fig.suptitle(f'DIBUJO TÉCNICO: {self.scene_name.upper()}', 
                    fontsize=16, fontweight='bold')
        
        plt.figtext(0.02, 0.02, f'Escala: 1:{1/scale:.0f}', fontsize=10)
        plt.figtext(0.02, 0.05, f'Fecha: {datetime.now().strftime("%Y-%m-%d")}', fontsize=10)
        plt.figtext(0.02, 0.08, 'Sistema de Modelado 3D Profesional', fontsize=10)
        
        plt.tight_layout()
        plt.show()
        
        return fig
    
    def _draw_2d_view(self, ax, view: str, scale: float, include_dimensions: bool):
        """Dibujar vista 2D específica"""
        colors = ['black', 'blue', 'red', 'green']
        
        for i, geometry in enumerate(self.geometries):
            color = colors[i % len(colors)]
            
            # Seleccionar coordenadas según la vista
            if view == 'top':
                coords = [(v.x * scale, v.y * scale) for v in geometry.vertices]
                ax.set_xlabel('X (mm)')
                ax.set_ylabel('Y (mm)')
            elif view == 'front':
                coords = [(v.x * scale, v.z * scale) for v in geometry.vertices]
                ax.set_xlabel('X (mm)')
                ax.set_ylabel('Z (mm)')
            elif view == 'side':
                coords = [(v.y * scale, v.z * scale) for v in geometry.vertices]
                ax.set_xlabel('Y (mm)')
                ax.set_ylabel('Z (mm)')
            
            # Dibujar contornos
            for face in geometry.faces:
                if len(face) >= 3:
                    face_coords = [coords[idx] for idx in face] + [coords[face[0]]]
                    x_coords, y_coords = zip(*face_coords)
                    ax.plot(x_coords, y_coords, color=color, linewidth=1.5, alpha=0.8)
        
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
        # Agregar dimensiones si se solicita
        if include_dimensions and self.geometries:
            self._add_dimensions(ax, view, scale)
    
    def _draw_isometric_view(self, ax, scale: float):
        """Dibujar vista isométrica simplificada"""
        # Matriz de transformación isométrica
        iso_matrix = np.array([
            [np.cos(np.pi/6), -np.cos(np.pi/6), 0],
            [np.sin(np.pi/6), np.sin(np.pi/6), 1]
        ])
        
        colors = ['black', 'blue', 'red', 'green']
        
        for i, geometry in enumerate(self.geometries):
            color = colors[i % len(colors)]
            
            # Transformar vértices a vista isométrica
            iso_coords = []
            for vertex in geometry.vertices:
                vertex_3d = np.array([vertex.x * scale, vertex.y * scale, vertex.z * scale])
                iso_point = iso_matrix @ vertex_3d
                iso_coords.append((iso_point[0], iso_point[1]))
            
            # Dibujar caras
            for face in geometry.faces:
                if len(face) >= 3:
                    face_coords = [iso_coords[idx] for idx in face] + [iso_coords[face[0]]]
                    x_coords, y_coords = zip(*face_coords)
                    ax.plot(x_coords, y_coords, color=color, linewidth=1.2, alpha=0.7)
        
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.2)
    
    def _add_dimensions(self, ax, view: str, scale: float):
        """Agregar cotas dimensionales al dibujo"""
        if not self.geometries:
            return
        
        # Obtener límites del modelo
        all_vertices = []
        for geometry in self.geometries:
            all_vertices.extend(geometry.vertices)
        
        if view == 'top':
            x_coords = [v.x * scale for v in all_vertices]
            y_coords = [v.y * scale for v in all_vertices]
        elif view == 'front':
            x_coords = [v.x * scale for v in all_vertices]
            y_coords = [v.z * scale for v in all_vertices]
        elif view == 'side':
            x_coords = [v.y * scale for v in all_vertices]
            y_coords = [v.z * scale for v in all_vertices]
        
        if x_coords and y_coords:
            x_range = max(x_coords) - min(x_coords)
            y_range = max(y_coords) - min(y_coords)
            
            # Agregar dimensión horizontal
            ax.annotate('', xy=(max(x_coords), min(y_coords) - y_range * 0.1),
                       xytext=(min(x_coords), min(y_coords) - y_range * 0.1),
                       arrowprops=dict(arrowstyle='<->', color='red', lw=1))
            ax.text((max(x_coords) + min(x_coords))/2, min(y_coords) - y_range * 0.15,
                   f'{x_range:.1f}', ha='center', va='top', color='red', fontsize=10)
            
            # Agregar dimensión vertical
            ax.annotate('', xy=(min(x_coords) - x_range * 0.1, max(y_coords)),
                       xytext=(min(x_coords) - x_range * 0.1, min(y_coords)),
                       arrowprops=dict(arrowstyle='<->', color='red', lw=1))
            ax.text(min(x_coords) - x_range * 0.15, (max(y_coords) + min(y_coords))/2,
                   f'{y_range:.1f}', ha='right', va='center', color='red', fontsize=10, rotation=90)


# Ejemplo de uso del sistema profesional
def example_architectural_house():
    """Ejemplo: Casa arquitectónica completa"""
    modeler = Professional3DModeler()
    modeler.scene_name = "Casa_Moderna"
    
    # Definir datos de la casa
    house_plan = {
        'walls': [
            {'length': 10, 'height': 3, 'thickness': 0.2, 'x': 0, 'y': 0, 'z': 0},
            {'length': 8, 'height': 3, 'thickness': 0.2, 'x': 0, 'y': 0, 'z': 0},
            {'length': 10, 'height': 3, 'thickness': 0.2, 'x': 0, 'y': 8, 'z': 0},
            {'length': 8, 'height': 3, 'thickness': 0.2, 'x': 10, 'y': 0, 'z': 0}
        ],
        'doors': [
            {'width': 1, 'height': 2.1, 'thickness': 0.05, 'x': 4.5, 'y': -0.05, 'z': 0}
        ],
        'windows': [
            {'width': 1.5, 'height': 1.2, 'thickness': 0.1, 'x': 2, 'y': -0.05, 'z': 1},
            {'width': 1.5, 'height': 1.2, 'thickness': 0.1, 'x': 7, 'y': -0.05, 'z': 1}
        ],
        'roof': {
            'length': 12, 'width': 10, 'height': 2, 'x': -1, 'y': -1, 'z': 3
        }
    }
    
    # Crear la casa
    modeler.create_architectural_plan(house_plan)
    
    # Agregar iluminación
    modeler.add_light('point', Vector3D(5, 4, 4), intensity=1.0)
    modeler.add_light('ambient', Vector3D(0, 0, 0), intensity=0.3)
    
    return modeler

def example_mechanical_assembly():
    """Ejemplo: Ensamble mecánico"""
    modeler = Professional3DModeler()
    modeler.scene_name = "Ensamble_Mecanico"
    
    # Definir datos del ensamble
    assembly_data = {
        'cylinders': [
            {'radius': 1, 'height': 3, 'segments': 32, 'x': 0, 'y': 0, 'z': 0},
            {'radius': 0.5, 'height': 4, 'segments': 16, 'x': 3, 'y': 0, 'z': 0}
        ],
        'spheres': [
            {'radius': 0.8, 'u_segments': 16, 'v_segments': 16, 'x': 0, 'y': 0, 'z': 3.5}
        ],
        'gears': [
            {'outer_radius': 2, 'inner_radius': 1.5, 'height': 0.3, 'teeth': 24, 'x': 6, 'y': 0, 'z': 0},
            {'outer_radius': 1.5, 'inner_radius': 1, 'height': 0.3, 'teeth': 18, 'x': 9, 'y': 0, 'z': 0}
        ]
    }
    
    # Crear el ensamble
    modeler.create_mechanical_assembly(assembly_data)
    
    return modeler

# Demostración del sistema
if __name__ == "__main__":
    print("=== SISTEMA PROFESIONAL DE MODELADO 3D ===")
    print("Creando ejemplos...")
    
    # Ejemplo 1: Casa arquitectónica
    print("\n1. Creando casa arquitectónica...")
    house = example_architectural_house()
    
    # Calcular propiedades
    volumes = house.calculate_volume()
    areas = house.calculate_surface_area()
    
    print("Volúmenes calculados:")
    for name, vol in volumes.items():
        print(f"  {name}: {vol:.3f} m³")
    
    print("Áreas superficiales:")
    for name, area in areas.items():
        print(f"  {name}: {area:.3f} m²")
    
    # Exportar
    house.export_to_obj("casa_moderna.obj")
    house.export_to_json("casa_moderna.json")
    
    # Visualizaciones
    print("Generando visualizaciones...")
    house.visualize_matplotlib(figsize=(15, 10), show_wireframe=True)
    house.visualize_plotly(interactive=True)
    house.generate_blueprint_2d('top')
    house.generate_technical_drawing(scale=100, include_dimensions=True)
    
    # Ejemplo 2: Ensamble mecánico
    print("\n2. Creando ensamble mecánico...")
    assembly = example_mechanical_assembly()
    
    assembly.export_to_obj("ensamble_mecanico.obj")
    assembly.visualize_matplotlib(show_wireframe=True)
    assembly.generate_technical_drawing(scale=50)
    
    print("\n¡Sistema de modelado 3D profesional completado!")
    print("Funcionalidades disponibles:")
    print("- Modelado arquitectónico completo")
    print("- Elementos mecánicos avanzados")
    print("- Visualización interactiva")
    print("- Exportación a múltiples formatos")
    print("- Dibujos técnicos profesionales")
    print("- Cálculos de volumen y área")
    print("- Optimización de mallas")
    print("- Sistema de animación")
    print("- Secciones transversales")
    print("- Transformaciones 3D completas")