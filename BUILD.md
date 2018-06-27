```
python setup.py sdist
python setup.py bdist_wheel --universal
twine upload dist/pyky040-0.1.x*
```