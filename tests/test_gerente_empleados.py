import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import types

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
def _dummy_ctk_module():
    def noop(*_a, **_k):
        pass

    return types.SimpleNamespace(
        CTk=type('CTk', (), {}),
        CTkFrame=type('CTkFrame', (), {}),
        CTkLabel=type('CTkLabel', (), {}),
        CTkButton=type('CTkButton', (), {}),
        CTkTabview=type('CTkTabview', (), {}),
        CTkToplevel=type('CTkToplevel', (), {}),
        set_appearance_mode=noop,
        set_default_color_theme=noop,
    )

tk_mod = types.SimpleNamespace(messagebox=MagicMock(), ttk=MagicMock(), END='end')



class GerenteEmpleadosTest(unittest.TestCase):
    def test_cargar_empleados_excluye_roles(self):
        with patch.dict(sys.modules, {
            'customtkinter': _dummy_ctk_module(),
            'tkinter': tk_mod,
            'tkcalendar': MagicMock(),
        }):
            with patch('interfaces.gerente.ConexionBD') as mock_conn_cls:
                from interfaces.gerente import VentanaGerente

                conn = MagicMock()
                mock_conn_cls.return_value = conn
            conn.ejecutar.side_effect = [
                [(2, 'Empleado'), (3, 'Vendedor')],
                [(1, 'Ana', 'a@x', 'Empleado')],
            ]
            g = object.__new__(VentanaGerente)
            g.conexion = conn
            g.combo_tipo = MagicMock()
            g.tree_emp = MagicMock()
            g.tree_emp.get_children.return_value = []

            g._cargar_empleados()

            q1 = conn.ejecutar.call_args_list[0].args[0].lower()
            q2 = conn.ejecutar.call_args_list[1].args[0].lower()
            self.assertIn("lower(nombre) not in ('administrador','gerente')", q1)
            self.assertIn("lower(te.nombre) not in ('administrador','gerente')", q2)
            g.combo_tipo.configure.assert_called_once_with(values=['Empleado', 'Vendedor'])
            g.tree_emp.insert.assert_called_once()

    def test_cambiar_tipo_bloquea_roles_protegidos_actual(self):
        with patch.dict(sys.modules, {
            'customtkinter': _dummy_ctk_module(),
            'tkinter': tk_mod,
            'tkcalendar': MagicMock(),
        }):
            from interfaces.gerente import VentanaGerente
            with patch('interfaces.gerente.messagebox') as mock_mb:
                g = object.__new__(VentanaGerente)
                g.tree_emp = MagicMock()
                g.tree_emp.focus.return_value = 'item'
                g.tree_emp.item.return_value = {"values": (1, 'Ana', 'a@x', 'Gerente')}
                g.combo_tipo = MagicMock()
                g.combo_tipo.get.return_value = 'Empleado'
                g.tipo_map = {'Empleado': 2}
                g.conexion = MagicMock()

                g._cambiar_tipo()

                mock_mb.showerror.assert_called_once()
                g.conexion.ejecutar.assert_not_called()

    def test_cambiar_tipo_bloquea_roles_protegidos_nuevo(self):
        with patch.dict(sys.modules, {
            'customtkinter': _dummy_ctk_module(),
            'tkinter': tk_mod,
            'tkcalendar': MagicMock(),
        }):
            from interfaces.gerente import VentanaGerente
            with patch('interfaces.gerente.messagebox') as mock_mb:
                g = object.__new__(VentanaGerente)
                g.tree_emp = MagicMock()
                g.tree_emp.focus.return_value = 'item'
                g.tree_emp.item.return_value = {"values": (1, 'Ana', 'a@x', 'Empleado')}
                g.combo_tipo = MagicMock()
                g.combo_tipo.get.return_value = 'Gerente'
                g.tipo_map = {'Gerente': 3}
                g.conexion = MagicMock()

                g._cambiar_tipo()

                mock_mb.showerror.assert_called_once()
                g.conexion.ejecutar.assert_not_called()

    def test_eliminar_empleado_bloquea_roles_protegidos(self):
        with patch.dict(sys.modules, {
            'customtkinter': _dummy_ctk_module(),
            'tkinter': tk_mod,
            'tkcalendar': MagicMock(),
        }):
            from interfaces.gerente import VentanaGerente
            with patch('interfaces.gerente.messagebox') as mock_mb:
                g = object.__new__(VentanaGerente)
                g.tree_emp = MagicMock()
                g.tree_emp.focus.return_value = 'item'
                g.tree_emp.item.return_value = {"values": (1, 'Ana', 'a@x', 'Administrador')}
                g.conexion = MagicMock()

                g._eliminar_empleado()

                mock_mb.showerror.assert_called_once()
                g.conexion.ejecutar.assert_not_called()
                mock_mb.askyesno.assert_not_called()


if __name__ == '__main__':
    unittest.main()
