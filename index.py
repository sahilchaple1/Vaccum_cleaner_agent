"""
Vacuum Cleaner AI Simulation - Professional 3D GUI
Fixed manual input parser and enhanced 3D visualization
"""

import sys
import random
import time
import copy
from enum import Enum
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
import OpenGL.GL as gl
import OpenGL.GLU as glu
import numpy as np

# ============================================================================
# BACKEND LOGIC CLASSES
# ============================================================================

class CellState(Enum):
    CLEAN = "C"
    DIRTY = "D"
    
    def __str__(self):
        return self.value
    
    @property
    def color(self):
        return QColor(0, 255, 0) if self == CellState.CLEAN else QColor(255, 0, 0)
    
    @property
    def glow_color(self):
        return (0.0, 1.0, 0.0, 0.8) if self == CellState.CLEAN else (1.0, 0.0, 0.0, 0.8)

class GridEnvironment:
    """Represents the grid environment for the vacuum cleaner"""
    
    def __init__(self, size, mode=1, manual_data=None):
        self.size = size
        self.grid = []
        
        if mode == 1:
            self.random_environment()
        else:
            if manual_data:
                self.grid = manual_data
            else:
                self.manual_environment()
    
    def random_environment(self):
        """Generate random environment"""
        for i in range(self.size):
            row = []
            for j in range(self.size):
                row.append(random.choice([CellState.DIRTY, CellState.CLEAN]))
            self.grid.append(row)
    
    def manual_environment(self):
        """Interactive manual environment creation"""
        print("Manual environment creation - using random for demo")
        self.random_environment()
    
    def clean(self, x, y):
        """Clean a cell if it's dirty"""
        if self.grid[x][y] == CellState.DIRTY:
            self.grid[x][y] = CellState.CLEAN
            return True
        return False
    
    def get_state(self, x, y):
        """Get the state of a specific cell"""
        return self.grid[x][y]

class ReflexAgent:
    """Reflex agent that visits every cell"""
    
    def __init__(self, env):
        self.env = copy.deepcopy(env)
        self.moves = 0
        self.cleaned = 0
        self.current_pos = (0, 0)
        self.path = []
        self._generate_path()
    
    def _generate_path(self):
        """Generate the path the agent will take"""
        for i in range(self.env.size):
            for j in range(self.env.size):
                self.path.append((i, j))
    
    def step(self):
        """Execute one step of the agent's movement"""
        if self.moves < len(self.path):
            self.current_pos = self.path[self.moves]
            x, y = self.current_pos
            
            if self.env.clean(x, y):
                self.cleaned += 1
            
            self.moves += 1
            return True
        return False
    
    def reset(self):
        """Reset the agent"""
        self.moves = 0
        self.cleaned = 0
        self.current_pos = (0, 0)

class ModelBasedAgent:
    """Model-based agent that only moves to dirty cells"""
    
    def __init__(self, env):
        self.env = copy.deepcopy(env)
        self.moves = 0
        self.cleaned = 0
        self.current_pos = (0, 0)
        self.model = [[None] * env.size for _ in range(env.size)]
        self.path = []
        self._build_model()
        self._generate_path()
    
    def _build_model(self):
        """Build internal model of the environment"""
        for i in range(self.env.size):
            for j in range(self.env.size):
                self.model[i][j] = self.env.grid[i][j]
    
    def _generate_path(self):
        """Generate path to only dirty cells"""
        for i in range(self.env.size):
            for j in range(self.env.size):
                if self.model[i][j] == CellState.DIRTY:
                    self.path.append((i, j))
    
    def step(self):
        """Execute one step of the agent's movement"""
        if self.moves < len(self.path):
            self.current_pos = self.path[self.moves]
            x, y = self.current_pos
            
            if self.env.clean(x, y):
                self.cleaned += 1
            
            self.moves += 1
            return True
        return False
    
    def reset(self):
        """Reset the agent"""
        self.moves = 0
        self.cleaned = 0
        self.current_pos = (0, 0)

# ============================================================================
# MANUAL INPUT DIALOG WITH FIXED PARSER
# ============================================================================

class ManualEnvironmentDialog(QDialog):
    """Dialog for manual environment input with proper parsing"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manual Environment Editor")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        
        # Result data
        self.grid_data = None
        self.grid_size = 3
        
        # Setup UI
        self.setup_ui()
        
        # Set example text
        self.set_example_text()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("MANUAL ENVIRONMENT EDITOR")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #00ffff;
            padding: 10px;
        """)
        layout.addWidget(title)
        
        # Instructions with examples
        instructions = QLabel(
            "Enter your grid below.\n\n"
            "✅ CORRECT formats:\n"
            "D C D\n"
            "C D C\n"
            "D C D\n\n"
            "or\n\n"
            "D,C,D\n"
            "C,D,C\n"
            "D,C,D\n\n"
            "❌ INCORRECT (what you had):\n"
            "D CD  (missing space between C and D)\n"
            "C DC  (missing space between D and C)"
        )
        instructions.setAlignment(Qt.AlignmentFlag.AlignLeft)
        instructions.setStyleSheet("""
            color: #a0a0ff;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 5px;
            padding: 10px;
            font-family: monospace;
        """)
        layout.addWidget(instructions)
        
        # Grid size input
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Grid Size:"))
        self.size_input = QLineEdit()
        self.size_input.setPlaceholderText("3")
        self.size_input.setText("3")
        self.size_input.setMaximumWidth(100)
        size_layout.addWidget(self.size_input)
        size_layout.addStretch()
        layout.addLayout(size_layout)
        
        # Text input area
        self.text_input = QTextEdit()
        self.text_input.setFont(QFont("Courier New", 14))
        self.text_input.setMaximumHeight(200)
        layout.addWidget(self.text_input)
        
        # Quick template buttons
        template_layout = QHBoxLayout()
        
        templates = [
            ("Your Intended Grid", self.set_your_grid),
            ("All Dirty", self.set_all_dirty),
            ("Checkerboard", self.set_checkerboard),
        ]
        
        for name, func in templates:
            btn = QPushButton(name)
            btn.clicked.connect(func)
            template_layout.addWidget(btn)
        
        layout.addLayout(template_layout)
        
        # Preview area
        preview_label = QLabel("Preview:")
        preview_label.setStyleSheet("color: #00ffff; font-weight: bold;")
        layout.addWidget(preview_label)
        
        self.preview_text = QLabel()
        self.preview_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_text.setStyleSheet("""
            background: rgba(0, 0, 0, 0.5);
            border: 2px solid #4a4a8a;
            border-radius: 5px;
            padding: 15px;
            font-family: monospace;
            font-size: 18px;
            color: white;
        """)
        layout.addWidget(self.preview_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("Preview")
        self.preview_btn.clicked.connect(self.update_preview)
        button_layout.addWidget(self.preview_btn)
        
        self.validate_btn = QPushButton("Validate")
        self.validate_btn.clicked.connect(self.validate_input)
        button_layout.addWidget(self.validate_btn)
        
        button_layout.addStretch()
        
        self.ok_btn = QPushButton("Create Environment")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setEnabled(False)
        button_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
    def set_example_text(self):
        """Set example text in the input area"""
        example = """D C D
C D C
D C D"""
        self.text_input.setText(example)
        self.update_preview()
        
    def set_your_grid(self):
        """Set the grid from your image"""
        grid = """D C D
C D C
D C D"""
        self.text_input.setText(grid)
        self.size_input.setText("3")
        self.update_preview()
        
    def set_all_dirty(self):
        """Set all cells to dirty"""
        size = int(self.size_input.text() or "3")
        grid = "\n".join(["D " * size for _ in range(size)])
        self.text_input.setText(grid)
        self.update_preview()
        
    def set_checkerboard(self):
        """Set checkerboard pattern"""
        size = int(self.size_input.text() or "3")
        rows = []
        for i in range(size):
            row = []
            for j in range(size):
                row.append("D" if (i + j) % 2 == 0 else "C")
            rows.append(" ".join(row))
        self.text_input.setText("\n".join(rows))
        self.update_preview()
        
    def update_preview(self):
        """Update the preview area"""
        text = self.text_input.toPlainText().strip()
        if text:
            # Format nicely for preview
            lines = text.split('\n')
            preview = ""
            for line in lines[:5]:  # Show first 5 lines
                # Clean up the line
                cells = self._parse_line(line)
                preview += "  ".join(cells) + "\n"
            self.preview_text.setText(preview)
            
    def _parse_line(self, line):
        """Parse a single line of input"""
        # Remove extra spaces and split
        line = line.strip()
        
        # Case 1: Space separated (D C D)
        if ' ' in line:
            cells = [c for c in line.split(' ') if c]
        # Case 2: Comma separated (D,C,D)
        elif ',' in line:
            cells = [c.strip() for c in line.split(',') if c.strip()]
        # Case 3: No separators (DCD)
        else:
            cells = list(line)
            
        # Validate and uppercase
        return [c.upper() for c in cells if c.upper() in ['D', 'C']]
        
    def validate_input(self):
        """Validate the manual input"""
        try:
            text = self.text_input.toPlainText().strip()
            if not text:
                QMessageBox.warning(self, "Error", "Please enter grid data")
                return
                
            # Parse each line
            lines = text.split('\n')
            grid = []
            expected_size = int(self.size_input.text() or "3")
            
            for i, line in enumerate(lines):
                if not line.strip():
                    continue
                    
                # Parse the line
                cells = self._parse_line(line)
                
                # Check if we have the right number of cells
                if len(cells) != expected_size:
                    QMessageBox.warning(
                        self, 
                        "Error", 
                        f"Row {i+1} has {len(cells)} cells, but should have {expected_size}.\n"
                        f"Make sure each cell is separated by a space: D C D"
                    )
                    return
                    
                grid.append(cells)
            
            # Check if we have the right number of rows
            if len(grid) != expected_size:
                QMessageBox.warning(
                    self, 
                    "Error", 
                    f"Grid has {len(grid)} rows, but should have {expected_size}."
                )
                return
            
            # Success!
            self.grid_data = []
            for row in grid:
                grid_row = []
                for cell in row:
                    grid_row.append(CellState.DIRTY if cell == 'D' else CellState.CLEAN)
                self.grid_data.append(grid_row)
            
            self.ok_btn.setEnabled(True)
            QMessageBox.information(
                self, 
                "Success", 
                f"✅ Valid {expected_size}x{expected_size} grid created!\n\n"
                f"Preview:\n" + "\n".join([" ".join(row) for row in grid])
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Validation failed: {str(e)}")

# ============================================================================
# 3D OPENGL WIDGET (Enhanced)
# ============================================================================

class GLWidget(QOpenGLWidget):
    """Enhanced OpenGL widget with better 3D visualization"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_size = 3
        self.cells = []
        self.robot_pos = (0, 0)
        self.robot_anim_offset = 0.0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(16)
        self.rotation_x = 30
        self.rotation_y = 45
        self.last_mouse_pos = None
        
        # Colors for cells
        self.dirty_color = (1.0, 0.2, 0.2, 0.9)
        self.clean_color = (0.2, 1.0, 0.2, 0.9)
        
    def initializeGL(self):
        """Initialize OpenGL settings"""
        gl.glClearColor(0.05, 0.05, 0.1, 1.0)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_LIGHTING)
        gl.glEnable(gl.GL_LIGHT0)
        gl.glEnable(gl.GL_LIGHT1)
        gl.glEnable(gl.GL_COLOR_MATERIAL)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        
        # Lighting setup
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, [1.0, 2.0, 1.0, 0.0])
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_AMBIENT, [0.3, 0.3, 0.4, 1.0])
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, [0.8, 0.8, 0.9, 1.0])
        
        gl.glLightfv(gl.GL_LIGHT1, gl.GL_POSITION, [-1.0, 1.0, -1.0, 0.0])
        gl.glLightfv(gl.GL_LIGHT1, gl.GL_AMBIENT, [0.2, 0.2, 0.3, 1.0])
        gl.glLightfv(gl.GL_LIGHT1, gl.GL_DIFFUSE, [0.5, 0.5, 0.7, 1.0])
        
    def resizeGL(self, w, h):
        """Handle window resize"""
        gl.glViewport(0, 0, w, h)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        aspect = w / h if h != 0 else 1.0
        glu.gluPerspective(45, aspect, 0.1, 100.0)
        
    def paintGL(self):
        """Render the 3D scene"""
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        
        # Set camera position
        distance = self.grid_size * 1.8
        glu.gluLookAt(
            distance * np.sin(np.radians(self.rotation_y)) * np.cos(np.radians(self.rotation_x)),
            distance * np.sin(np.radians(self.rotation_x)) + 2,
            distance * np.cos(np.radians(self.rotation_y)) * np.cos(np.radians(self.rotation_x)),
            0, 0, 0,
            0, 1, 0
        )
        
        # Draw ground plane with grid
        self.draw_ground_grid()
        
        # Draw cells
        self.draw_cells()
        
        # Draw robot
        self.draw_robot()
        
        # Draw cell labels (D/C)
        self.draw_cell_labels()
        
    def draw_ground_grid(self):
        """Draw a subtle ground grid"""
        gl.glDisable(gl.GL_LIGHTING)
        gl.glBegin(gl.GL_LINES)
        gl.glColor4f(0.3, 0.3, 0.5, 0.3)
        
        size = self.grid_size
        offset = self.grid_size / 2
        
        for i in range(size + 1):
            pos = i - offset
            # Lines along X
            gl.glVertex3f(pos, -0.5, -offset)
            gl.glVertex3f(pos, -0.5, offset)
            # Lines along Z
            gl.glVertex3f(-offset, -0.5, pos)
            gl.glVertex3f(offset, -0.5, pos)
            
        gl.glEnd()
        gl.glEnable(gl.GL_LIGHTING)
        
    def draw_cells(self):
        """Draw the grid cells as 3D cubes with glow"""
        offset = self.grid_size / 2
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x = i - offset + 0.5
                z = j - offset + 0.5
                
                # Determine cell color and glow
                if i < len(self.cells) and j < len(self.cells[i]):
                    if self.cells[i][j] == CellState.DIRTY:
                        color = self.dirty_color
                        emissive = [0.3, 0.0, 0.0, 1.0]
                    else:
                        color = self.clean_color
                        emissive = [0.0, 0.3, 0.0, 1.0]
                else:
                    color = [0.3, 0.3, 0.3, 0.5]
                    emissive = [0.0, 0.0, 0.0, 1.0]
                
                # Draw cube with glow
                gl.glMaterialfv(gl.GL_FRONT, gl.GL_AMBIENT_AND_DIFFUSE, color)
                gl.glMaterialfv(gl.GL_FRONT, gl.GL_EMISSION, emissive)
                
                self.draw_cube(x, 0, z, 0.4)
                
    def draw_cube(self, x, y, z, size):
        """Draw a cube at the specified position"""
        vertices = [
            [x - size, y - size, z - size],
            [x + size, y - size, z - size],
            [x + size, y + size, z - size],
            [x - size, y + size, z - size],
            [x - size, y - size, z + size],
            [x + size, y - size, z + size],
            [x + size, y + size, z + size],
            [x - size, y + size, z + size]
        ]
        
        faces = [
            [0, 1, 2, 3],
            [4, 5, 6, 7],
            [0, 1, 5, 4],
            [2, 3, 7, 6],
            [0, 3, 7, 4],
            [1, 2, 6, 5]
        ]
        
        normals = [
            [0, 0, -1],
            [0, 0, 1],
            [0, -1, 0],
            [0, 1, 0],
            [-1, 0, 0],
            [1, 0, 0]
        ]
        
        gl.glBegin(gl.GL_QUADS)
        for i, face in enumerate(faces):
            gl.glNormal3fv(normals[i])
            for vertex in face:
                gl.glVertex3fv(vertices[vertex])
        gl.glEnd()
        
    def draw_cell_labels(self):
        """Draw D/C labels on cells"""
        gl.glDisable(gl.GL_LIGHTING)
        gl.glColor4f(1.0, 1.0, 1.0, 0.8)
        
        # Note: In a real implementation, you'd use QPainter for text
        # This is a simplified version
        
        gl.glEnable(gl.GL_LIGHTING)
        
    def draw_robot(self):
        """Draw the robot with animation"""
        offset = self.grid_size / 2
        x = self.robot_pos[0] - offset + 0.5
        z = self.robot_pos[1] - offset + 0.5
        
        # Bobbing animation
        y_offset = np.sin(time.time() * 5) * 0.1
        
        # Robot body
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_AMBIENT_AND_DIFFUSE, [0.2, 0.5, 1.0, 1.0])
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_EMISSION, [0.1, 0.2, 0.5, 1.0])
        self.draw_cube(x, 0.3 + y_offset, z, 0.3)
        
        # Robot head
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_AMBIENT_AND_DIFFUSE, [1.0, 1.0, 0.8, 1.0])
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_EMISSION, [0.3, 0.3, 0.1, 1.0])
        self.draw_cube(x, 0.7 + y_offset, z, 0.15)
        
        # Robot eyes
        gl.glDisable(gl.GL_LIGHTING)
        gl.glColor4f(0.0, 1.0, 1.0, 1.0)
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex3f(x - 0.1, 0.75 + y_offset, z - 0.15)
        gl.glVertex3f(x + 0.1, 0.75 + y_offset, z - 0.15)
        gl.glVertex3f(x + 0.1, 0.65 + y_offset, z - 0.15)
        gl.glVertex3f(x - 0.1, 0.65 + y_offset, z - 0.15)
        gl.glEnd()
        gl.glEnable(gl.GL_LIGHTING)
        
    def update_animation(self):
        """Update animation"""
        self.update()
        
    def set_grid(self, grid):
        """Update the grid data"""
        self.cells = grid
        self.grid_size = len(grid) if grid else 3
        self.update()
        
    def set_robot_pos(self, pos):
        """Update robot position"""
        self.robot_pos = pos
        self.update()
        
    def mousePressEvent(self, event):
        """Handle mouse press"""
        self.last_mouse_pos = event.pos()
        
    def mouseMoveEvent(self, event):
        """Handle mouse move"""
        if self.last_mouse_pos:
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()
            self.rotation_y += dx * 0.5
            self.rotation_x = max(-30, min(60, self.rotation_x - dy * 0.5))
            self.last_mouse_pos = event.pos()
            self.update()

# ============================================================================
# MAIN WINDOW
# ============================================================================

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vacuum Cleaner AI Simulation")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize simulation components
        self.env = None
        self.reflex_agent = None
        self.model_agent = None
        self.current_agent = None
        self.simulation_timer = QTimer()
        self.simulation_timer.timeout.connect(self.simulation_step)
        self.is_paused = False
        self.speed = 1.0
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Left Panel
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background: rgba(20, 20, 40, 0.8);
                border: 1px solid #4a4a8a;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        
        # Title
        title = QLabel("VACUUM CLEANER\nAI SIMULATION")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #00ffff;
            text-shadow: 0 0 10px #00ffff;
            padding: 10px;
        """)
        left_layout.addWidget(title)
        
        # Grid Size
        left_layout.addWidget(QLabel("GRID SIZE:"))
        self.size_input = QLineEdit()
        self.size_input.setPlaceholderText("Enter size (2-8)")
        self.size_input.setText("3")
        self.size_input.setStyleSheet("""
            QLineEdit {
                background: rgba(10, 10, 20, 0.8);
                border: 1px solid #4a4a8a;
                border-radius: 5px;
                color: white;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #00ffff;
            }
        """)
        left_layout.addWidget(self.size_input)
        
        # Environment
        left_layout.addWidget(QLabel("ENVIRONMENT:"))
        self.env_combo = QComboBox()
        self.env_combo.addItems(["Random Environment", "Manual Environment"])
        self.env_combo.setStyleSheet("""
            QComboBox {
                background: rgba(10, 10, 20, 0.8);
                border: 1px solid #4a4a8a;
                border-radius: 5px;
                color: white;
                padding: 8px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #00ffff;
                margin-right: 5px;
            }
        """)
        left_layout.addWidget(self.env_combo)
        
        # Manual input preview (hidden initially)
        self.manual_preview = QLabel("Manual input will open in dialog")
        self.manual_preview.setStyleSheet("""
            background: rgba(0, 0, 0, 0.3);
            border: 1px dashed #4a4a8a;
            border-radius: 5px;
            padding: 10px;
            color: #a0a0ff;
            font-family: monospace;
        """)
        self.manual_preview.hide()
        left_layout.addWidget(self.manual_preview)
        
        # Buttons
        self.start_btn = QPushButton("▶ START SIMULATION")
        self.start_btn.clicked.connect(self.start_simulation)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00aa00,
                    stop:1 #00ff00);
                border: none;
                border-radius: 5px;
                color: black;
                font-weight: bold;
                padding: 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00cc00,
                    stop:1 #33ff33);
            }
            QPushButton:disabled {
                background: #666666;
                color: #999999;
            }
        """)
        left_layout.addWidget(self.start_btn)
        
        # Control buttons layout
        control_layout = QHBoxLayout()
        
        self.pause_btn = QPushButton("⏸ PAUSE")
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #aaaa00,
                    stop:1 #ffff00);
                border: none;
                border-radius: 5px;
                color: black;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:disabled {
                background: #666666;
                color: #999999;
            }
        """)
        control_layout.addWidget(self.pause_btn)
        
        self.step_btn = QPushButton("⏩ STEP")
        self.step_btn.clicked.connect(self.step_simulation)
        self.step_btn.setEnabled(False)
        self.step_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #aa5500,
                    stop:1 #ffaa00);
                border: none;
                border-radius: 5px;
                color: black;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:disabled {
                background: #666666;
                color: #999999;
            }
        """)
        control_layout.addWidget(self.step_btn)
        
        self.reset_btn = QPushButton("↺ RESET")
        self.reset_btn.clicked.connect(self.reset_simulation)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #aa0000,
                    stop:1 #ff0000);
                border: none;
                border-radius: 5px;
                color: white;
                font-weight: bold;
                padding: 8px;
            }
        """)
        control_layout.addWidget(self.reset_btn)
        
        left_layout.addLayout(control_layout)
        
        # Speed control
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(5)
        self.speed_slider.valueChanged.connect(self.update_speed)
        self.speed_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #2a2a4a;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #00ffff;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
        """)
        speed_layout.addWidget(self.speed_slider)
        self.speed_label = QLabel("1.0x")
        speed_layout.addWidget(self.speed_label)
        left_layout.addLayout(speed_layout)
        
        left_layout.addStretch()
        
        # Center Panel - 3D View
        center_panel = QFrame()
        center_panel.setStyleSheet("""
            QFrame {
                background: rgba(10, 10, 20, 0.9);
                border: 1px solid #4a4a8a;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        center_layout = QVBoxLayout(center_panel)
        
        view_title = QLabel("3D SIMULATION VIEW")
        view_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        view_title.setStyleSheet("color: #a0a0ff; font-size: 16px; padding: 5px;")
        center_layout.addWidget(view_title)
        
        self.gl_widget = GLWidget()
        self.gl_widget.setMinimumSize(600, 500)
        center_layout.addWidget(self.gl_widget)
        
        self.status_label = QLabel("Ready to start simulation...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            background: rgba(0, 0, 0, 0.3);
            border-radius: 5px;
            padding: 8px;
            color: #00ffff;
        """)
        center_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #4a4a8a;
                border-radius: 3px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ffff,
                    stop:1 #ff00ff);
                border-radius: 3px;
            }
        """)
        center_layout.addWidget(self.progress_bar)
        
        # Right Panel - Analytics
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background: rgba(20, 20, 40, 0.8);
                border: 1px solid #4a4a8a;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        
        # Analytics title
        analytics_title = QLabel("ANALYTICS DASHBOARD")
        analytics_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        analytics_title.setStyleSheet("""
            font-size: 18px;
            color: #ff00ff;
            font-weight: bold;
            padding: 10px;
        """)
        right_layout.addWidget(analytics_title)
        
        # Reflex Agent
        reflex_group = QFrame()
        reflex_group.setStyleSheet("""
            QFrame {
                background: rgba(30, 30, 50, 0.5);
                border: 1px solid #00ffff;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        reflex_layout = QVBoxLayout(reflex_group)
        
        reflex_title = QLabel("REFLEX AGENT")
        reflex_title.setStyleSheet("color: #00ffff; font-weight: bold;")
        reflex_layout.addWidget(reflex_title)
        
        self.reflex_moves = QLabel("Moves: 0")
        self.reflex_cleaned = QLabel("Cleaned: 0")
        reflex_layout.addWidget(self.reflex_moves)
        reflex_layout.addWidget(self.reflex_cleaned)
        right_layout.addWidget(reflex_group)
        
        # Model Agent
        model_group = QFrame()
        model_group.setStyleSheet("""
            QFrame {
                background: rgba(30, 30, 50, 0.5);
                border: 1px solid #ff00ff;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        model_layout = QVBoxLayout(model_group)
        
        model_title = QLabel("MODEL-BASED AGENT")
        model_title.setStyleSheet("color: #ff00ff; font-weight: bold;")
        model_layout.addWidget(model_title)
        
        self.model_moves = QLabel("Moves: 0")
        self.model_cleaned = QLabel("Cleaned: 0")
        model_layout.addWidget(self.model_moves)
        model_layout.addWidget(self.model_cleaned)
        right_layout.addWidget(model_group)
        
        # Efficiency
        eff_group = QFrame()
        eff_group.setStyleSheet("""
            QFrame {
                background: rgba(40, 40, 60, 0.7);
                border: 2px solid #ffff00;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        eff_layout = QVBoxLayout(eff_group)
        
        eff_title = QLabel("EFFICIENCY COMPARISON")
        eff_title.setStyleSheet("color: #ffff00; font-weight: bold;")
        eff_layout.addWidget(eff_title)
        
        self.reflex_eff = QLabel("Reflex: 0%")
        self.model_eff = QLabel("Model: 0%")
        eff_layout.addWidget(self.reflex_eff)
        eff_layout.addWidget(self.model_eff)
        right_layout.addWidget(eff_group)
        
        right_layout.addStretch()
        
        # Add all panels
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(center_panel, 3)
        main_layout.addWidget(right_panel, 1)
        
        # Store manual grid data
        self.manual_grid_data = None
        
    def start_simulation(self):
        """Start the simulation"""
        try:
            size = int(self.size_input.text())
            if size < 2 or size > 8:
                QMessageBox.warning(self, "Invalid Size", "Grid size must be between 2 and 8")
                return
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number")
            return
        
        # Handle environment type
        if self.env_combo.currentText() == "Manual Environment":
            # Open manual input dialog
            dialog = ManualEnvironmentDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted and dialog.grid_data:
                self.manual_grid_data = dialog.grid_data
                size = len(dialog.grid_data)
                self.env = GridEnvironment(size, 2, self.manual_grid_data)
                
                # Show preview
                preview_text = "\n".join([" ".join([str(cell) for cell in row]) for row in self.manual_grid_data])
                self.manual_preview.setText(f"Manual Grid:\n{preview_text}")
                self.manual_preview.show()
            else:
                return
        else:
            # Random environment
            self.env = GridEnvironment(size, 1)
            self.manual_preview.hide()
        
        # Create agents
        self.reflex_agent = ReflexAgent(self.env)
        self.model_agent = ModelBasedAgent(self.env)
        self.current_agent = self.reflex_agent
        
        # Update 3D view
        self.gl_widget.set_grid(self.env.grid)
        self.gl_widget.set_robot_pos((0, 0))
        
        # Enable/disable buttons
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.step_btn.setEnabled(True)
        
        # Start simulation
        self.is_paused = False
        self.pause_btn.setText("⏸ PAUSE")
        self.simulation_timer.start(int(500 / self.speed))
        
        self.status_label.setText("Simulation started - Reflex Agent running")
        
        # Update total cells for progress
        self.total_cells = size * size
        
    def simulation_step(self):
        """Execute one simulation step"""
        if self.is_paused:
            return
            
        self.step_simulation()
        
    def step_simulation(self):
        """Execute a single step"""
        if not self.current_agent:
            return
            
        # Run current agent
        if self.current_agent == self.reflex_agent:
            if self.reflex_agent.step():
                # Update display
                self.gl_widget.set_robot_pos(self.reflex_agent.current_pos)
                self.reflex_moves.setText(f"Moves: {self.reflex_agent.moves}")
                self.reflex_cleaned.setText(f"Cleaned: {self.reflex_agent.cleaned}")
                
                # Update status
                x, y = self.reflex_agent.current_pos
                self.status_label.setText(f"Reflex Agent cleaning cell ({x}, {y})")
                
                # Update progress
                progress = int((self.reflex_agent.moves / self.total_cells) * 100)
                self.progress_bar.setValue(progress)
                
                # Check if reflex agent is done
                if self.reflex_agent.moves >= self.total_cells:
                    self.status_label.setText("Reflex Agent completed - Starting Model Agent")
                    self.current_agent = self.model_agent
                    
        else:  # Model agent
            if self.model_agent.step():
                # Update display
                self.gl_widget.set_robot_pos(self.model_agent.current_pos)
                self.model_moves.setText(f"Moves: {self.model_agent.moves}")
                self.model_cleaned.setText(f"Cleaned: {self.model_agent.cleaned}")
                
                # Update status
                x, y = self.model_agent.current_pos
                self.status_label.setText(f"Model Agent cleaning cell ({x}, {y})")
                
                # Update efficiency
                self.update_efficiency()
                
                # Check if model agent is done
                if self.model_agent.moves >= len(self.model_agent.path):
                    self.simulation_timer.stop()
                    self.status_label.setText("Simulation Complete! ✓")
                    self.pause_btn.setEnabled(False)
                    self.step_btn.setEnabled(False)
                    self.progress_bar.setValue(100)
                    
    def update_efficiency(self):
        """Update efficiency calculations"""
        if self.reflex_agent.moves > 0:
            reflex_eff = (self.reflex_agent.cleaned / self.reflex_agent.moves) * 100
            self.reflex_eff.setText(f"Reflex: {reflex_eff:.0f}%")
            
        if self.model_agent.moves > 0:
            model_eff = (self.model_agent.cleaned / self.model_agent.moves) * 100
            self.model_eff.setText(f"Model: {model_eff:.0f}%")
            
    def toggle_pause(self):
        """Toggle simulation pause"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.setText("▶ RESUME")
            self.status_label.setText("Simulation Paused")
        else:
            self.pause_btn.setText("⏸ PAUSE")
            self.status_label.setText("Simulation Resumed")
            
    def update_speed(self, value):
        """Update simulation speed"""
        self.speed = value / 5.0
        self.speed_label.setText(f"{self.speed:.1f}x")
        if not self.is_paused and self.simulation_timer.isActive():
            self.simulation_timer.setInterval(int(500 / self.speed))
            
    def reset_simulation(self):
        """Reset the simulation"""
        self.simulation_timer.stop()
        self.reflex_agent = None
        self.model_agent = None
        self.current_agent = None
        
        # Reset UI
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.step_btn.setEnabled(False)
        self.pause_btn.setText("⏸ PAUSE")
        
        # Reset counters
        self.reflex_moves.setText("Moves: 0")
        self.reflex_cleaned.setText("Cleaned: 0")
        self.model_moves.setText("Moves: 0")
        self.model_cleaned.setText("Cleaned: 0")
        self.reflex_eff.setText("Reflex: 0%")
        self.model_eff.setText("Model: 0%")
        
        self.progress_bar.setValue(0)
        self.status_label.setText("Simulation Reset - Ready to start")
        
        # Clear 3D view
        self.gl_widget.set_grid([])
        self.gl_widget.set_robot_pos((0, 0))

# ============================================================================
# MAIN
# ============================================================================

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set dark theme palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(20, 20, 30))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(200, 200, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 40))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(40, 40, 50))
    palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(40, 40, 50))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 255))
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
