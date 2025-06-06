from setuptools import setup, Extension

gpmf_module = Extension(
    'gpmf_parser',
    sources=['gpmf_wrapper.c', 'GPMF_parser.c', 'GPMF_utils.c', 'GPMF_mp4reader.c'],
    include_dirs=['.'],
    extra_compile_args=['-std=c99']
)

setup(
    name='gpmf_parser',
    version='0.1',
    ext_modules=[gpmf_module],
)