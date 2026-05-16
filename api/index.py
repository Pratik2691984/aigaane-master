from pathlib import Path
import importlib.util
import sys


kernel_api_path = Path(__file__).with_name("kernel_api.py")
spec = importlib.util.spec_from_file_location("kernel_api", kernel_api_path)
kernel_api = importlib.util.module_from_spec(spec)
sys.modules["kernel_api"] = kernel_api
spec.loader.exec_module(kernel_api)

app = kernel_api.app
handler = kernel_api.handler
