pip install virtualenv

if [ ! -d "venv" ]; then
    virtualenv venv --python=python3
fi

if [ ! -f ".env" ]; then
    cp .env.example .env
fi

source venv/bin/activate

pip install -r requirements.txt