import unittest
from unittest.mock import patch

from certificado.services.revisor_service import RevisorService


class TestIngresoTecnico(unittest.TestCase):
    @patch("certificado.services.revisor_service.consultar_telnet")
    def test_consulta_telnet_sin_contrasena_ssh_y_acceso_ok(self, consultar_telnet_mock):
        def responder_telnet(host, puerto, comando):
            if comando == "cmd status":
                return "Pancoordinator status\nVersion v9.3.1\nN of motes attached: 2"
            if comando == "cmd motes":
                return "1 00:15:8D:00:00:00:01 80:81 4 Equipo 1"
            self.fail(f"Comando inesperado: {comando}")

        consultar_telnet_mock.side_effect = responder_telnet

        resultado = RevisorService.consultar_ingreso_tecnico_remoto({
            "host": "ce-prueba.acuimatic.com",
            "puerto_telnet": "9999",
            # Sin contraseña SSH: Telnet debe continuar funcionando.
        })

        self.assertEqual(resultado["acceso_remoto"], "OK")
        self.assertIn("Version v9.3.1", resultado["antena_status"])
        self.assertIn("00:15:8D:00:00:00:01", resultado["equipos_conectados"])
        self.assertIn("cmd status", [call.args[2] for call in consultar_telnet_mock.call_args_list])
        self.assertIn("cmd motes", [call.args[2] for call in consultar_telnet_mock.call_args_list])
        self.assertIn("Sin datos: se requieren credenciales SSH", resultado["voltaje_pilas"])
        self.assertIn("Acceso remoto: OK", resultado["plantilla_texto"])


if __name__ == "__main__":
    unittest.main()
