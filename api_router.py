from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
import subprocess
import json
import os

router = APIRouter()

# Lista de testes disponíveis
available_tests = [
    {"name": "dns", "description": "Teste de latência DNS"},
    {"name": "ping", "description": "Ping 4 pacotes para 8.8.8.8"},
    {"name": "speed", "description": "Velocidade de Upload e Download"},
    {"name": "jitter", "description": "Variabilidade da latência"},
    {"name": "bufferbloat", "description": "Carga de rede sob ping"},
    {"name": "packetloss", "description": "Perda de pacotes"},
    {"name": "traceroute", "description": "Rota até 8.8.8.8"}
]

@router.get("/api/tests")
def list_tests():
    return available_tests

@router.post("/api/run/{test_name}")
def run_test(test_name: str):
    script_map = {
        "dns": "dns_test.py",
        "ping": "ping",
        "speed": "speedtest-cli",
        "jitter": "jitter_test.py",
        "bufferbloat": "bufferbloat_test.py",  # Corrigir nome real do script
        "packetloss": "packet_loss_test.py",
        "traceroute": "traceroute.py"
    }

    if test_name not in script_map:
        return {"status": "erro", "mensagem": f"Teste '{test_name}' não encontrado"}

    try:
        # Teste de ping
        if test_name == "ping":
            output = subprocess.check_output(["ping", "-c", "4", "8.8.8.8"], stderr=subprocess.STDOUT).decode()
            return {"status": "ok", "output": output}

        # Teste de velocidade com saída JSON
        elif test_name == "speed":
            try:
                output = subprocess.check_output(["speedtest-cli", "--simple"], stderr=subprocess.STDOUT).decode()
                lines = output.strip().split("\n")
                ping = float(lines[0].split(":")[1].replace(" ms", "").strip())
                download = float(lines[1].split(":")[1].replace(" Mbit/s", "").strip())
                upload = float(lines[2].split(":")[1].replace(" Mbit/s", "").strip())

                return JSONResponse(content={
                    "ping": ping,
                    "download": download,
                    "upload": upload
                })
            except Exception as e:
                return {"status": "erro", "mensagem": "Falha ao converter resultado para JSON", "raw": output, "erro": str(e)}

        # Outros scripts Python
        else:
            output = subprocess.check_output(["python3", f"scripts/{script_map[test_name]}"], stderr=subprocess.STDOUT).decode()
            try:
                return json.loads(output)  # Se o script já retornar JSON
            except:
                return {"status": "ok", "output": output}  # Retorno como texto padrão

    except subprocess.CalledProcessError as e:
        return {"status": "erro", "erro": e.output.decode()}

@router.post("/api/monitor/anacom")
def start_anacom_monitor():
    try:
        subprocess.Popen(["python3", "scripts/deepseek_python_20250429_8963ca.py"])
        return {"status": "iniciado", "mensagem": "Monitoramento ANACOM foi iniciado com sucesso."}
    except Exception as e:
        return {"status": "erro", "erro": str(e)}

@router.get("/api/report/latest")
def get_latest_report():
    folder = "static"
    latest_file = None
    try:
        files = [f for f in os.listdir(folder) if f.endswith(".html")]
        if not files:
            return {"status": "erro", "mensagem": "Nenhum relatório encontrado."}
        latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(folder, x)))
        return FileResponse(os.path.join(folder, latest_file), media_type="text/html")
    except Exception as e:
        return {"status": "erro", "mensagem": "Erro ao obter relatório.", "erro": str(e)}
