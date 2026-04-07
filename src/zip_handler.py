# -*- coding: utf-8 -*-
"""
Módulo para extração de arquivos ZIP protegidos por senha.
Suporta ZIPs com criptografia AES (usados pela Xiaomi no export de dados).
"""

import zipfile
import tempfile
import os
import io

try:
    import pyzipper
    HAS_PYZIPPER = True
except ImportError:
    HAS_PYZIPPER = False


def extrair_zip(uploaded_file, senha: str) -> tuple[str, list[str]]:
    """
    Extrai o conteúdo de um arquivo ZIP protegido por senha.
    
    Args:
        uploaded_file: arquivo enviado pelo Streamlit (UploadedFile)
        senha: senha para desbloquear o ZIP
        
    Returns:
        tuple: (caminho do diretório temporário, lista de arquivos extraídos)
        
    Raises:
        ValueError: se a senha estiver incorreta ou o arquivo for inválido
    """
    temp_dir = tempfile.mkdtemp(prefix="mifitness_")
    senha_bytes = senha.encode("utf-8")
    
    # Ler bytes do arquivo enviado
    file_bytes = uploaded_file.read()
    uploaded_file.seek(0)  # Reset para possível re-leitura
    
    # Tentar primeiro com pyzipper (suporta AES)
    if HAS_PYZIPPER:
        try:
            with pyzipper.AESZipFile(io.BytesIO(file_bytes), 'r') as zf:
                zf.setpassword(senha_bytes)
                zf.extractall(temp_dir)
                arquivos = zf.namelist()
                return temp_dir, [a for a in arquivos if not a.endswith('/')]
        except RuntimeError as e:
            if "password" in str(e).lower() or "Bad password" in str(e):
                raise ValueError("❌ Senha incorreta! Verifique a senha enviada por e-mail pela Xiaomi.")
            raise ValueError(f"❌ Erro ao extrair o ZIP: {e}")
        except Exception:
            pass  # Tentar com zipfile padrão
    
    # Fallback com zipfile padrão
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes), 'r') as zf:
            zf.setpassword(senha_bytes)
            zf.extractall(temp_dir)
            arquivos = zf.namelist()
            return temp_dir, [a for a in arquivos if not a.endswith('/')]
    except RuntimeError as e:
        if "password" in str(e).lower():
            raise ValueError("❌ Senha incorreta! Verifique a senha enviada por e-mail pela Xiaomi.")
        # Pode ser AES sem pyzipper instalado
        if not HAS_PYZIPPER:
            raise ValueError(
                "❌ Este ZIP usa criptografia AES. Instale o pyzipper: `pip install pyzipper`"
            )
        raise ValueError(f"❌ Erro ao extrair o ZIP: {e}")
    except zipfile.BadZipFile:
        raise ValueError("❌ O arquivo enviado não é um ZIP válido.")


def listar_csvs(temp_dir: str, arquivos: list[str]) -> list[str]:
    """
    Retorna apenas os arquivos CSV da lista de arquivos extraídos.
    """
    csvs = []
    for a in arquivos:
        if a.lower().endswith('.csv'):
            caminho = os.path.join(temp_dir, a)
            if os.path.exists(caminho):
                csvs.append(a)
    return csvs
