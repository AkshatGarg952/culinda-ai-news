import subprocess
try:
    out = subprocess.check_output(['pytest', '-v', 'tests/test_normalizer.py'], text=True, stderr=subprocess.STDOUT)
    print("SUCCESS")
except subprocess.CalledProcessError as e:
    with open('pytest_err.txt', 'w', encoding='utf-8') as f:
        f.write(e.output)
    print("FAILED")
