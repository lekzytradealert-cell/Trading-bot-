from setuptools import setup, find_packages

setup(
    name="lekzy-trade-bot",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "python-telegram-bot==20.7",
        "requests==2.31.0",
        "pandas==2.0.2", 
        "numpy==1.24.3",
        "yfinance==0.2.18",
        "python-dotenv==1.0.0",
        "schedule==1.2.0",
        "pytz==2023.3",
        "flask==2.3.2",
        "pyTelegramBotAPI==4.19.1",
    ],
    python_requires=">=3.8",
)
