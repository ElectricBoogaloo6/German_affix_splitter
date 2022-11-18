from setuptools import setup

setup(
    name='german_affix_splitter',
    version='0.1',
    author='ElectricBoogaloo6',
    author_email='20081208@mail.wit.ie',
    packages=['German_affix_splitter'],
    url='https://github.com/ElectricBoogaloo6/German_affix_splitter',
    license='nolicense',
    description='German affix splitter implements multiple methods to return German affixes along with their Zipf frequencies.',
    long_description=open('README.md').read(),
    install_requires=[
       "pyahocorasick", "chardet", "nltk", "wordfreq", 
   ],
)
