#!/usr/bin/env python3
"""
MonkeyType Runner para DC-API-X

Script para coletar informações de tipos em tempo de execução durante a execução de testes,
aplicar essas anotações de tipos aos módulos e gerar stubs para integração com mypy e pydantic.

Uso:
    python monkeytype_runner.py run [--test-path <caminho_do_teste>]
    python monkeytype_runner.py apply --module <caminho_do_módulo>
    python monkeytype_runner.py list
    python monkeytype_runner.py stub --module <caminho_do_módulo>

Exemplos:
    # Executar todos os testes do projeto com MonkeyType
    python monkeytype_runner.py run

    # Executar um teste específico com MonkeyType
    python monkeytype_runner.py run --test-path tests/test_config.py

    # Listar módulos com informações de tipo coletadas
    python monkeytype_runner.py list

    # Aplicar tipos ao módulo config
    python monkeytype_runner.py apply --module dc_api_x.config

    # Gerar stub para o módulo models
    python monkeytype_runner.py stub --module dc_api_x.models
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


class MonkeyTypeRunner:
    """Runner para MonkeyType no projeto DC-API-X."""

    def __init__(self) -> None:
        """Inicializa o runner com os caminhos do projeto."""
        # Encontra a raiz do projeto
        self.project_root = self._find_project_root()

        # Caminhos importantes
        self.venv_dir = Path(
            os.environ.get("VIRTUAL_ENV", self.project_root.parent / ".venv"),
        )
        self.python_exe = self.venv_dir / "bin" / "python"
        self.monkeytype_exe = self.venv_dir / "bin" / "monkeytype"

        # Diretório para o banco de dados MonkeyType
        self.db_dir = self.project_root / ".monkeytype"
        self.db_dir.mkdir(exist_ok=True)

        # Arquivo de banco de dados SQLite
        self.db_file = self.db_dir / "dc_api_x.sqlite"
        self.db_file_absolute = str(self.db_file.absolute())

        # Configura o ambiente para usar o banco de dados
        os.environ["MONKEYTYPE_DB"] = f"sqlite:///{self.db_file_absolute}"

        # Pasta de código fonte
        self.src_dir = self.project_root / "src"
        self.tests_dir = self.project_root / "tests"

        # Verifique se os diretórios existem
        if not self.src_dir.exists():
            raise FileNotFoundError(
                f"Diretório de código fonte não encontrado: {self.src_dir}",
            )
        if not self.tests_dir.exists():
            raise FileNotFoundError(
                f"Diretório de testes não encontrado: {self.tests_dir}",
            )

    def _find_project_root(self) -> Path:
        """Encontra a raiz do projeto DC-API-X."""
        # Obtém o diretório atual
        current_dir = Path.cwd()

        # Navega pelos diretórios pais procurando pelo pyproject.toml
        dir_to_check = current_dir
        while dir_to_check != dir_to_check.parent:  # Até chegar à raiz do sistema
            if (dir_to_check / "pyproject.toml").exists():
                # Verifica se é o projeto dc-api-x
                with open(dir_to_check / "pyproject.toml") as f:
                    content = f.read()
                    if 'name = "dc-api-x"' in content:
                        return dir_to_check
            dir_to_check = dir_to_check.parent

        # Se não encontrou, tenta o diretório atual ou diretório de script
        script_dir = Path(__file__).parent
        for check_dir in [current_dir, script_dir.parent]:
            if (check_dir / "pyproject.toml").exists():
                with open(check_dir / "pyproject.toml") as f:
                    content = f.read()
                    if 'name = "dc-api-x"' in content:
                        return check_dir

        # Se ainda não encontrou, assumimos que estamos no diretório dc-api-x
        return Path("dc-api-x").absolute()

    def run_tests_with_monkeytype(self, test_path: Optional[str] = None) -> int:
        """
        Executa testes com instrumentação do MonkeyType para coletar tipos.

        Args:
            test_path: Caminho do teste específico a ser executado (opcional)

        Returns:
            Código de retorno do comando
        """
        # Muda para o diretório raiz do projeto
        os.chdir(self.project_root)

        # Constrói o comando monkeytype run -m pytest
        cmd = [
            "monkeytype",
            "run",
            "-m",
            "pytest",
        ]

        # Adiciona o caminho do teste, se especificado
        if test_path:
            test_path_full = self.project_root / test_path
            if not test_path_full.exists():
                print(f"Erro: Caminho de teste {test_path_full} não encontrado")
                return 1
            cmd.append(str(test_path))

        print("Executando testes com MonkeyType em DC-API-X")
        result = subprocess.run(cmd, check=False)

        if result.returncode == 0:
            print(
                "\nMonkeyType coletou tipos com sucesso durante a execução dos testes.",
            )

            # Lista os módulos disponíveis
            print("\nMódulos com informações de tipo coletadas:")
            subprocess.run(["monkeytype", "list-modules"], check=False)

            print("\nPara aplicar os tipos coletados:")
            print(f"  python {Path(__file__).name} apply --module <caminho_do_módulo>")

            # Sugestão para aplicar tipos ao módulo de configuração
            print("\nExemplo de aplicação de tipos:")
            print(f"  python {Path(__file__).name} apply --module dc_api_x.config")
        else:
            print(
                "\nAlguns testes falharam, mas os tipos podem ter sido coletados mesmo assim.",
            )
            print("Verifique os módulos disponíveis com:")
            print(f"  python {Path(__file__).name} list")

        return result.returncode

    def list_modules(self) -> int:
        """
        Lista módulos com informações de tipo coletadas.

        Returns:
            Código de retorno do comando
        """
        # Verifica se o banco de dados existe (opcional, o MonkeyType já faz isso)
        # if not self.db_file.exists():
        #    print(f"Erro: Arquivo de banco de dados não encontrado: {self.db_file}")
        #    print(f"Execute os testes primeiro: python {Path(__file__).name} run")
        #    return 1

        # Usa o comando monkeytype list-modules diretamente
        cmd = ["monkeytype", "list-modules"]

        print("Listando módulos com informações de tipo coletadas:")
        result = subprocess.run(cmd, check=False)

        # Se a listagem foi bem-sucedida, exibe instruções para o usuário
        if result.returncode == 0:
            print("\nPara aplicar tipos a um módulo específico:")
            print(f"  python {Path(__file__).name} apply --module <nome_do_módulo>")
            print("\nExemplo:")
            print(f"  python {Path(__file__).name} apply --module dc_api_x.config")

        return result.returncode

    def apply_types(self, module_path: str = None, apply_all: bool = False) -> int:
        """
        Aplica tipos coletados a um módulo ou a todos os módulos disponíveis.

        Args:
            module_path: Caminho do módulo para aplicar os tipos (opcional se apply_all=True)
            apply_all: Se True, aplica tipos a todos os módulos disponíveis

        Returns:
            Código de retorno do comando
        """
        if apply_all:
            # Lista todos os módulos com informações de tipo
            cmd_list = ["monkeytype", "list-modules"]
            print("Listando módulos com informações de tipo...")
            result = subprocess.run(cmd_list, check=False, capture_output=True, text=True)
            
            if result.returncode != 0:
                print("Erro ao listar módulos com informações de tipo")
                return result.returncode
            
            # Extrai os módulos da saída
            modules = [m.strip() for m in result.stdout.strip().split('\n') if m.strip()]
            
            # Filtra apenas os módulos dc_api_x
            dc_modules = [m for m in modules if m.startswith('dc_api_x.')]
            
            if not dc_modules:
                print("Nenhum módulo dc_api_x encontrado com informações de tipo")
                return 0
            
            print(f"Encontrados {len(dc_modules)} módulos para aplicar tipos:")
            for m in dc_modules:
                print(f"  - {m}")
            
            # Aplica tipos a cada módulo
            success_count = 0
            failed_modules = []
            
            for module in dc_modules:
                print(f"\n{'='*40}")
                print(f"Aplicando tipos ao módulo {module}...")
                result = self.apply_types(module)
                
                if result == 0:
                    success_count += 1
                else:
                    failed_modules.append(module)
            
            # Resumo
            print(f"\n{'='*60}")
            print(f"Resumo: Aplicação de tipos concluída para {success_count}/{len(dc_modules)} módulos")
            
            if failed_modules:
                print("Falha ao aplicar tipos para os seguintes módulos:")
                for m in failed_modules:
                    print(f"  - {m}")
                return 1
            
            return 0
        
        # Aplicar tipos a um único módulo
        if not module_path:
            print("Erro: Caminho do módulo não especificado")
            return 1
            
        # Verifica se o módulo existe (por segurança)
        module_parts = module_path.split(".")
        if module_parts[0] == "dc_api_x":
            # Corrige o caminho para apontar para o módulo dentro de src/dc_api_x/
            module_file = self.src_dir / "dc_api_x" / "/".join(module_parts[1:])
            module_file = module_file.with_suffix(".py")
            if not module_file.exists():
                print(f"Erro: Arquivo do módulo não encontrado: {module_file}")
                return 1

        # Aplica os tipos usando o comando monkeytype apply diretamente
        cmd = [
            "monkeytype",
            "apply",
            module_path,
        ]

        print(f"Aplicando tipos ao módulo {module_path}")
        result = subprocess.run(cmd, check=False)

        if result.returncode == 0:
            print(f"\nTipos aplicados com sucesso ao módulo {module_path}")
            print(
                "Não se esqueça de verificar as alterações e executar mypy para validar os tipos."
            )
            print("\nPara verificar a conformidade dos tipos:")
            print(
                f"  cd {self.project_root} && python -m mypy src/{module_path.replace('.', '/')}.py"
            )

            # Guia para modelos Pydantic
            if "models" in module_path or "schema" in module_path:
                print("\nDica para integração com Pydantic:")
                print(
                    "  Para classes de modelo, você pode converter anotações de tipo para campos Pydantic:"
                )
                print("  Em vez de:")
                print("    def __init__(self, name: str, age: Optional[int] = None):")
                print("  Use:")
                print("    class User(BaseModel):")
                print("        name: str")
                print("        age: Optional[int] = None")

        return result.returncode

    def generate_stub(self, module_path: str) -> int:
        """
        Gera stub com tipos coletados.
        
        Args:
            module_path: Caminho do módulo para gerar o stub
            
        Returns:
            Código de retorno do comando
        """
        # Verifica se o módulo existe (por segurança)
        module_parts = module_path.split(".")
        if module_parts[0] == "dc_api_x":
            # Corrige o caminho para apontar para o módulo dentro de src/dc_api_x/
            module_file = self.src_dir / "dc_api_x" / "/".join(module_parts[1:])
            module_file = module_file.with_suffix(".py")
            if not module_file.exists():
                print(f"Erro: Arquivo do módulo não encontrado: {module_file}")
                return 1

        # Gera o stub usando o comando monkeytype stub diretamente
        cmd = [
            "monkeytype",
            "stub",
            module_path,
        ]

        print(f"Gerando stub de tipos para o módulo {module_path}")
        result = subprocess.run(cmd, check=False)

        if result.returncode == 0:
            print(f"\nStub de tipos gerado com sucesso para {module_path}")
            print(
                "Revise o stub gerado e aplique-o manualmente ao seu código, se necessário.",
            )

            # Dicas para integração com Pydantic
            if "models" in module_path or "schema" in module_path:
                print("\nDica para integração com Pydantic:")
                print(
                    "  Para classes de modelo, converta as anotações de tipo para campos Pydantic:",
                )
                print("  Exemplo:")
                print("    # Stub gerado pelo MonkeyType")
                print("    class User:")
                print("        name: str")
                print("        email: str")
                print("        age: Optional[int]")
                print("    ")
                print("    # Convertido para Pydantic")
                print("    class User(BaseModel):")
                print("        name: str")
                print("        email: EmailStr  # Com validação adicional")
                print("        age: Optional[int] = None")

        return result.returncode


def parse_args() -> argparse.Namespace:
    """Analisa os argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="DC-API-X MonkeyType Runner - Ferramenta para coleção e aplicação de tipos.",
    )

    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")
    subparsers.required = True

    # Comando run
    run_parser = subparsers.add_parser(
        "run",
        help="Executar testes com rastreamento do MonkeyType",
    )
    run_parser.add_argument(
        "--test-path",
        help="Caminho específico do teste dentro do projeto",
    )

    # Comando list
    list_parser = subparsers.add_parser(
        "list",
        help="Listar módulos com tipos coletados",
    )

    # Comando apply
    apply_parser = subparsers.add_parser(
        "apply",
        help="Aplicar tipos coletados a um módulo",
    )
    apply_parser.add_argument(
        "--module",
        required=True,
        help="Caminho do módulo para aplicar os tipos",
    )

    # Comando stub
    stub_parser = subparsers.add_parser(
        "stub",
        help="Gerar arquivo stub com tipos coletados",
    )
    stub_parser.add_argument(
        "--module",
        required=True,
        help="Caminho do módulo para gerar o stub",
    )

    return parser.parse_args()


def main() -> int:
    """Ponto de entrada principal."""
    try:
        args = parse_args()
        runner = MonkeyTypeRunner()

        if args.command == "run":
            return runner.run_tests_with_monkeytype(args.test_path)
        if args.command == "list":
            return runner.list_modules()
        if args.command == "apply":
            return runner.apply_types(args.module)
        if args.command == "stub":
            return runner.generate_stub(args.module)
        print(f"Comando desconhecido: {args.command}")
        return 1
    except Exception as e:
        print(f"Erro: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
