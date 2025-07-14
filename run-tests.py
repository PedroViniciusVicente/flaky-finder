import subprocess
import re
import os
from datetime import datetime

# ============= CONFIGURAÇÕES =============
PROJECT_ROOT = "projects/cs4218-2420-ecom-project-team15"
LOG_DIRECTORY = "logs_cs4218"
TOTAL_RUNS = 1000
LOG_INTERVAL = 20

COMMAND = [
    'npx', 'jest', 
    'controllers/integration-tests/categoryControllerPartA.integration.test.js',
    '-t', 'should return all categories when categories exist',
    '--coverage=false'
]
# ================================================================

class TestLogger:
    """Classe para acumular e gerenciar os logs dos testes"""
    def __init__(self, log_dir):
        self.log_buffer = []
        self.log_dir = log_dir
    
    def add_test_result(self, run_number, test_result):
        """Adiciona um resultado de teste ao buffer"""
        self.log_buffer.append({
            'run_number': run_number,
            'output': test_result['output'],
            'error': test_result['error'],
            'timestamp': test_result['timestamp'],
            'failed': test_result['failed'],
            'returncode': test_result['returncode']
        })
    
    def write_log_file(self, start_run, end_run):
        """Escreve um arquivo de log com todos os testes no intervalo"""
        log_filename = os.path.join(
            self.log_dir, 
            f'jest_test_log_{start_run}_to_{end_run}.txt'
        )
        
        os.makedirs(self.log_dir, exist_ok=True)
        
        with open(log_filename, 'w') as log_file:
            log_file.write(f'=== Log de Testes {start_run} a {end_run} ===\n\n')
            
            for test in self.log_buffer:
                status = "FALHOU" if test['failed'] else "PASSOU"
                log_file.write(f"\n=== Teste #{test['run_number']} - {test['timestamp']} - {status} ===\n")
                log_file.write(test['output'])
                
                # Mostra a seção de ERROS apenas se houver erros relevantes
                if test['failed'] or ("error" in test['error'].lower() and "PASS" not in test['error']):
                    log_file.write('\n=== ERROS ===\n')

                log_file.write(test['error'])
                
                log_file.write(f"\nCódigo de retorno: {test['returncode']}\n")
                log_file.write('\n' + '='*80 + '\n')
            
            log_file.write(f'\n=== Fim do Log ===\n')
        
        print(f'  Logs salvos em {os.path.abspath(log_filename)}')
        self.log_buffer = []

def change_to_project_root(original_dir):
    """Muda para o diretório raiz do projeto"""
    try:
        os.chdir(PROJECT_ROOT)
        print(f"Entrou no diretório do projeto: {os.getcwd()}")
        return True
    except FileNotFoundError:
        print(f"Erro: Diretório do projeto não encontrado: {PROJECT_ROOT}")
        os.chdir(original_dir)
        return False

def create_log_directory():
    """Cria o diretório para armazenar os logs se não existir"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(script_dir, LOG_DIRECTORY)
    
    os.makedirs(log_dir, exist_ok=True)
    print(f"Diretório de logs: {log_dir}")
    
    return log_dir

def run_jest_test():
    """Executa o teste Jest e retorna os resultados"""
    result = subprocess.run(COMMAND, capture_output=True, text=True)
    combined_output = result.stdout + "\n" + result.stderr
    
    # Verifica falhas de várias maneiras diferentes
    tests_failed = (
        result.returncode != 0 or  # Código de retorno não-zero indica falha
        "Tests:      1 failed" in combined_output or
        "Test Suites: 1 failed" in combined_output or
        "FAIL" in combined_output
    )
    
    return {
        'output': result.stdout,
        'error': result.stderr,
        'returncode': result.returncode,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'failed': tests_failed,
        'combined_output': combined_output
    }

def extract_failed_test_info(test_result):
    """Extrai informações detalhadas de testes falhados"""
    output = test_result['combined_output']
    
    # Tenta encontrar a seção de falha completa
    fail_section = re.search(
        r'(FAIL.*?Test Suites:.*?\n(.*?)\n\nTest Suites:)', 
        output, 
        re.DOTALL
    )
    
    if fail_section:
        return fail_section.group(1).strip()
    
    # Se não encontrar, tenta pegar pelo menos o erro específico
    specific_error = re.search(
        r'(● renders category tiles.*?\n.*?\n.*?\n.*?)', 
        output
    )
    
    if specific_error:
        return specific_error.group(1).strip()
    
    # Se ainda não encontrar, retorna pelo menos a parte FAIL
    fail_line = re.search(r'(FAIL.*)', output)
    if fail_line:
        return fail_line.group(1).strip()
    
    # Último recurso - retorna a saída combinada
    return output

def main():
    original_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = create_log_directory()
    
    project_dir_success = change_to_project_root(original_dir)
    if not project_dir_success:
        return
    
    failed_tests = []
    test_logger = TestLogger(log_dir)
    
    for run in range(1, TOTAL_RUNS + 1):
        print(f'Executando teste {run}/{TOTAL_RUNS}...')
        test_result = run_jest_test()
        
        test_logger.add_test_result(run, test_result)
        
        if test_result['failed']:
            failed_info = extract_failed_test_info(test_result)
            failed_tests.append({
                'run_number': run,
                'timestamp': test_result['timestamp'],
                'info': failed_info,
                'returncode': test_result['returncode']
            })
            print(f'  Teste {run} FALHOU! (Código: {test_result["returncode"]})')
        
        if run % LOG_INTERVAL == 0 or run == TOTAL_RUNS:
            start_run = run - LOG_INTERVAL + 1 if run % LOG_INTERVAL == 0 else (run // LOG_INTERVAL) * LOG_INTERVAL + 1
            test_logger.write_log_file(start_run, run)
    
    os.chdir(original_dir)
    
    report_filename = os.path.join(log_dir, 'failed_tests_report.txt')
    with open(report_filename, 'w') as report_file:
        report_file.write('=== RELATÓRIO DE TESTES FALHADOS ===\n\n')
        report_file.write(f'Total de testes executados: {TOTAL_RUNS}\n')
        report_file.write(f'Total de falhas: {len(failed_tests)}\n')
        report_file.write(f'Taxa de falha: {len(failed_tests)/TOTAL_RUNS*100:.2f}%\n\n')
        
        for fail in failed_tests:
            report_file.write(f'Teste #{fail["run_number"]} - {fail["timestamp"]} (Código: {fail["returncode"]}):\n')
            report_file.write(fail['info'])
            report_file.write('\n' + '='*80 + '\n\n')
        
    if failed_tests:
        print(f'\nOuveram falhas!! Relatório de testes falhados salvo em {os.path.abspath(report_filename)}')
    else:
        print(f'\nTodos os testes passaram. Relatório de testes salvo em {os.path.abspath(report_filename)}')

if __name__ == '__main__':
    main()