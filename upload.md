https://autopilot-docs.readthedocs.io/en/latest/license_list.html

https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56




```
> python3.8 -m pip install --user --force-reinstall setuptools wheel twine

> python3.8 setup.py sdist
> python3.8 -m twine upload dist/* --verbose 

> python3.8 -m pip install --upgrade bones_data

```

