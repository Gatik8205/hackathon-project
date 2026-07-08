## For backend
cd backend
python -m venv venv
venv/Scritps/activate
pip install -r requirements.txt
uvicorn main:app --reload

## For frontend
cd frontend
npm install
npm run dev