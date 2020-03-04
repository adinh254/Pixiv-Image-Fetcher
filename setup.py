from setuptools import setup

setup(name='pixiv-image-fetcher',
      version='0.1',
      description='Fetch images from user bookmarks.',
      url='https://github.com/adinh254/Pixiv-Image-Fetcher',
      author='adinh',
      author_email='adinh254@gmail.com',
      license='MIT',
      packages=['pixiv_image_fetcher'],
      install_requires=['scrapy'],
      zip_safe=False)
