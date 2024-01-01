
cd C_lib


python -m build --wheel --no-isolation

cd ../

python -m pip install .\C_lib\dist\GOL-0.1-cp310-cp310-win_amd64.whl --force-reinstall