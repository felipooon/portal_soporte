import os

for root, _, files in os.walk('certificado'):
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'from src.' in content or 'import src.' in content:
                content = content.replace('from src.', 'from certificado.').replace('import src.', 'import certificado.')
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
