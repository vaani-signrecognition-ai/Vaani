# Deploying Vaani to Render

This project is configured for easy deployment on **Render**.

## 1. Database Setup
1. Go to your Render Dashboard and click **New > PostgreSQL**.
2. Name it `vaanidb` and create it.
3. Once created, copy the **Internal Database URL**.

## 2. Web Service Setup
1. Click **New > Web Service**.
2. Connect your GitHub repository.
3. Use the following settings:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `gunicorn --chdir backend app:app`
4. Click **Advanced** and add these **Environment Variables**:
   - `DATABASE_URL`: (Paste the **Internal Database URL** from step 1)
   - `SECRET_KEY`: (Any random string)
   - `PYTHON_VERSION`: `3.11.9`
   - `FLASK_ENV`: `production`

## 3. Populate Dictionary
After the app is deployed, you can populate the database:
1. Go to the **Shell** tab of your Web Service in Render.
2. Run:
   ```bash
   python backend/update_db_signs.py
   ```

## Local Testing
To test the remote database from your local machine:
1. Copy the **External Database URL** from Render.
2. Paste it into your local `.env` file as `DATABASE_URL`.
3. In Render settings, add your local IP to the **Access Control** (Allow List).
4. Run:
   ```bash
   python backend/init_db.py
   ```
