from setuptools import setup, find_packages

# Read the contents of your requirements.txt file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='agentless',  # Replace with your project's name if it's different
    version='0.1.0',  # Start with a version number
    author='Your Name',  # Replace with your name
    author_email='your.email@example.com',  # Replace with your email
    description='A short description of your Agentless project.',  # Add a brief description
    long_description=open('README.md').read() if open('README.md') else '', # Optional: if you have a README.md
    long_description_content_type='text/markdown',  # Optional: if long_description is markdown
    url='https://github.com/yourusername/agentless',  # Optional: Replace with your project's URL
    packages=find_packages(include=['agentless', 'agentless.*']), # Finds all packages in the 'agentless' directory
    install_requires=requirements, # Installs dependencies from requirements.txt
    classifiers=[ # Optional: Trove classifiers
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License', # Choose your license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6', # Specify a minimum Python version
)
